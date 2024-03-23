# YT-DLP Server

YT-DLP Server 是基于 YT-DLP 的网页服务器版本，支持iOS快捷指令进行远程推送。

![icon.png](https://raw.githubusercontent.com/Wuvomi/yt-dlp-server/main/icon.png)

## 环境要求
- Python 3.6 或更高版本
- 为了方便地安装所需的依赖，请使用以下命令:
```
pip install -r requirements.txt
```

## 文件列表
- `yt_dlp_server.py`: 主程序
- `YT-DLPServerPush.user.js`: 游猴脚本
- `Dockerfile`: 用于构建和设置Docker容器的脚本
- `start.sh`: 用于在Docker环境下通过获取环境变量来启动`yt_dlp_server.py`
- `运行环境检测.bat`: 适用于Windows的运行环境检测脚本

## 功能介绍



- 支持主流网站如YouTube、91（其他网站可以自行尝试）
- 支持通过API提交下载请求
- 默认使用16个线程进行暴力下载
- 支持IPv6
- 支持下载链接日志
- 支持多任务并行下载
- 支持游猴脚本（提供Web-UI 设置服务器地址）
- 支持IPv6
- 提供Docker生成配置文件
- 在Docker宿主机上，需要确保给`start.sh`脚本赋予执行权限


## 使用说明


使用以下命令启动服务器：`python yt_dlp_server.py -l 0.0.0.0 -p 7777`

- `-l, --host` 设置监听地址（默认：0.0.0.0）
- `-p, --port` 设置监听端口（默认：7777）
- `-d, --dir` 设置下载目录路径（默认：download）
- `-6, --ipv6` 设置监听IPv6地址（默认：IPv4的0.0.0.0）


- GET 提交方式：`http://127.0.0.1:7777/download?url=https://www.example.com/video`
- POST 提交方式：`http://127.0.0.1:7777/download`

使用表单，`url=https://www.example.com/video`，`cookie=xxx`（可选，请把 JSON 抓包的头部 Cookie 写入参数，程序会自动转换为 Netscape 格式并保存至 `cookies.txt`）

docker项目地址：https://registry.hub.docker.com/r/wuvomi/yt_dlp_server/

![IMG_7061](https://user-images.githubusercontent.com/7725643/233867727-1955b068-3d30-461b-9922-5e218effb581.jpeg)

