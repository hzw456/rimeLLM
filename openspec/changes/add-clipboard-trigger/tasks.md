# Tasks: Add Clipboard Trigger Feature

## Phase 1: Clipboard Module
- [x] Create clipboard.lua module
- [x] Implement get_clipboard() function
- [x] Handle clipboard access errors gracefully
- [x] Add clipboard access permission handling

## Phase 2: Trigger Detection
- [x] Modify input.lua to detect "cb" pattern
- [x] Add trigger pattern configuration (default: "cb")
- [x] Implement debounce for trigger detection
- [x] Handle trigger cancellation

## Phase 3: AI Integration
- [x] Connect clipboard content to text processor
- [x] Implement AI optimization prompt for clipboard
- [x] Handle AI processing errors
- [x] Add processing timeout

## Phase 4: Candidate Display
- [x] Modify display.lua to show two candidates
- [x] Candidate 1: Raw clipboard text
- [x] Candidate 2: AI-optimized text
- [x] Handle candidate selection
- [x] Handle no-clipboard scenario

## Phase 5: Configuration
- [x] Add clipboard trigger config option
- [x] Add AI optimization toggle
- [x] Add max clipboard length config
- [x] Document new configuration options

## Phase 6: Testing
- [x] Test clipboard access
- [x] Test trigger detection
- [x] Test candidate display
- [x] Test AI optimization
- [x] Test error handling
