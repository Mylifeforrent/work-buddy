## ADDED Requirements

### Requirement: Create Jira task from requirement description
The system SHALL create Jira tasks from a requirement description, auto-populating Epic link, Sprint, Component, Labels, and Description fields based on project-specific templates.

#### Scenario: Create task with project-specific template
- **WHEN** user provides a requirement description and target project name
- **THEN** the system creates a Jira task with the correct Epic link, Sprint, Labels, and Component tags matching that project's configuration

#### Scenario: Apply description template
- **WHEN** a Jira task is created for a project
- **THEN** the Description field is populated using the project's description template with requirement details filled in

### Requirement: Support per-project Jira configuration
The system SHALL support YAML-based configuration per project defining Jira project key, default Epic, Sprint board, required labels, component tags, and description templates.

#### Scenario: Load project-specific Jira config
- **WHEN** user specifies a project name for task creation
- **THEN** the system loads the corresponding YAML config and uses its Jira settings

#### Scenario: Reject unknown project
- **WHEN** user specifies a project name that has no configuration
- **THEN** the system reports an error with available project names

### Requirement: Bulk task creation
The system SHALL support creating multiple Jira tasks from a list of requirements in a single operation.

#### Scenario: Create multiple tasks
- **WHEN** user provides multiple requirement descriptions
- **THEN** the system creates all corresponding Jira tasks and returns a summary of created ticket IDs
