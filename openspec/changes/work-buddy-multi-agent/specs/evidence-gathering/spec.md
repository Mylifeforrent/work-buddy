## ADDED Requirements

### Requirement: Collect test results from CI/CD pipelines
The system SHALL collect test results (Dev, UAT, Regression, Performance) from CI/CD pipelines and format them as structured Jira comments.

#### Scenario: Collect and format Dev test results
- **WHEN** a Dev test cycle completes or user triggers evidence collection
- **THEN** the system retrieves test results from the CI/CD pipeline and formats them into a structured comment ready for Jira

#### Scenario: Collect and format Performance test results
- **WHEN** a Performance test cycle completes or user triggers evidence collection
- **THEN** the system retrieves performance test metrics and formats them with pass/fail status and key metrics

### Requirement: Attach evidence to Jira comments
The system SHALL attach formatted test evidence (including screenshots and reports) to the corresponding Jira ticket as comments with evidence type labels.

#### Scenario: Attach evidence with type label
- **WHEN** evidence is formatted for a specific test type (Dev/UAT/Regression/Performance)
- **THEN** the system posts a Jira comment tagged with the evidence type and attaches any associated screenshots or report files

### Requirement: Consume Browser Test Agent output
The system SHALL accept screenshot packages and test results from the Browser Test Agent as input for evidence formatting.

#### Scenario: Format browser test screenshots as evidence
- **WHEN** the Browser Test Agent produces a set of timestamped screenshots for a test flow
- **THEN** the Evidence Gatherer formats them into a structured evidence comment with screenshot attachments and step descriptions
