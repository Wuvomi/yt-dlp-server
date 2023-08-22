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

args = None

app = Flask(__name__)
socketio = SocketIO(app)
push_logger = setup_logging()

index_template = '''
<!doctype html>
<html>
<head>
    <title>YT-DLP 服务器</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 0.9;
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>
    <h1>YT-DLP 服务器</h1>
    <p>当前监听地址：{{ host }}</p>
    <p>当前监听端口：{{ port }}</p>
    <p>当前下载目录：{{ download_dir }}</p>
    <p>通过 GET 方式提交下载：http://{{ request_host }}:{{ port }}/download?url=https://www.example.com/video-url</p>
</body>
</html>
'''

@app.route('/')
def index():
    request_host = request.headers.get('Host').split(':')[0]
    return render_template_string(index_template, host=args.host, request_host=request_host, port=args.port, download_dir=args.download_dir)


def download_video(url, cookie, socketio, output_directory):
    try:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        host = urlparse(url).netloc

        if cookie:
            with open("saved_cookies.txt", "w") as cookie_file:
                cookie_file.write(f"Host: {host}\n")
                cookie_file.write(f"Cookie: {cookie}\n")

            convert_to_netscape()
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

def download_thread(socketio, output_directory):
    while True:
        url, cookie, socketio = download_queue.get()
        push_logger.info(f"{url}")
        download_video(url, cookie, socketio, output_directory)

@app.route('/download', methods=['GET', 'POST'])
def download():
    url = request.values.get('url')
    cookie = request.values.get('cookie')
    if not url:
        return '需要提供网址', 400

    push_logger.info(f"{url}")
    download_queue.put((url, cookie, socketio))
    return '下载任务已添加', 200

def main():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--host', default='0.0.0.0', help='设置监听地址（默认：0.0.0.0）')
    parser.add_argument('-p', '--port', type=int, default=5000, help='设置监听端口（默认：5000）')
    parser.add_argument('-d', '--download-dir', default='downloads', help='设置下载目录（默认：downloads）')
    args = parser.parse_args()

    # Add IPv6 support
    if args.host == '0.0.0.0':
        args.host = '::'


    print("YT-DLP 服务器使用说明：")
    print("-l, --host 设置监听地址（默认：0.0.0.0）")
    print("-p, --port 设置监听端口（默认：5000）")
    print("-d, --download-dir 设置下载目录（默认：downloads）")
    print("示例：python yt_dlp_server.py -l 0.0.0.0 -p 5000 -d downloads")

    print(f"\n当前监听地址：{args.host}")
    print(f"当前监听端口：{args.port}")
    print(f"当前下载目录：{args.download_dir}")

    threading.Thread(target=download_thread, args=(socketio, args.download_dir), daemon=True).start()
    socketio.run(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
