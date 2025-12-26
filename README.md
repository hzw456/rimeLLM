# rimeLLM

简体中文拼音输入法 + AI 增强功能

## 安装步骤

### 1. 安装 Rime 输入法

**macOS:**
```bash
brew install --cask squirrel
```

**Windows:** 下载地址 https://rime.im/download/

**Linux:**
```bash
# ibus
sudo apt install ibus-rime

# fcitx5
sudo apt install fcitx5-rime
```

### 2. 复制配置文件

```bash
# macOS
cp rimeLLM.schema.yaml rimeLLM.yaml ~/Library/Rime/

# Windows
copy rimeLLM.schema.yaml rimeLLM.yaml %APPDATA%\Rime\

# Linux (ibus)
cp rimeLLM.schema.yaml rimeLLM.yaml ~/.config/ibus/rime/

# Linux (fcitx5)
cp rimeLLM.schema.yaml rimeLLM.yaml ~/.local/share/fcitx5/rime/
```

### 3. 编辑配置文件

编辑 `rimeLLM.yaml`，设置你的 API 密钥：

```yaml
rimeLLM:
  enabled: true
  provider: openai
  api_key: sk-your-api-key
  endpoint: https://api.openai.com/v1
  model: gpt-3.5-turbo
```

**支持的服务：**

- **OpenAI**: `provider: openai`, endpoint: `https://api.openai.com/v1`
- **Anthropic**: `provider: anthropic`, endpoint: `https://api.anthropic.com/v1/messages`
- **Ollama**: `provider: ollama`, endpoint: `localhost:11434`

### 4. 重新部署

右键点击 Rime 托盘图标，选择「重新部署」

### 5. 切换输入法

按 `Ctrl+Shift+数字` 或右键托盘图标，选择 `rimeLLM` 输入方案

## 使用方法

- 输入拼音 → 选词 → 上屏
- AI 自动纠错功能会在输入后自动处理

## 快捷键

| 按键 | 功能 |
|------|------|
| `Tab` | 接受第一个候选词 |
| `Escape` | 清除当前输入 |

## 卸载

删除以下文件并重新部署：

```bash
rm ~/Library/Rime/rimeLLM.schema.yaml
rm ~/Library/Rime/rimeLLM.yaml
```
