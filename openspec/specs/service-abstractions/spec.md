## ADDED Requirements

### Requirement: Abstract all external services behind interfaces
The system SHALL define Python abstract base classes (ABCs) for every external service (Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin, SSO, Browser), ensuring agents never depend on concrete implementations.

#### Scenario: Agent uses service interface, not implementation
- **WHEN** the Jira Task Agent creates a ticket
- **THEN** it calls methods on JiraService (ABC), not on a specific Jira client or mock directly

### Requirement: Support mock and real adapters for each service
The system SHALL provide at least a mock adapter for each service interface. Real adapters SHALL be stub files with clear integration points for the user to implement.

#### Scenario: Switch from mock to real via configuration
- **WHEN** the global config is set to `mode: live` and a service has a real adapter
- **THEN** the dependency injection layer instantiates the real adapter instead of the mock

#### Scenario: Real adapter stubs guide implementation
- **WHEN** a developer opens a real adapter stub (e.g., `real_jira.py`)
- **THEN** the file contains the ABC implementation skeleton with TODO comments and documentation explaining what each method should do with the real API

### Requirement: Dependency injection for adapter selection
The system SHALL use a dependency injection container (or factory pattern) that reads the global configuration to select mock or real adapters for each service.

#### Scenario: Inject mock adapters in local mode
- **WHEN** `app.yaml` contains `mode: mock`
- **THEN** all service interfaces are bound to their mock adapter implementations

#### Scenario: Inject real adapters in live mode
- **WHEN** `app.yaml` contains `mode: live`
- **THEN** all service interfaces are bound to their real adapter implementations (or raise an error if not implemented)

### Requirement: Credential store abstraction
The system SHALL provide a credential store interface with mock (in-memory) and real (keyring-based) implementations, ensuring no credentials are hardcoded.

#### Scenario: Retrieve credentials in mock mode
- **WHEN** the system needs SSO credentials in mock mode
- **THEN** the mock credential store returns pre-configured test credentials

#### Scenario: Retrieve credentials in live mode
- **WHEN** the system needs SSO credentials in live mode
- **THEN** the real credential store retrieves them from the system keyring or environment variables
