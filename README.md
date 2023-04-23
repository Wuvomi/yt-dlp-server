# 0.6版

注意：需要python 3.6及以上版本，所需库Flask Flask-SocketIO yt-dlp eventlet，请使用pip进行安装

- 支持命令行和web页面下载
- 注释和帮助信息以中文显示
- 支持使用get提交网址
- 支持自定义参数（如-l和-p）
- 支持多行网址粘贴并同时下载
- 在正式代码开始执行前进行python版本检测
- 默认使用16线程进行下载

## YT-DLP 服务器使用说明

`-l, --host` 设置监听地址（默认：0.0.0.0）  
`-p, --port` 设置监听端口（默认：5000）  

示例：`python yt_dlp_server.py -l 0.0.0.0 -p 5000`

支持使用快捷指令从iPhone/iPad直接推送进行下载，enjoy it!
