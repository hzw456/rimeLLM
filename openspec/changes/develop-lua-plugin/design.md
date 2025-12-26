# Design: Native Rime Lua Plugin Architecture

## Overview
This document describes the architecture of the native Rime Lua plugin for AI-powered text processing.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rime Input Framework                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Schema     │  │  Engine     │  │  Composition Engine     │  │
│  │  Loader     │  │  (C++)      │  │  (C++)                  │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│         │        ┌───────┴──────┐              │                │
│         │        │  Lua Runtime │◄─────────────┘                │
│         │        │  (lua53.dll) │                               │
│         │        └──────┬───────┘                               │
│         │               │                                       │
│  ┌──────┴───────────────┴───────────────────────────────────┐   │
│  │                    rimeLLM.lua                            │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │   │
│  │  │ Config      │ │ Input       │ │ AI Client           │  │   │
│  │  │ Manager     │ │ Capturer    │ │ (HTTP)              │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │   │
│  │  ┌─────────────┐ ┌─────────────┐                          │   │
│  │  │ Suggestion  │ │ Processor   │                          │   │
│  │  │ Display     │ │ (纠错/翻译) │                          │   │
│  │  └─────────────┘ └─────────────┘                          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                    │                                              │
│                    ▼                                              │
│         ┌─────────────────────┐                                   │
│         │  External Services  │                                   │
│         │  OpenAI/Claude/     │                                   │
│         │  Ollama HTTP APIs   │                                   │
│         └─────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. Config Manager
- **File**: `config.lua`
- **Purpose**: Load and manage YAML configuration
- **Responsibilities**:
  - Read `rimeLLM.yaml` from Rime user directory
  - Provide config access with defaults
  - Hot-reload on config change

```lua
Config = {
  provider = "openai",
  api_key = "",
  endpoint = "https://api.openai.com/v1",
  model = "gpt-3.5-turbo",
  enabled = true,
  features = {
    correction = true,
    translation = false,
    expansion = false
  }
}
```

### 2. Input Capturer
- **File**: `input.lua`
- **Purpose**: Capture and buffer input context from Rime
- **Responsibilities**:
  - Hook into Rime's composition events
  - Buffer recent input history
  - Detect input mode changes

### 3. AI Client
- **File**: `ai_client.lua`
- **Purpose**: HTTP communication with AI providers
- **Responsibilities**:
  - Build API requests (OpenAI chat completions format)
  - Handle HTTP responses
  - Implement timeout and retry logic

### 4. Processor
- **File**: `processor.lua`
- **Purpose**: Process text with AI based on detected intent
- **Features**:
  - 自动纠错 (correction)
  - 翻译 (translation)
  - 扩写 (expansion)

### 5. Suggestion Display
- **File**: `display.lua`
- **Purpose**: Show AI suggestions to user
- **Modes**:
  - Inline: Show gray text after cursor
  - Candidate: Show in candidate window with number keys

## Data Flow

### Input → Suggestion Flow
```
1. User types "nihao"
2. InputCapturer captures composition
3. Buffer stores context
4. On commit: Processor analyzes text
5. AI Client sends request to API
6. Response parsed → suggestions generated
7. Display shows suggestions
8. User accepts with number key or tab
```

## Configuration Schema

```yaml
# rimeLLM.yaml
rimeLLM:
  enabled: true
  provider: openai  # openai, anthropic, ollama
  api_key: sk-xxx
  endpoint: https://api.openai.com/v1
  model: gpt-3.5-turbo
  
  features:
    correction: true
    translation: false
    expansion: false
    
  display:
    mode: candidate  # inline, candidate
    max_suggestions: 3
    
  key_bindings:
    accept: Tab
    reject: Escape
    trigger: Ctrl+Shift+A
```

## Key Hook Points

The plugin hooks into these Rime lifecycle events:

| Event | Handler | Purpose |
|-------|---------|---------|
| `key_event` | `on_key()` | Capture input |
| `composing_changed` | `on_composition()` | Track composition |
| `commit` | `on_commit()` | Process committed text |
| `select_candidate` | `on_select()` | Handle suggestion selection |

## Performance Considerations

1. **Non-blocking HTTP**: Use Lua coroutines for async requests
2. **Debouncing**: Wait 300ms after last keystroke before API call
3. **Timeout**: 2s timeout on all AI requests
4. **Caching**: Cache recent suggestions for identical inputs
5. **Size Limits**: Max 100 char input for AI processing

## Error Handling

- Network errors: Fallback to no suggestion
- API errors: Log and continue
- Timeout: Abort request, notify user
- Config errors: Use defaults, warn user

## File Structure

```
rimeLLM/
├── lua/
│   ├── rimeLLM.lua          # Main plugin entry
│   ├── config.lua           # Configuration management
│   ├── input.lua            # Input capture
│   ├── ai_client.lua        # AI API client
│   ├── processor.lua        # Text processing
│   ├── display.lua          # Suggestion display
│   └── utils.lua            # Utilities (log, json)
├── rimeLLM.schema.yaml      # Rime schema definition
└── rimeLLM.yaml             # User configuration template
```
