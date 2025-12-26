# Proposal: Add Clipboard Trigger Feature

## Summary
Add clipboard integration to the rimeLLM Lua plugin that triggers when user types "cb", displaying the latest clipboard content and its AI-optimized version as candidate suggestions.

## Problem Statement
Currently, the rimeLLM plugin processes committed text but doesn't provide quick access to clipboard content. Users need a fast way to:
- Access recently copied text directly through Rime
- See AI-optimized versions of clipboard content

## Proposed Solution
When the user types "cb" in Rime:
1. Detect the "cb" trigger pattern
2. Fetch the latest clipboard content
3. Display two candidates:
   - Candidate 1: Raw clipboard text
   - Candidate 2: AI-optimized clipboard text

## Scope
- Add clipboard capture module
- Detect "cb" trigger pattern in composition
- Fetch latest clipboard content
- Integrate with existing AI processor
- Show two candidates in Rime candidate window

## Out of Scope
- Clipboard history management (single latest entry only)
- Multiple clipboard entries selection
- Clipboard sync across devices

## Dependencies
- Existing rimeLLM Lua plugin
- Rime candidate window API
- System clipboard access (via librime API)

## Timeline
Target: 1 week for MVP
