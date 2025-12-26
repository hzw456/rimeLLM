const { app, BrowserWindow, Menu, Tray, ipcMain, shell } = require('electron');
const path = require('path');
const http = require('http');

let tray = null;
let settingsWindow = null;
const API_BASE = 'http://localhost:8000';

app.whenReady().then(() => {
  createTray();
  createSettingsWindow();
  checkBackendConnection();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createSettingsWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'iconTemplate.png');
  
  tray = new Tray(iconPath);
  tray.setToolTip('AI 剪切板');
  tray.setContextMenu(Menu.buildFromTemplate([
    {
      label: '打开设置',
      click: () => createSettingsWindow()
    },
    { type: 'separator' },
    {
      label: '文本纠错',
      click: () => sendToClipboard('测试文本')
    },
    {
      label: '翻译',
      submenu: [
        { label: '中→英', click: () => translateText('测试', 'zh-en') },
        { label: '英→中', click: () => translateText('test', 'en-zh') }
      ]
    },
    { type: 'separator' },
    {
      label: '检查更新',
      click: () => checkForUpdates()
    },
    {
      label: '帮助文档',
      click: () => openHelp()
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => app.quit()
    }
  ]));
}

function createSettingsWindow() {
  if (settingsWindow) {
    settingsWindow.show();
    return;
  }
  
  settingsWindow = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    title: 'AI 剪切板 - 设置',
    resizable: true,
    minimizable: true
  });
  
  settingsWindow.loadFile(path.join(__dirname, 'index.html'));
  
  settingsWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      settingsWindow.hide();
    }
  });
}

function checkBackendConnection() {
  const checkInterval = setInterval(() => {
    http.get(`${API_BASE}/health`, (res) => {
      if (res.statusCode === 200) {
        clearInterval(checkInterval);
        console.log('Backend connected');
      }
    }).on('error', () => {
      console.log('Backend not available, starting...');
    });
  }, 5000);
}

function sendToClipboard(text) {
  const { clipboard } = require('electron');
  clipboard.writeText(text);
  showNotification('已复制到剪贴板', text.substring(0, 50));
}

async function translateText(text, direction) {
  try {
    const response = await fetch(`${API_BASE}/api/v1/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, direction })
    });
    const data = await response.json();
    sendToClipboard(data.result);
  } catch (error) {
    showNotification('翻译失败', error.message);
  }
}

function checkForUpdates() {
  shell.openExternal('https://github.com/rime-ai-clipboard/releases');
}

function openHelp() {
  shell.openExternal('https://github.com/rime-ai-clipboard/wiki');
}

function showNotification(title, body) {
  const { Notification } = require('electron');
  if (Notification.isSupported()) {
    new Notification({ title, body }).show();
  }
}

ipcMain.handle('get-config', async () => {
  try {
    const response = await fetch(`${API_BASE}/api/v1/config`);
    return await response.json();
  } catch {
    return { providers: [], default_provider: '' };
  }
});

ipcMain.handle('save-config', async (event, config) => {
  try {
    await fetch(`${API_BASE}/api/v1/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('test-provider', async (event, provider) => {
  try {
    const response = await fetch(`${API_BASE}/api/v1/providers/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(provider)
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});
