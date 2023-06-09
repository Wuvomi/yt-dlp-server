# YT-DLP Server 1.0版

## 环境要求
- Python 3.6 或更高版本
- Flask: `pip install Flask`
- Flask-SocketIO: `pip install Flask-SocketIO`
- eventlet: `pip install eventlet`
- requests: `pip install requests`
- yt-dlp: `pip install yt-dlp`

## 文件列表
- `YT-DLPServerPush.user.js`: 游猴推送脚本
- `yt_dlp_server.py`: 主程序
- `运行环境检测.bat`: 适用于Windows的运行环境检测脚本

## 功能介绍

### yt_dlp_server.py
- 支持命令行和 web 页面下载
- 注释和帮助信息以中文显示
- 支持使用 GET 提交网址
- 支持自定义参数（如 `-l` 和 `-p` 和 `-d`）
- 支持多行网址粘贴并同时下载
- 在正式代码开始执行前进行 Python 版本检测
- 使用 16 线程暴力下载
- 支持记录推送日志
- 支持带 Cookie 下载（YouTube 频道会员视频）

### YT-DLPServerPush.user.js
- 支持 Web-UI 设置服务器地址
- 支持长按拖动

## 使用说明

### YT-DLP 服务器命令行参数
使用以下命令启动服务器：`python yt_dlp_server.py -l 0.0.0.0 -p 5000`

- `-l, --host` 设置监听地址（默认：0.0.0.0）
- `-p, --port` 设置监听端口（默认：5000）
- `-d, --dir` 设置下载目录路径（默认：download）

### 网络请求
- GET 提交方式：`http://127.0.0.1:5000/download?url=https://www.example.com/video`
- POST 提交方式：`http://127.0.0.1:5000/download`

  使用表单，`url=https://www.example.com/video`，`cookie=xxx`（可选，请把 JSON 抓包的头部 Cookie 写入参数，程序会自动转换为 Netscape 格式并保存至 `cookies.txt`）

![IMG_7061](https://user-images.githubusercontent.com/7725643/233867727-1955b068-3d30-461b-9922-5e218effb581.jpeg)
