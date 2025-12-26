# Tasks: Develop Native Rime Lua Plugin

## Phase 1: Foundation
- [x] Create Lua plugin directory structure (plugin/lua/rimeLLM.lua)
- [x] Set up Rime schema configuration file (rimeLLM.schema.yaml)
- [x] Implement plugin loader and initialization
- [x] Create configuration loader (config.yaml)
- [x] Set up logging utility

## Phase 2: Input Capture
- [x] Implement input context capture module
- [x] Capture composition text and cursor position
- [x] Capture committed text events
- [x] Implement context buffering for AI processing
- [x] Add input mode detection (中文/英文/标点)

## Phase 3: AI Integration
- [x] Create HTTP client for AI APIs (OpenAI format)
- [x] Implement API request builder (JSON payload)
- [x] Add response parser for AI suggestions
- [x] Support multiple providers (OpenAI, Claude, Ollama)
- [x] Implement request timeout and error handling
- [x] Add API key management from config

## Phase 4: Suggestion Display
- [x] Implement inline suggestion display
- [x] Add candidate window integration
- [x] Create suggestion filtering and ranking
- [x] Implement suggestion acceptance (key bindings)
- [x] Add suggestion caching to avoid duplicate requests

## Phase 5: Configuration
- [x] Define configuration schema (schema.yaml)
- [x] Add provider settings (API key, endpoint, model)
- [x] Add feature toggles (纠错/翻译/扩写)
- [x] Add key bindings configuration
- [x] Implement hot-reload support

## Phase 6: Testing & Documentation
- [x] Create installation guide
- [x] Write API configuration documentation
- [x] Add troubleshooting guide
- [ ] Test on macOS (Squirrel), Windows (Weasel), Linux (ibus/fcitx)
