import os
import sys
import argparse
import subprocess
import threading
import queue
import logging
import time
import re
import http.cookiejar
from flask import Flask, render_template, request, render_template_string
from flask_socketio import SocketIO
from urllib.parse import urlparse

def convert_to_netscape():
    # 从文件中读取 Cookie 数据
    with open('saved_cookies.txt', 'r') as file:
        cookie_text = file.read()

    # 提取 Cookie 数据
    cookies = re.findall(r'([\w-]+)=([^;]+);', cookie_text)
    domain = re.search(r'Host: (.+)', cookie_text).group(1)

    # 将 Cookie 转换为 Netscape 格式并保存到文件
    jar = http.cookiejar.MozillaCookieJar('cookies.txt')

    for cookie_name, cookie_value in cookies:
        cookie = http.cookiejar.Cookie(
            version=0,
            name=cookie_name,
            value=cookie_value,
            port=None,
            port_specified=False,
            domain=domain,
            domain_specified=True,
            domain_initial_dot=False,
            path='/',
            path_specified=True,
            secure=True,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest={},
            rfc2109=False,
        )
        jar.set_cookie(cookie)

    jar.save(ignore_discard=True, ignore_expires=True)

def setup_logging():
    push_logger = logging.getLogger('push')
    push_logger.setLevel(logging.INFO)
    push_handler = logging.FileHandler('yt_dlp_push.log', encoding='utf-8')
    push_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    push_logger.addHandler(push_handler)

    return push_logger


if sys.version_info < (3, 6):
    print("错误：您当前使用的 Python 版本低于 3.6。")
    print("请更新到最新版本的 Python。建议使用 pyenv 进行 Python 安装和管理。")
    print("\n使用 pyenv 的一些常用命令：")
    print("查看当前已安装的所有版本：pyenv versions")
    print("安装指定的 Python 版本：pyenv install <version>")
    print("卸载指定的 Python 版本：pyenv uninstall <version>")
    print("设置全局 Python 版本：pyenv global <version>")
    sys.exit(1)

app = Flask(__name__)
socketio = SocketIO(app)
push_logger = setup_logging()

index_template = '''
<!doctype html>
<html>
<head>
    <title>YT-DLP 服务器</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.4.1/socket.io.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        textarea {
            width: 100%;
            height: 100px;
            resize: none;
        }
        pre {
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h1>YT-DLP 服务器</h1>
    <form id="download-form">
        <textarea id="url" name="url" placeholder="输入视频网址，每行一个"></textarea>
        <input type="text" id="cookie" name="cookie" placeholder="输入cookie（可选）">
        <button type="submit">下载</button>
    </form>
    <pre id="output"></pre>
    <script>
        const socket = io();

        socket.on('output', (data) => {
            $('#output').append(`${data}\\n`);
        });

        $('#download-form').submit((e) => {
            e.preventDefault();
            const urls = $('#url').val().split('\\n');
            const cookie = $('#cookie').val();
            urls.forEach((url) => {
                if (url.trim()) {
                    $.post('/download', { url: url.trim(), cookie: cookie });
                }
            });
            $('#url').val('');
            $('#cookie').val('');
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(index_template)


def download_video(url, cookie, socketio):
    try:
        output_directory = 'downloads'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        host = urlparse(url).netloc

        if cookie:
            # 保存 Cookie 到文件
            with open("saved_cookies.txt", "w") as cookie_file:
                cookie_file.write(f"Host: {host}\n")
                cookie_file.write(f"Cookie: {cookie}\n")

            # 调用 convert_to_netscape 函数
            convert_to_netscape()

            # 使用 cookies.txt 下载视频
            cmd = ['yt-dlp', '-o', f'{output_directory}/%(title)s-%(id)s.%(ext)s', url, '--newline', '--concurrent-fragments', '16', '--cookies', 'cookies.txt']
        else:
            cmd = ['yt-dlp', '-o', f'{output_directory}/%(title)s-%(id)s.%(ext)s', url, '--newline', '--concurrent-fragments', '16']

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        for line in iter(process.stdout.readline, ''):
            socketio.emit('output', line.strip())
            print(line.strip())

        process.wait()
    except Exception as e:
        print(f"下载出错：{e}")
    finally:
        if cookie:
            os.remove("saved_cookies.txt")
            os.remove("cookies.txt")
        socketio.sleep(0)
        socketio.emit("download complete", namespace="/")

download_queue = queue.Queue()

def download_thread(socketio):
    while True:
        url, cookie, socketio = download_queue.get()
        push_logger.info(f"{url}")
        download_video(url, cookie, socketio)

@app.route('/download', methods=['GET', 'POST'])
def download():
    url = request.values.get('url')
    cookie = request.values.get('cookie')
    if not url:
        return '需要提供网址', 400

    # 在将下载任务添加到队列之前记录日志
    push_logger.info(f"{url}")

    # 将下载任务添加到队列，而不是在此处立即下载
    download_queue.put((url, cookie, socketio))
    return '下载任务已添加', 200


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--host', default='0.0.0.0', help='设置监听地址（默认：0.0.0.0）')
    parser.add_argument('-p', '--port', type=int, default=5000, help='设置监听端口（默认：5000）')
    args = parser.parse_args()

    print("YT-DLP 服务器使用说明：")
    print("-l, --host 设置监听地址（默认：0.0.0.0）")
    print("-p, --port 设置监听端口（默认：5000）")
    print("示例：python yt_dlp_server.py -l 0.0.0.0 -p 5000")

    print(f"\n当前监听地址：{args.host}")
    print(f"当前监听端口：{args.port}")

    threading.Thread(target=download_thread, args=(socketio,), daemon=True).start()
    socketio.run(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
