## ADDED Requirements

### Requirement: Execute browser test flows per project configuration
The system SHALL execute browser test flows defined in per-project YAML configuration, navigating React web applications, performing actions, and capturing timestamped screenshots at each step.

#### Scenario: Run a configured test flow
- **WHEN** user triggers a test flow for a specific project
- **THEN** the system opens a Playwright browser, navigates through the defined steps (navigate, click, type, wait), and captures a screenshot at each capture point

#### Scenario: Handle authentication
- **WHEN** a project's test flow requires login
- **THEN** the system performs the configured authentication steps (form login, SSO redirect, etc.) before executing test steps

### Requirement: Per-project YAML test configuration
The system SHALL support YAML configuration files defining test flows for each of the 9 React projects, including base URL, authentication method, and ordered test steps with screenshot capture points.

#### Scenario: Load and validate project test config
- **WHEN** user specifies a project for test execution
- **THEN** the system loads the project's YAML config, validates required fields (base_url, auth, test_flows), and reports any configuration errors

### Requirement: Capture before/after upgrade comparisons
The system SHALL support capturing baseline screenshots before an upgrade and comparison screenshots after, generating a side-by-side visual comparison report.

#### Scenario: Capture baseline screenshots
- **WHEN** user triggers a baseline capture for a project before upgrade
- **THEN** the system executes all test flows and saves screenshots with a "baseline" label and timestamp

#### Scenario: Generate upgrade comparison report
- **WHEN** user triggers a post-upgrade capture for a project that has baseline screenshots
- **THEN** the system captures post-upgrade screenshots and generates an HTML comparison report with side-by-side images and visual diff indicators

### Requirement: Package screenshots as evidence
The system SHALL package all captured screenshots with metadata (timestamps, step names, pass/fail status) into a structured evidence package for consumption by other agents.

#### Scenario: Produce evidence package
- **WHEN** a test flow execution completes
- **THEN** the system produces a structured evidence package containing all screenshots, step metadata, timestamps, and overall pass/fail status

### Requirement: Support all 9 React projects
The system SHALL support independent test configurations for 9 React web applications, allowing concurrent or sequential test execution across projects.

#### Scenario: Run tests for all projects
- **WHEN** user triggers a full regression run
- **THEN** the system executes test flows for all 9 configured projects and produces an aggregate report with per-project evidence packages
