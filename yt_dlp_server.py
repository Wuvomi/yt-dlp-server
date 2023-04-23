import os
import sys
import argparse
import subprocess
import threading
import queue
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO

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
            urls.forEach((url) => {
                if (url.trim()) {
                    $.post('/download', { url: url.trim() });
                }
            });
            $('#url').val('');
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(index_template)

def download_video(url, socketio):
    output_directory = 'downloads'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    try:
        cmd = ['yt-dlp', '-o', f'{output_directory}/%(title)s-%(id)s.%(ext)s', url, '--newline']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        for line in process.stdout:
            socketio.emit('output', line.rstrip())
            print(line.rstrip())

        process.wait()
        socketio.emit('output', '下载完成。')

    except Exception as e:
        socketio.emit('output', f'发生错误：{e}')

download_queue = queue.Queue()

def process_download_queue():
    while True:
        url, socketio = download_queue.get()
        if url is None:
            break
        download_video(url, socketio)
        download_queue.task_done()

download_thread = threading.Thread(target=process_download_queue)
download_thread.start()

@app.route('/download', methods=['GET', 'POST'])
def download():
    url = request.values.get('url')
    if not url:
        return '需要提供网址', 400

    # 将下载任务添加到队列，而不是在此处立即下载
    download_queue.put((url, socketio))
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

    socketio.run(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
