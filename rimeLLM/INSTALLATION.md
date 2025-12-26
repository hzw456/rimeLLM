# rimeLLM Lua Plugin Installation Guide

## Quick Start

### 1. Install Rime Input Method

**macOS:**
```bash
brew install --cask squirrel
```

**Windows:**
Download from https://rime.im/download/

**Linux:**
```bash
# ibus
sudo apt install ibus-rime

# fcitx5
sudo apt install fcitx5-rime
```

### 2. Copy Lua Plugin Files

1. Copy the `rimeLLM/` folder to your Rime user data directory:

**macOS:**
```bash
cp -r rimeLLM/ ~/Library/Rime/
```

**Windows:**
```cmd
xcopy rimeLLM\ %APPDATA%\Rime\ /E /I
```

**Linux (ibus):**
```bash
cp -r rimeLLM/ ~/.config/ibus/rime/
```

**Linux (fcitx5):**
```bash
cp -r rimeLLM/ ~/.local/share/fcitx5/rime/
```

2. Copy the configuration template:
```bash
cp rimeLLM/rimeLLM.yaml ~/Library/Rime/
```

### 3. Configure API Settings

Edit `rimeLLM.yaml` in your Rime directory and set your API credentials:

**OpenAI:**
```yaml
rimeLLM:
  provider: openai
  api_key: sk-your-api-key
  endpoint: https://api.openai.com/v1
  model: gpt-3.5-turbo
```

**Anthropic Claude:**
```yaml
rimeLLM:
  provider: anthropic
  api_key: your-anthropic-key
  endpoint: https://api.anthropic.com/v1/messages
  model: claude-sonnet-4-20250514
```

**Ollama (Local):**
```yaml
rimeLLM:
  provider: ollama
  api_key: ""
  endpoint: localhost:11434
  model: llama3
```

### 4. Deploy Rime

1. Right-click the Rime status icon
2. Select "Deploy" or "重新部署"

### 5. Test

Start typing in any application using Rime. The plugin will:
- Automatically correct spelling errors (if correction enabled)
- Suggest translations (if translation enabled)
- Expand short text (if expansion enabled)

## Key Bindings

| Key | Action |
|-----|--------|
| `Tab` | Accept AI suggestion |
| `Escape` | Reject suggestion |
| `Ctrl+Shift+a` | Manually trigger AI |

## Troubleshooting

### No suggestions appearing

1. Check if plugin is enabled in `rimeLLM.yaml`:
```yaml
rimeLLM:
  enabled: true
```

2. Verify API key is set correctly

3. Check Rime logs:
```bash
# macOS
log show --predicate 'eventMessage CONTAINS "rimeLLM"' --last 5m
```

4. Enable debug logging:
```yaml
rimeLLM:
  logging:
    level: DEBUG
    enabled: true
```

### Plugin not loading

1. Ensure Lua files are in correct location:
```bash
# Should exist:
~/Library/Rime/rimeLLM/lua/rimeLLM.lua
~/Library/Rime/rimeLLM/rimeLLM.yaml
```

2. Check Rime logs for errors

3. Restart Rime completely

### Connection errors

1. Verify API endpoint is accessible:
```bash
curl https://api.openai.com/v1/models
```

2. Check firewall settings

3. For Ollama, ensure local server is running:
```bash
ollama serve
```

## Configuration Options

```yaml
rimeLLM:
  enabled: true                  # Enable/disable plugin
  provider: openai               # openai, anthropic, ollama
  api_key: your-api-key
  endpoint: https://api.example.com/v1
  model: gpt-3.5-turbo
  
  features:
    correction: true             # Auto-correct text
    translation: false           # Enable translation
    expansion: false             # Expand short text
  
  display:
    mode: candidate              # inline or candidate
    max_suggestions: 3
  
  key_bindings:
    accept: Tab
    reject: Escape
    trigger: Ctrl+Shift+a
  
  performance:
    debounce_ms: 300             # Wait before AI request
    timeout_ms: 2000             # API timeout
    cache_enabled: true
    max_input_chars: 100
```

## Support

- GitHub: https://github.com/hzw456/rimeLLM
- Issues: Report bugs and feature requests on GitHub
