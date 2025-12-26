## MODIFIED Requirements
### Requirement: Input Length Validation for LLM Processing
The system SHALL only trigger LLM processing when the input text length is greater than 10 characters.

#### Scenario: Short input rejected
- **WHEN** user commits text with 5 characters
- **THEN** the system SHALL NOT call the LLM API
- **AND** the system SHALL log debug message indicating input is too short

#### Scenario: Threshold input accepted
- **WHEN** user commits text with exactly 10 characters
- **THEN** the system SHALL NOT call the LLM API
- **AND** the system SHALL wait for additional input

#### Scenario: Long input triggers LLM
- **WHEN** user commits text with 11 characters
- **THEN** the system SHALL call the LLM API
- **AND** the system SHALL generate candidate suggestions

#### Scenario: Very long input within limits
- **WHEN** user commits text with 50 characters (within max limit)
- **THEN** the system SHALL call the LLM API
- **AND** the system SHALL generate candidate suggestions

#### Scenario: Input exceeds maximum length
- **WHEN** user commits text with 200 characters (exceeds max of 100)
- **THEN** the system SHALL NOT call the LLM API
- **AND** the system SHALL log debug message indicating input is too long
