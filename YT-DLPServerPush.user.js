// ==UserScript==
// @name         YT-DLP服务器推送脚本
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  在网页上添加一个悬浮半透明按钮，用于将当前网址POST到指定服务器
// @author       Wuvomi & GPT-4
// @match        *://*/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @updateURL    https://raw.githubusercontent.com/Wuvomi/yt-dlp-server/main/YT-DLPServerPush.user.js
// ==/UserScript==

(function () {
    'use strict';

    // 获取下载服务器地址，如果不存在则设置默认值
    let serverUrl = GM_getValue('serverUrl', 'http://127.0.0.1:5000/download');

    // 创建按钮并设置样式
    const btn = document.createElement('button');
    btn.textContent = '🖕️';
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

    // 添加设置窗口
    const settingsDiv = document.createElement('div');
    settingsDiv.style.display = 'none';
    settingsDiv.style.position = 'fixed';
    settingsDiv.style.top = '50%';
    settingsDiv.style.left = '50%';
    settingsDiv.style.transform = 'translate(-50%, -50%)';
    settingsDiv.style.zIndex = '10000';
    settingsDiv.style.backgroundColor = 'white';
    settingsDiv.style.padding = '20px';
    settingsDiv.style.borderRadius = '10px';
    settingsDiv.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.5)';
    settingsDiv.innerHTML = `
        <h2>YT-DLP服务器推送脚本设置</h2>
        <label for="serverUrl">下载服务器地址：</label>
        <input type="text" id="serverUrl" value="${serverUrl}" style="width: 100%;" />
        <button id="saveSettings" style="display: block; width: 100%; margin-top: 10px;">保存设置</button>
    `;
    document.body.appendChild(settingsDiv);

    // 添加设置按钮
    const settingsBtn = document.createElement('button');
    settingsBtn.textContent = '⚙️';
    settingsBtn.style.position = 'fixed';
    settingsBtn.style.bottom = '20px';
    settingsBtn.style.right = '20px';
    settingsBtn.style.zIndex = '9999';
    settingsBtn.style.backgroundColor = 'rgba(76, 175, 80, 0.5)';
    settingsBtn.style.border = 'none';
      settingsBtn.style.color = 'white';
    settingsBtn.style.textAlign = 'center';
    settingsBtn.style.textDecoration = 'none';
    settingsBtn.style.display = 'inline-block';
    settingsBtn.style.fontSize = '24px';
    settingsBtn.style.padding = '10px 20px';
    settingsBtn.style.borderRadius = '50%';
    settingsBtn.style.opacity = '0.5';
    settingsBtn.style.transition = 'opacity 0.3s ease';
    document.body.appendChild(settingsBtn);

    // 为设置按钮添加点击事件
    settingsBtn.addEventListener('click', () => {
        settingsDiv.style.display = 'block';
    });

    // 保存设置并关闭设置窗口
    const saveSettingsBtn = document.getElementById('saveSettings');
    saveSettingsBtn.addEventListener('click', () => {
        serverUrl = document.getElementById('serverUrl').value;
        GM_setValue('serverUrl', serverUrl);
        settingsDiv.style.display = 'none';
        alert('设置已保存');
    });

    // 添加拖动功能
    let dragging = false;
    let mouseX, mouseY;
    let touchMoved = false;

    btn.addEventListener('mousedown', (e) => {
        dragging = true;
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    btn.addEventListener('touchstart', (e) => {
        dragging = true;
        touchMoved = false;
        mouseX = e.touches[0].clientX;
        mouseY = e.touches[0].clientY;
    });

    document.addEventListener('mousemove', (e) => {
        if (dragging) {
            moveButton(e.clientX, e.clientY);
        }
    });

    document.addEventListener('touchmove', (e) => {
        if (dragging) {
            touchMoved = true;
            moveButton(e.touches[0].clientX, e.touches[0].clientY);
        }
    });

    document.addEventListener('mouseup', () => {
        dragging = false;
    });

    document.addEventListener('touchend', () => {
        dragging = false;
    });

    function moveButton(newX, newY) {
        let deltaX = newX - mouseX;
        let deltaY = newY - mouseY;
        let newTop = parseInt(btn.style.top) + deltaY;
        let newRight = parseInt(btn.style.right) - deltaX;

        btn.style.top = `${newTop}px`;
        btn.style.right = `${newRight}px`;

        mouseX = newX;
        mouseY = newY;
    }

    // 为按钮添加点击事件
    btn.addEventListener('click', (e) => {
        if (e.type === 'click' && touchMoved) return;
        const currentUrl = window.location.href;
        const data = `url=${encodeURIComponent(currentUrl)}`;

        GM_xmlhttpRequest({
            method: 'POST',
            url: serverUrl,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data: data,
            onload: function (response) {
                if (response.status === 200) {
                    alert('提交成功');
                } else {
                    alert(`提交失败：${response.statusText}`);
                }
            },
            onerror: function () {
                alert('提交失败');
            },
            ontimeout: function () {
                alert('提交失败：请求超时');
            },
        });
    });

    btn.addEventListener('touchend', (e) => {
        if (!touchMoved) {
            btn.dispatchEvent(new MouseEvent('click'));
        }
    });
})();
