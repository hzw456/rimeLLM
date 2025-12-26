# AI 剪切板 (rimeLLM)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: macOS](https://img.shields.io/badge/Platform-mOS-black.svg)]()

一款创新的输入增强工具，通过深度集成 Rime 输入法框架和 AI 大模型能力，为用户提供智能化的文本处理体验。

## 功能特性

- ✨ **智能纠错** - 自动检测并修复拼写和语法错误
- 📝 **文本扩写** - 根据上下文智能扩展文本内容
- 🌐 **多语言翻译** - 支持中英文等多语言互译
- 🎯 **场景感知** - 自动理解输入场景并提供优化建议
- ⚡ **Rime 集成** - 与 Rime 输入法深度集成

## 快速开始

### 1. 安装依赖

```bash
# Python 依赖
pip3 install fastapi uvicorn httpx pydantic

# Node.js 依赖 (可选，用于 Electron 客户端)
cd client && npm install
```

### 2. 启动服务

```bash
# 启动后端 API 服务
cd backend
python3 main.py

# 启动 Electron 客户端 (新终端)
cd client && npm run dev
```

### 3. 访问 API

```bash
# 健康检查
curl http://localhost:8000/health

# 获取配置
curl http://localhost:8000/api/v1/config
```

## 项目结构

```
rimeLLM/
├── backend/           # FastAPI 后端服务
│   ├── main.py       # 主服务入口
│   └── requirements.txt
├── client/           # Electron 客户端
│   ├── src/         # 源码
│   └── public/      # 静态资源
├── electron/        # Electron 主进程
│   ├── main.js      # 主进程入口
│   ├── preload.js   # 预加载脚本
│   └── index.html   # 设置界面
├── openspec/        # OpenSpec 规范文档
├── INSTALLATION.md  # 安装指南
└── README.md
```

## API 文档

### 健康检查

```http
GET /health
```

响应:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### 配置管理

```http
GET /api/v1/config
POST /api/v1/config
```

### AI 提供商测试

```http
POST /api/v1/providers/test
Content-Type: application/json

{
  "type": "openai",
  "apiKey": "sk-...",
  "endpoint": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

### 文本纠错

```http
POST /api/v1/correct
Content-Type: application/json

{
  "text": "I goes to school"
}
```

### 翻译

```http
POST /api/v1/translate
Content-Type: application/json

{
  "text": "人工智能正在改变世界",
  "direction": "zh-en"
}
```

### 文本扩写

```http
POST /api/v1/expand
Content-Type: application/json

{
  "text": "项目使用了 React",
  "ratio": 2.0
}
```

## 配置 AI 提供商

### OpenAI

```python
# 在设置中配置
provider = {
    "type": "openai",
    "apiKey": "sk-your-api-key",
    "model": "gpt-4"  # 或 gpt-3.5-turbo
}
```

### Anthropic Claude

```python
provider = {
    "type": "anthropic",
    "apiKey": "your-claude-api-key",
    "model": "claude-sonnet-4-20250514"
}
```

### 本地模型 (Ollama)

```bash
# 安装 Ollama
brew install ollama
ollama serve
ollama pull llama3
```

```python
provider = {
    "type": "local",
    "endpoint": "http://localhost:11434/v1",
    "model": "llama3"
}
```

## Rime 集成

### 安装 Rime

```bash
# macOS
brew install --cask squirrel
```

### 配置集成

编辑 `~/.rime/custom.yaml`:

```yaml
patch:
  ai_clipboard:
    enabled: true
    api_server: "http://localhost:8000"
    suggestion_mode: "inline"
```

## 开发

### 运行测试

```bash
# 启动后端
cd backend && python3 main.py

# 测试 API
curl http://localhost:8000/health
```

### 构建客户端

```bash
# Electron 打包
npm run build
npm run package
```

## 贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- [Rime 输入法](https://rime.im/) - 优秀的输入框架
- [OpenAI](https://openai.com/) - AI 能力支持
- [Anthropic](https://www.anthropic.com/) - Claude 模型支持
