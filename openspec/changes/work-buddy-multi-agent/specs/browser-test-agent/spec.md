## ADDED Requirements

### Requirement: Execute browser test flows for React web applications
The system SHALL execute browser test flows defined in per-project YAML configuration for 3 React web apps, navigating the application UI, performing actions, and capturing timestamped screenshots at each step.

#### Scenario: Run a React app UI test flow
- **WHEN** user triggers a test flow for a React web app project
- **THEN** the system opens a Playwright browser, performs SSO authentication, navigates through the defined steps, and captures a screenshot at each capture point

### Requirement: Capture monitoring dashboard screenshots for backend services
The system SHALL capture screenshots from OpenSearch, SpringBoot Admin, and Grafana dashboards as testing evidence for backend services, using per-service configured tool URLs and keywords.

#### Scenario: Capture OpenSearch log evidence
- **WHEN** user triggers evidence capture for a backend service
- **THEN** the system opens the service's configured OpenSearch instance, authenticates via SSO, executes the configured search queries with service-specific keywords, and captures screenshots of the log results

#### Scenario: Capture SpringBoot Admin R2DB status
- **WHEN** user triggers evidence capture for a backend service with SpringBoot Admin configured
- **THEN** the system opens the service's configured SpringBoot Admin instance, navigates to the service, verifies R2DB status shows "UP", and captures a screenshot

#### Scenario: Capture Grafana metrics dashboard
- **WHEN** user triggers evidence capture for a backend service with Grafana configured
- **THEN** the system opens the service's configured Grafana instance, navigates to the service dashboard, and captures a screenshot of the metrics

### Requirement: Handle Corporate SSO authentication per tool
The system SHALL authenticate via Corporate SSO for each monitoring tool separately, as sessions are not shared between tools. The SSO handler SHALL be abstracted to support mock and real implementations.

#### Scenario: SSO login for each tool independently
- **WHEN** the agent needs to access a tool that requires authentication
- **THEN** the system detects the SSO redirect, navigates to the login form, enters staffid and password, completes the login, and returns to the tool

#### Scenario: Use mock SSO in local development
- **WHEN** the system is running in mock mode
- **THEN** the mock SSO accepts any staffid/password and issues a session cookie

### Requirement: Per-project YAML configuration with tool instance mapping
The system SHALL support YAML configuration files per project specifying the base URLs for each monitoring tool instance (OpenSearch, SpringBoot Admin, Grafana), since not all services share the same instances.

#### Scenario: Load project config with tool URLs
- **WHEN** user triggers a test for a specific project
- **THEN** the system loads the project's YAML config including the correct tool instance URLs for that project's cluster

### Requirement: Capture before/after upgrade comparisons
The system SHALL support capturing baseline screenshots before an upgrade and comparison screenshots after, generating a side-by-side visual comparison report.

#### Scenario: Generate upgrade comparison report
- **WHEN** user triggers a post-upgrade capture for a project that has baseline screenshots
- **THEN** the system captures post-upgrade screenshots and generates an HTML comparison report with side-by-side images

### Requirement: Package screenshots as evidence
The system SHALL package all captured screenshots with metadata (timestamps, step names, pass/fail status, source tool) into a structured evidence package for consumption by other agents.

#### Scenario: Produce evidence package from mixed sources
- **WHEN** evidence capture completes for a backend service (OpenSearch + SpringBoot Admin + Grafana)
- **THEN** the system produces a single evidence package containing all screenshots with source tool labels and metadata

### Requirement: Run Postman collections via Newman for API testing
The system SHALL execute Postman collections via Newman CLI for backend services and capture the test report as evidence.

#### Scenario: Run Newman and capture report
- **WHEN** user triggers API testing for a backend service with a configured Postman collection
- **THEN** the system runs Newman CLI, captures the HTML/JSON test report, and includes it in the evidence package
