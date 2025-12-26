# AI 剪切板配置教程

## 目录

1. [安装依赖](#安装依赖)
2. [配置 AI 提供商](#配置-ai-提供商)
3. [启动服务](#启动服务)
4. [使用托盘菜单](#使用托盘菜单)
5. [配置说明](#配置说明)

---

## 安装依赖

### Python 依赖

```bash
pip install -r backend/requirements.txt
```

主要依赖：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `httpx` - HTTP 客户端
- `pydantic` - 数据验证

### Node.js 依赖

```bash
cd client
npm install
```

---

## 配置 AI 提供商

### OpenAI 配置

1. 获取 API Key: https://platform.openai.com/api-keys
2. 在设置界面中配置：

```json
{
  "type": "openai",
  "apiKey": "sk-your-api-key",
  "endpoint": "https://api.openai.com/v1",
  "model": "gpt-3.5-turbo"
}
```

推荐模型：
- `gpt-3.5-turbo` - 性价比高
- `gpt-4` - 更强能力
- `gpt-4-turbo` - 快速响应

### Anthropic Claude 配置

1. 获取 API Key: https://console.anthropic.com/
2. 在设置界面中配置：

```json
{
  "type": "anthropic",
  "apiKey": "your-anthropic-api-key",
  "endpoint": "https://api.anthropic.com/v1/messages",
  "model": "claude-sonnet-4-20250514"
}
```

推荐模型：
- `claude-haiku-4-20250514` - 快速
- `claude-sonnet-4-20250514` - 平衡
- `claude-opus-4-20250514` - 最强能力

### 本地模型配置 (Ollama)

1. 安装 Ollama: https://ollama.com/
2. 启动本地服务：

```bash
ollama serve
```

3. 下载模型：

```bash
ollama pull llama3
ollama pull qwen
ollama pull deepseek-r1
```

4. 在设置界面中配置：

```json
{
  "type": "local",
  "apiKey": "不需要",
  "endpoint": "http://localhost:11434/v1",
  "model": "llama3"
}
```

---

## 启动服务

### 方式一：同时启动前后端

```bash
npm run dev
```

这会同时启动：
- 后端服务: http://localhost:8000
- 前端服务: http://localhost:5173

### 方式二：分别启动

**启动后端：**
```bash
npm run dev:backend
```

**启动前端：**
```bash
npm run dev:frontend
```

### 方式三：启动桌面应用

```bash
npm start
```

---

## 使用托盘菜单

启动应用后，托盘图标会出现在菜单栏：

### 菜单选项

| 选项 | 功能 |
|------|------|
| 打开设置 | 打开配置界面 |
| 文本纠错 | 纠正剪贴板文本 |
| 中→英 | 将剪贴板文本翻译为英文 |
| 英→中 | 将剪贴板文本翻译为中文 |
| 检查更新 | 检查新版本 |
| 帮助文档 | 打开帮助页面 |
| 退出 | 退出应用 |

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Cmd+Shift+C` | 打开设置 |
| `Cmd+Shift+V` | 纠错并复制 |
| `Cmd+Shift+T` | 翻译并复制 |

---

## 配置说明

### 配置文件位置

配置文件存储在：
```bash
~/.config/ai-clipboard/config.json
```

### 完整配置示例

```json
{
  "providers": [
    {
      "type": "openai",
      "apiKey": "sk-xxx",
      "endpoint": "https://api.openai.com/v1",
      "model": "gpt-3.5-turbo",
      "temperature": 0.7,
      "maxTokens": 1000
    }
  ],
  "default_provider": "openai",
  "features": {
    "auto_correct": true,
    "auto_translate": false,
    "auto_expand": false
  },
  "shortcuts": {
    "correct": "Cmd+Shift+V",
    "translate": "Cmd+Shift+T"
  },
  "rules": [
    {
      "pattern": "URGENT",
      "replacement": "紧急",
      "enabled": true
    }
  ]
}
```

### 环境变量

也可以通过环境变量配置：

```bash
export OPENAI_API_KEY="sk-xxx"
export ANTHROPIC_API_KEY="xxx"
export DEFAULT_MODEL="gpt-4"
```

---

## 故障排除

### 后端无法启动

```bash
# 检查端口是否被占用
lsof -i :8000

# 查看详细错误
npm run dev:backend
```

### 无法连接 AI 服务

```bash
# 测试 API Key
curl -H "Authorization: Bearer sk-xxx" \
  https://api.openai.com/v1/models
```

### 托盘图标不显示

- 重启应用
- 检查系统权限
- 重新安装应用

---

## 常见问题

### Q: 支持哪些输入方式？

A: 目前支持：
- 托盘菜单操作
- 剪贴板监听
- Rime 输入法集成（开发中）

### Q: 消耗多少 API 配额？

A: 典型操作消耗：
- 文本纠错: ~50 tokens
- 翻译: ~100 tokens
- 扩写: ~200-500 tokens

### Q: 如何回退到旧版本？

```bash
git checkout v0.0.1
```

### Q: 如何贡献代码？

1. Fork 仓库
2. 创建特性分支
3. 提交改动
4. 发起 Pull Request

---

## 相关链接

- 项目主页: https://github.com/rime-ai-clipboard
- 问题反馈: https://github.com/rime-ai-clipboard/issues
- 帮助文档: https://github.com/rime-ai-clipboard/wiki

