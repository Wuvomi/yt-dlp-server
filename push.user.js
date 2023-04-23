// ==UserScript==
// @name         yt-dlp-push
// @namespace    http://tampermonkey.net/
// @version      0.5
// @description  在网页上添加一个悬浮半透明按钮，用于将当前网址POST到指定服务器
// @author       Your Name
// @match        *://*/*
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function () {
    'use strict';

    // 创建按钮并设置样式
    const btn = document.createElement('button');
    btn.textContent = '⇡';
    btn.style.position = 'fixed';
    btn.style.top = '20px';
    btn.style.right = '20px';
    btn.style.zIndex = '9999';
    btn.style.backgroundColor = 'rgba(76, 175, 80, 0.5)';
    btn.style.border = 'none';
    btn.style.color = 'white';
    btn.style.textAlign = 'center';
    btn.style.textDecoration = 'none';
    btn.style.display = 'inline-block';
    btn.style.fontSize = '24px';
    btn.style.padding = '10px 20px';
    btn.style.borderRadius = '50%';
    btn.style.opacity = '0.5';
    btn.style.transition = 'opacity 0.3s ease';

    // 将按钮添加到页面中
    document.body.appendChild(btn);

    // 为按钮添加鼠标悬停事件，使其在悬停时不透明
    btn.addEventListener('mouseover', () => {
        btn.style.opacity = '1';
    });

    // 为按钮添加鼠标离开事件，使其在离开时半透明
    btn.addEventListener('mouseout', () => {
        btn.style.opacity = '0.5';
    });

    // 为按钮添加点击事件
    btn.addEventListener('click', () => {
        const currentUrl = window.location.href;
        const serverUrl = 'http://127.0.0.1:5000/download';
        const data = `url=${encodeURIComponent(currentUrl)}`;

        // 使用GM_xmlhttpRequest发送请求
        GM_xmlhttpRequest({
            method: 'POST',
            url: serverUrl,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data: data,
            onload: function (response) {
                if (response.status === 200) {
                    alert('提交成功！');
                } else {
                    alert(`提交失败：${response.status}\n${response.responseText}`);
                }
            },
            onerror: function (error) {
                alert(`提交失败：${error.message}`);
            },
        });
    });
})();
