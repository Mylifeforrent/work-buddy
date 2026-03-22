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
The system SHALL attach formatted test evidence (including screenshots and reports) to the corresponding Jira ticket as comments with evidence type labels. Uses the JiraService interface (not direct API calls).

#### Scenario: Attach evidence with type label
- **WHEN** evidence is formatted for a specific test type (Dev/UAT/Regression/Performance)
- **THEN** the system posts a Jira comment tagged with the evidence type and attaches any associated screenshots or report files

### Requirement: Consume Browser Test Agent output
The system SHALL accept screenshot evidence packages from the Browser Test Agent (covering both React app UIs and monitoring dashboard screenshots) as input for evidence formatting.

#### Scenario: Format mixed evidence from React app and monitoring dashboards
- **WHEN** the Browser Test Agent produces evidence packages containing React app screenshots, OpenSearch log screenshots, SpringBoot Admin screenshots, and Grafana screenshots
- **THEN** the Evidence Gatherer formats them into organized Jira comments with sections per evidence source

### Requirement: Consume Newman test reports
The system SHALL accept Newman CLI test reports as input and format them as API testing evidence for Jira.

#### Scenario: Format Newman report as API test evidence
- **WHEN** a Postman collection has been executed via Newman and a report is available
- **THEN** the Evidence Gatherer formats the report into a Jira comment with pass/fail summary and attaches the full report
