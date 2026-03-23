## ADDED Requirements

### Requirement: Cron-based scheduled PVT execution
The system SHALL support scheduled PVT execution using cron expressions, allowing automatic health checks at configured times without manual triggering.

#### Scenario: Enable scheduled PVT in configuration
- **WHEN** user configures `pvt_schedule.enabled: true` and a cron expression in project config
- **THEN** the system automatically triggers PVT health checks at the specified schedule

#### Scenario: Disable scheduled PVT
- **WHEN** user configures `pvt_schedule.enabled: false`
- **THEN** the system does not trigger automatic PVT health checks (manual only)

#### Scenario: Scheduled PVT with notification
- **WHEN** a scheduled PVT completes
- **THEN** the system can optionally notify configured channels (Slack, email, Jira comment)

### Requirement: PVT schedule configuration
The system SHALL support per-project PVT schedule configuration with enable/disable switch:

```yaml
pvt_schedule:
  enabled: true/false
  cron: "0 6 * * *"  # Every day at 6 AM
  timezone: "Asia/Shanghai"
  notify:
    slack_channel: "#alerts"
    jira_comment: true
```

#### Scenario: Load PVT schedule from project config
- **WHEN** the application starts
- **THEN** it loads PVT schedule settings from each project's YAML configuration

#### Scenario: Timezone-aware scheduling
- **WHEN** a cron schedule is configured with a timezone
- **THEN** the system executes PVT at the correct local time in that timezone

### Requirement: Scheduler daemon management
The system SHALL provide CLI commands to manage the PVT scheduler:
- View current schedule status
- Start the scheduler daemon
- Stop the scheduler daemon

#### Scenario: View PVT schedule status
- **WHEN** user runs `workbuddy pvt schedule`
- **THEN** the system displays all project schedules with enabled status and next run times

#### Scenario: Start scheduler daemon
- **WHEN** user runs `workbuddy pvt start-scheduler`
- **THEN** the system starts background tasks for all enabled project schedules