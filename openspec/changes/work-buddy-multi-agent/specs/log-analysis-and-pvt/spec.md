## ADDED Requirements

### Requirement: Execute scheduled PVT health checks
The system SHALL perform PVT health checks at scheduled times (e.g., after upstream maintenance), capturing login page screenshots, searching for keywords on specific pages, and extracting logs for secondary confirmation.

#### Scenario: PVT health check passes
- **WHEN** a PVT health check is triggered for a project
- **THEN** the system captures a login page screenshot, navigates to configured pages, verifies expected keywords are present, extracts relevant logs, and produces a PVT report with pass status

#### Scenario: PVT health check fails
- **WHEN** a PVT health check finds missing keywords or login failures
- **THEN** the system produces a PVT report with fail status, failed step details, screenshots showing the failure, and relevant log excerpts

### Requirement: Triage production alerts via log correlation
The system SHALL analyze production alerts by querying Grafana dashboards, Prometheus metrics, and OpenSearch logs, correlating data across sources to provide a triage recommendation.

#### Scenario: Alert is transient and can be ignored
- **WHEN** a production alert fires and log analysis shows a brief upstream hiccup with auto-recovery
- **THEN** the system recommends "Safe to ignore — transient upstream issue" with supporting evidence from logs and metrics

#### Scenario: Alert requires manual intervention
- **WHEN** a production alert fires and log analysis shows elevated error rates or service degradation
- **THEN** the system recommends "Needs attention" with a summary of affected services, error patterns, and suggested investigation steps

#### Scenario: Critical alert detected
- **WHEN** a production alert fires and log analysis shows service downtime or data loss risk
- **THEN** the system recommends "Critical — immediate intervention required" with detailed log excerpts, metric graphs references, and escalation guidance

### Requirement: Query multiple observability platforms
The system SHALL support querying Grafana API for dashboard data, Prometheus API for metrics, and OpenSearch API for log entries.

#### Scenario: Correlate data across platforms
- **WHEN** the system triages an alert
- **THEN** it queries all three platforms (Grafana, Prometheus, OpenSearch) and correlates the data by timestamp and service identifier

### Requirement: Generate PVT and alert triage reports
The system SHALL produce structured reports for both PVT health checks and alert triage, suitable for attaching to Jira or sharing with the team.

#### Scenario: Generate PVT report
- **WHEN** PVT health checks complete
- **THEN** the system produces an HTML/PDF report with screenshots, keyword verification results, log excerpts, and overall status

#### Scenario: Generate alert triage report
- **WHEN** alert triage completes
- **THEN** the system produces a structured report with alert details, correlated log entries, metric summaries, and triage recommendation
