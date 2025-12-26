## 1. Update threshold in input.lua
- [x] 1.1 Change `min_chars` from 3 to 10 in `should_trigger_ai` function
- [x] 1.2 Update the reason message to reflect new threshold

## 2. Update threshold in processor.lua
- [x] 2.1 Change `min_length` from 2 to 10 in `_should_process` function
- [x] 2.2 Remove redundant check since input.lua already validates length

## 3. Consolidate JSON utilities
- [x] 3.1 Extract `_json_encode` and `_json_decode` from `ai_client.lua`
- [x] 3.2 Add functions to `utils.lua` with public names
- [x] 3.3 Update `ai_client.lua` to use consolidated functions

## 4. Validate changes
- [x] 4.1 Run openspec validate
- [x] 4.2 Verify no regressions in functionality
