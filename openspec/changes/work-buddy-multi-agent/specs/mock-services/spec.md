## ADDED Requirements

### Requirement: Provide mock implementations for all external services
The system SHALL include mock implementations for Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin, and Corporate SSO, enabling the entire multi-agent system to run fully locally without access to real services.

#### Scenario: Run all mocks via Docker Compose
- **WHEN** developer runs `docker compose up`
- **THEN** all mock services start and are accessible on their configured ports, ready for agent interaction

### Requirement: Mock Jira with realistic API
The system SHALL provide a mock Jira server (FastAPI) that supports creating tasks, adding comments with attachments, managing labels/tags, querying tickets, and simulating Epic/Sprint structures.

#### Scenario: Create and query mock Jira ticket
- **WHEN** the Jira Task Agent creates a ticket via the mock Jira API
- **THEN** the mock stores the ticket and returns it with a realistic ticket ID (e.g. "PROJ-123"), and the ticket is queryable via the mock API

### Requirement: Mock OpenSearch with web dashboard UI
The system SHALL provide a mock OpenSearch server that returns configurable log entries for search queries AND serves a minimal Dashboards-like web UI where the Browser Test Agent can perform searches and capture screenshots.

#### Scenario: Search mock OpenSearch and capture screenshot
- **WHEN** the Browser Test Agent opens the mock OpenSearch Dashboards UI and searches for "service:payment AND level:INFO"
- **THEN** the mock returns pre-configured log entries matching the query, displayed in a realistic table UI that can be screenshotted

### Requirement: Mock SpringBoot Admin with web UI
The system SHALL provide a mock SpringBoot Admin server that displays a list of registered services with their health status (including R2DB connection status) in a web UI.

#### Scenario: Check R2DB status on mock SpringBoot Admin
- **WHEN** the Browser Test Agent navigates to a service on mock SpringBoot Admin
- **THEN** the mock shows the service's health details with R2DB status as "UP" (configurable), displayed in a UI that can be screenshotted

### Requirement: Mock Grafana with dashboard UI
The system SHALL provide a mock Grafana server that displays simple metric dashboards with configurable chart data, rendered as a web page for screenshot capture.

#### Scenario: Capture mock Grafana dashboard screenshot
- **WHEN** the Browser Test Agent navigates to a service dashboard on mock Grafana
- **THEN** the mock renders a realistic-looking dashboard with sample metrics that can be screenshotted

### Requirement: Mock Confluence with searchable content
The system SHALL provide a mock Confluence server that stores markdown files as "pages" and supports search queries, returning results with page content and metadata.

#### Scenario: Search mock Confluence
- **WHEN** the Doc Retriever Agent searches for "payment API specification"
- **THEN** the mock returns matching pages from its stored content with titles, excerpts, and page IDs

### Requirement: Mock Corporate SSO
The system SHALL provide a mock SSO server that simulates corporate SSO login, accepting any staffid/password and issuing session cookies. Each mock tool SHALL redirect to this SSO server when not authenticated.

#### Scenario: SSO redirect and login on mock
- **WHEN** the Browser Test Agent accesses a mock tool without a valid session
- **THEN** the tool redirects to mock SSO, the agent enters credentials, mock SSO issues a session cookie, and the agent is redirected back to the tool

### Requirement: Configurable mock data
The system SHALL support configurable mock data (via YAML or seed files) for all mock services, allowing users to define sample tickets, log entries, services, metrics, and Confluence pages.

#### Scenario: Load seed data on startup
- **WHEN** mock services start via Docker Compose
- **THEN** each mock service loads its seed data from configuration files and is ready to serve realistic responses
