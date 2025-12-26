# Proposal: Develop Native Rime Lua Plugin

## Summary
Develop a native Rime Lua plugin (librime/lua) to replace the current Python/Electron architecture, enabling direct integration with Rime input method without external service dependencies.

## Problem Statement
The current implementation uses a Python FastAPI backend + Electron client architecture which requires:
- Running a separate HTTP/WebSocket server
- Complex inter-process communication
- Multiple dependency installations
- Configuration overhead

This approach is fragile and difficult for users to set up. The Lua plugin approach will:
- Run directly within Rime's process
- Zero external dependencies (besides Rime)
- Instant startup with Rime
- Native performance

## Proposed Solution
Develop a native Rime Lua plugin that:
1. Captures input context directly from Rime's composition engine
2. Communicates with AI APIs (OpenAI, Claude, Ollama) via HTTP
3. Displays AI suggestions inline or in candidate window
4. Stores configuration in Rime's YAML config format

## Scope
- Create Lua plugin for librime (works on macOS/Windows/Linux Rime)
- Implement AI API client in Lua
- Add configuration via Rime schema customization
- Support inline suggestions and candidate window display

## Out of Scope
- Electron/UI client (replaced by native Rime integration)
- Python backend (replaced by Lua code)
- WebSocket communication (replaced by direct Lua HTTP calls)

## Dependencies
- Rime 输入法 (Squirrel/Mac, Weasel/Windows, ibus-fcitx-rime/Linux)
- Lua 5.4+ (bundled with librime)
- AI API access (OpenAI/Anthropic/Ollama)

## Risks
- librime Lua API stability across versions
- Network requests may block input (need async/非阻塞处理)
- Large AI responses may cause input lag

## Timeline
Target: 2-3 weeks for MVP
