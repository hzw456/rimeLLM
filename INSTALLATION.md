# AI 剪切板 - macOS 安装指南

## 目录

- [简介](#简介)
- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置 AI 提供商](#配置-ai-提供商)
- [Rime 输入法集成](#rime-输入法集成)
- [使用方法](#使用方法)
- [常见问题](#常见问题)
- [卸载](#卸载)

---

## 简介

AI 剪切板是一款创新的输入增强工具，通过深度集成 Rime 输入法框架和 AI 大模型能力，为用户提供智能化的文本处理体验。

**核心功能：**
- ✨ 智能文本纠错
- 📝 文本扩写
- 🌐 多语言翻译
- 🎯 场景感知优化
- ⚡ Rime 无缝集成

---

## 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | macOS 11.0 (Big Sur) 或更高版本 |
| 处理器 | Intel 或 Apple Silicon |
| 内存 | 至少 4GB RAM |
| 存储 | 至少 100MB 可用空间 |
| 其他 | Rime 输入法（可选，用于完整集成） |

---

## 安装步骤

### 方法一：源码安装（推荐）

#### 1. 安装 Homebrew（如果尚未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. 安装 Python 3.10+

```bash
# 使用 Homebrew 安装
brew install python@3.11

# 验证安装
python3.11 --version
```

#### 3. 安装 Node.js（用于 Electron 客户端）

```bash
# 使用 Homebrew 安装
brew install node

# 验证安装
node --version
```

#### 4. 克隆并安装项目

```bash
# 克隆项目
git clone https://github.com/rime-ai-clipboard/rimeLLM.git
cd rimeLLM

# 安装后端依赖
cd backend
pip install -r requirements.txt
cd ..

# 安装前端依赖
cd client
npm install
cd ..
```

#### 5. 启动服务

```bash
# 终端 1 - 启动后端服务
cd backend
python main.py

# 终端 2 - 启动 Electron 客户端
cd client
npm run dev
```

### 方法二：使用安装脚本

```bash
# 下载安装脚本
curl -O https://raw.githubusercontent.com/rime-ai-clipboard/rimeLLM/main/install.sh

# 运行安装脚本
chmod +x install.sh
./install.sh
```

### 方法三：手动打包安装

```bash
# 1. 安装依赖
brew install python@3.11 node

# 2. 安装 Python 包
pip3 install fastapi uvicorn httpx pydantic

# 3. 安装 Node 包
npm install electron-builder -g

# 4. 打包应用
cd /path/to/rimeLLM
npm run package

# 打包后的应用在 dist/ 目录
```

---

## 配置 AI 提供商

### OpenAI 配置

1. 打开 AI 剪切板应用
2. 进入「AI 提供商」设置
3. 选择「OpenAI (GPT-4)」
4. 输入你的 API Key
5. 选择模型（推荐 gpt-4 或 gpt-3.5-turbo）
6. 点击「测试」验证连接

```bash
# 环境变量方式
export OPENAI_API_KEY="sk-your-api-key"
```

### Anthropic Claude 配置

1. 进入「AI 提供商」设置
2. 选择「Anthropic (Claude)」
3. 输入 Claude API Key
4. 选择模型（推荐 claude-sonnet-4）
5. 点击「测试」验证连接

```bash
# 环境变量方式
export ANTHROPIC_API_KEY="your-claude-api-key"
```

### 本地模型配置（Ollama）

```bash
# 安装 Ollama
brew install ollama

# 启动 Ollama 服务
ollama serve

# 下载模型
ollama pull llama3
ollama pull qwen
```

在应用中选择「本地模型」并设置地址为 `http://localhost:11434`

---

## Rime 输入法集成

### 1. 安装 Rime 输入法

**方式一：使用 Homebrew**

```bash
brew install --cask squirrel
```

**方式二：手动下载**

1. 访问 [Rime 官网](https://rime.im/download/)
2. 下载「鼠须管」(Squirrel) for macOS
3. 安装 dmg 文件

### 2. 配置 Rime

#### 启用 AI 剪切板插件

编辑 Rime 配置文件：

```bash
# 打开配置文件
mkdir -p ~/.rime
nano ~/.rime/custom.yaml
```

添加以下配置：

```yaml
# ~/.rime/custom.yaml
patch:
  schema_list:
    - schema: luna_pinyin
    - schema: terra_pinyin
    - schema: stroke
  
  # AI 剪切板集成配置
  ai_clipboard:
    enabled: true
    api_server: "http://localhost:8000"
    suggestion_mode: "inline"  # inline | candidate | clipboard
    
  # 候选词窗口设置
  menu:
    page_size: 5
    shadow_radius: 8
    
  # 样式设置
  style:
    color_scheme: github_light
    font_face: "PingFang SC"
    font_point: 16
```

#### 重新部署 Rime

在菜单栏点击「ㄓ」图标，选择「重新部署」

### 3. 验证集成

1. 打开任意文本编辑器
2. 切换到 Rime 输入法
3. 输入文本，检查是否显示 AI 建议

---

## 使用方法

### 桌面客户端

1. **启动应用**
   ```bash
   # 从源码启动
   cd rimeLLM
   npm run dev
   ```

2. **图标位置**
   - 菜单栏显示应用图标
   - 点击图标打开设置窗口

3. **快捷操作**
   - 点击菜单栏图标
   - 选择「文本纠错」「翻译」等功能
   - 结果自动复制到剪贴板

### 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `⌥ + T` | 唤起翻译面板 |
| `⌥ + C` | 快速纠错 |
| `⌥ + E` | 智能扩写 |
| `⌥ + S` | 显示状态 |

### 输入法内使用

1. 在任何文本输入框中使用 Rime 输入法
2. 输入过程中自动显示 AI 建议
3. 使用 `Tab` 键接受建议
4. 使用数字键选择候选词

---

## 常见问题

### Q1: 后端服务无法启动？

```bash
# 检查端口占用
lsof -i :8000

# 杀死占用端口的进程
kill -9 <PID>

# 重新启动
cd backend && python main.py
```

### Q2: API Key 无效？

- 检查 API Key 是否正确复制（注意前后的空格）
- 确认 API Key 有足够的配额
- 验证网络连接

### Q3: Rime 集成不工作？

```bash
# 1. 检查 Rime 是否运行
ps aux | grep squirrel

# 2. 检查配置文件
cat ~/.rime/custom.yaml

# 3. 重新部署
killall Squirrel
# 重新启动 Squirrel
```

### Q4: Electron 应用无法启动？

```bash
# 清除缓存
rm -rf node_modules/.cache
npm install
npm run dev
```

### Q5: Apple Silicon (M1/M2) 兼容性问题？

```bash
# 使用 Rosetta 模式运行
arch -x86_64 npm run dev

# 或确保安装原生依赖
brew install --build-from-source <package>
```

---

## 卸载

### 1. 停止服务

```bash
# 停止后端服务
pkill -f "python main.py"

# 退出应用
pkill -f "electron"
```

### 2. 删除文件

```bash
# 删除应用文件
rm -rf ~/Applications/AI\ 剪切板.app
rm -rf /path/to/rimeLLM

# 删除配置
rm -rf ~/.config/ai-clipboard

# 删除 Rime 配置（可选）
rm -rf ~/.rime/custom.yaml
```

### 3. 清理依赖

```bash
# 使用 Homebrew 安装的依赖（谨慎使用）
brew uninstall python@3.11 node
brew cleanup
```

---

## 技术支持

- **GitHub Issues**: https://github.com/rime-ai-clipboard/rimeLLM/issues
- **文档**: https://github.com/rime-ai-clipboard/rimeLLM/wiki
- **更新日志**: [CHANGELOG.md](./CHANGELOG.md)

---

## 更新日志

### v0.1.0 (2024-12-25)

- ✨ 初始版本发布
- ⚡ 支持 OpenAI GPT-4/3.5
- ⚡ 支持 Anthropic Claude
- ⚡ 支持本地模型 (Ollama)
- ⌨️ Rime 输入法集成
- 📦 Electron 桌面客户端

---

**Copyright © 2024 AI 剪切板**
