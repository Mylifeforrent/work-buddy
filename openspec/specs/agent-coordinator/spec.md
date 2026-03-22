## ADDED Requirements

### Requirement: Route user requests to appropriate agents
The system SHALL accept user requests via CLI and route them to the appropriate specialized agent based on the request type.

#### Scenario: Route Jira task creation request
- **WHEN** user says "Create Jira tasks for requirement X in Project Alpha"
- **THEN** the coordinator routes the request to the Jira Task Agent with the parsed project name and requirement details

#### Scenario: Route test execution request
- **WHEN** user says "Run regression tests for Project Beta"
- **THEN** the coordinator routes the request to the Browser Test Agent with the target project name

#### Scenario: Route multi-agent workflow
- **WHEN** user says "Prepare release for PROJ-1234"
- **THEN** the coordinator orchestrates a multi-agent workflow: ICE Compliance check → Release Prep → Jira update

### Requirement: Manage inter-agent data flow
The system SHALL pass data between agents when workflows span multiple agents (e.g., Browser Test Agent screenshots → Evidence Gatherer → Jira).

#### Scenario: Pass screenshots from Browser Test Agent to Evidence Gatherer
- **WHEN** Browser Test Agent produces an evidence package
- **THEN** the coordinator passes it to the Evidence Gatherer Agent for Jira formatting and attachment

### Requirement: Provide unified status and progress
The system SHALL provide real-time progress feedback to the user during multi-agent workflows.

#### Scenario: Show workflow progress
- **WHEN** a multi-agent workflow is executing
- **THEN** the system displays which agent is currently active, what step it is on, and overall workflow progress

### Requirement: Support human-in-the-loop confirmation
The system SHALL pause and request user confirmation before executing actions with side effects (posting to Jira, updating tickets, deploying).

#### Scenario: Confirm before Jira update
- **WHEN** an agent is about to post content to a Jira ticket
- **THEN** the system shows a preview of the content and waits for user confirmation before proceeding
