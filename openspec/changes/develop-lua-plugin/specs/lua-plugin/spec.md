# Lua Plugin Specification

## Purpose
Define requirements for native Rime Lua plugin that provides AI-powered text processing directly within the Rime input framework.

## ADDED Requirements

### Requirement: Plugin Initialization

The system SHALL initialize the rimeLLM plugin when Rime starts.

**Acceptance Criteria**:
- Plugin loads from `lua/rimeLLM.lua`
- Configuration loaded from `rimeLLM.yaml`
- Error handling for missing config

#### Scenario: Successful initialization
Given Rime is starting
When the rimeLLM plugin is enabled
Then it SHALL load configuration and prepare AI client

#### Scenario: Missing configuration
Given Rime is starting
When `rimeLLM.yaml` is missing
Then it SHALL use default configuration and log warning

#### Scenario: Invalid configuration
Given Rime is starting
When configuration contains invalid values
Then it SHALL use defaults and notify user

---

### Requirement: Input Context Capture

The system SHALL capture user input context from Rime's composition engine.

**Acceptance Criteria**:
- Capture composition text in real-time
- Buffer last N characters for AI processing
- Detect input mode (中文/英文/标点)

#### Scenario: Capturing composition
Given the user is typing
When characters are being composed
Then the system SHALL capture the composition text

#### Scenario: Buffering input history
Given text has been committed
When buffer limit not reached
Then the system SHALL retain history for context

#### Scenario: Mode detection
Given user switches input mode
When mode changes (中/英/数)
Then the system SHALL update mode state

---

### Requirement: AI API Communication

The system SHALL communicate with AI providers via HTTP.

**Acceptance Criteria**:
- Support OpenAI chat completions API
- Support Anthropic Claude API
- Support local Ollama API
- Request timeout < 3 seconds

#### Scenario: OpenAI request
Given a valid API key is configured
When sending text for processing
Then it SHALL format request as OpenAI chat completions

#### Scenario: Ollama local request
Given Ollama is running locally
When configured as local provider
Then it SHALL call localhost:11434

#### Scenario: Request timeout
Given an AI request is in progress
When response takes > 3 seconds
Then it SHALL abort and log timeout

---

### Requirement: Suggestion Display

The system SHALL display AI-generated suggestions to the user.

**Acceptance Criteria**:
- Support inline display (gray text after cursor)
- Support candidate window display
- Maximum 3 suggestions shown
- Response displayed within 500ms

#### Scenario: Inline suggestion display
Given AI processing is complete
When inline mode is configured
Then it SHALL show suggestion as grayed text

#### Scenario: Candidate window display
Given AI processing is complete
When candidate mode is configured
Then it SHALL show suggestions in numbered list

#### Scenario: Suggestion acceptance
Given suggestions are displayed
When user presses assigned key (Tab/数字)
Then it SHALL insert selected suggestion

---

### Requirement: Configuration Management

The system SHALL manage plugin configuration via Rime's YAML format.

**Acceptance Criteria**:
- API provider settings
- Feature toggles (纠错/翻译/扩写)
- Key binding customization
- Hot-reload support

#### Scenario: Provider configuration
Given the user edits rimeLLM.yaml
When API key and endpoint are set
Then the system SHALL connect to configured provider

#### Scenario: Feature toggling
Given the user disables "correction"
When processing text
Then the system SHALL skip correction feature

#### Scenario: Hot reload
Given the configuration file is modified
When Rime schema is reloaded
Then the system SHALL apply new settings

---

### Requirement: Text Processing Features

The system SHALL provide AI-powered text processing features.

**Acceptance Criteria**:
- 自动纠错 (Auto-correction)
- 翻译 (Translation)
- 扩写 (Expansion)

#### Scenario: Auto-correction
Given the user commits a sentence with errors
When correction is enabled
Then the system SHALL suggest corrected text

#### Scenario: Translation trigger
Given user triggers translation
When text is selected or committed
Then the system SHALL provide translated text

#### Scenario: Text expansion
Given user triggers expansion
When short text is committed
Then the system SHALL suggest longer version
