# Change: Refactor LLM trigger threshold and consolidate Lua scripts

## Why
The current implementation triggers LLM calls for very short inputs (2-3 characters), which is inefficient and wasteful of API resources. Additionally, duplicate code exists across Lua scripts that should be consolidated for maintainability.

## What Changes
- Change minimum character threshold from 2-3 to > 10 characters before LLM is called
- Consolidate duplicate JSON utility functions into `utils.lua`
- Remove redundant length checks by centralizing the threshold logic

## Impact
- Affected specs: `input-processing`
- Affected code:
  - `lua/input.lua:224` - `min_chars` variable
  - `lua/processor.lua:80` - `min_length` variable
  - `lua/ai_client.lua:269-445` - JSON encode/decode functions
  - `lua/utils.lua` - Will receive new functions
