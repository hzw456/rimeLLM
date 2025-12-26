# Clipboard Trigger Specification

## Purpose
Define requirements for clipboard trigger feature that displays latest clipboard content and AI-optimized version when user types "cb".

## ADDED Requirements

### Requirement: Clipboard Access

The system SHALL fetch the latest clipboard content when requested.

**Acceptance Criteria**:
- Return clipboard text as string
- Handle empty clipboard gracefully
- Return nil on access failure
- Max content length: configurable

#### Scenario: Successful clipboard access
Given clipboard contains "Hello world"
When rimeLLM requests clipboard
Then it SHALL return "Hello world"

#### Scenario: Empty clipboard
Given clipboard is empty
When rimeLLM requests clipboard
Then it SHALL return nil or empty string

#### Scenario: Clipboard access denied
Given clipboard access fails
When rimeLLM requests clipboard
Then it SHALL return nil and log warning

---

### Requirement: Trigger Pattern Detection

The system SHALL detect the "cb" trigger pattern during composition.

**Acceptance Criteria**:
- Detect "cb" sequence in preedit text
- Trigger on second character input
- Cancel trigger if user continues typing other characters
- Configurable trigger pattern

#### Scenario: Trigger activation
Given user types "c" then "b"
When "b" is committed
Then the system SHALL activate clipboard trigger

#### Scenario: Trigger cancellation
Given "cb" was typed
When user types another character (e.g., "x")
Then the trigger SHALL be cancelled

#### Scenario: Custom trigger pattern
Given trigger pattern is configured as "clip"
When user types "clip"
Then the system SHALL activate clipboard trigger

---

### Requirement: Dual Candidate Display

The system SHALL display two candidates when trigger is activated.

**Acceptance Criteria**:
- Candidate 1: Raw clipboard text
- Candidate 2: AI-optimized clipboard text
- Maximum 2 candidates shown
- Raw text is always first

#### Scenario: Display two candidates
Given clipboard contains "hello"
And AI optimization is enabled
When trigger is activated
Then show candidate 1: "hello"
And show candidate 2: "Hello (optimized)"

#### Scenario: AI optimization disabled
Given clipboard contains "hello"
And AI optimization is disabled
When trigger is activated
Then show only candidate 1: "hello"

#### Scenario: Empty clipboard
Given clipboard is empty
When trigger is activated
Then show no candidates

---

### Requirement: AI Optimization

The system SHALL generate AI-optimized version of clipboard content.

**Acceptance Criteria**:
- Optimize based on clipboard content type
- Processing timeout: 2 seconds
- Fallback to raw text on error
- Configurable optimization type

#### Scenario: AI optimization success
Given clipboard contains raw text
When AI processing completes
Then return optimized text

#### Scenario: AI processing timeout
Given AI request takes > 2 seconds
When timeout occurs
Then fallback to raw clipboard text

#### Scenario: AI API error
Given AI API returns error
When processing clipboard
Then fallback to raw clipboard text

---

### Requirement: Candidate Selection

The system SHALL insert selected candidate into input.

**Acceptance Criteria**:
- Number keys select candidates
- Tab key selects first candidate
- Candidate inserted at cursor position

#### Scenario: Select first candidate
Given two candidates are displayed
When user presses "1"
Then raw clipboard text SHALL be inserted

#### Scenario: Select second candidate
Given two candidates are displayed
When user presses "2"
Then AI-optimized text SHALL be inserted

#### Scenario: Tab to accept
Given two candidates are displayed
When user presses Tab
Then first candidate SHALL be inserted

