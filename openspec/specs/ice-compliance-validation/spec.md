## ADDED Requirements

### Requirement: Validate Jira ticket against ICE standards
The system SHALL validate a Jira ticket's compliance with ICE (Internal Compliance Engine) standards, checking for required testing evidence (Dev, UAT, Regression, Performance), correct labels/tags, description template conformance, and CR details completeness.

#### Scenario: Full compliance check passes
- **WHEN** user requests ICE compliance validation for a Jira ticket that has all required evidence, labels, and template fields
- **THEN** the system reports the ticket as compliant with a checklist showing all passing items

#### Scenario: Compliance check identifies gaps
- **WHEN** user requests ICE compliance validation for a Jira ticket missing required evidence or fields
- **THEN** the system reports each gap (e.g., "Missing: UAT testing evidence", "Missing label: release-approved") with specific remediation guidance

### Requirement: Auto-fix labels and tags
The system SHALL offer to automatically add missing required labels and tags to a Jira ticket when compliance gaps are detected.

#### Scenario: Auto-fix missing labels
- **WHEN** a compliance check finds missing labels/tags
- **THEN** the system offers to auto-apply the missing labels and, upon user confirmation, updates the Jira ticket

### Requirement: Validate description template conformance
The system SHALL validate that a Jira ticket's description follows the required template structure for the ticket type and project.

#### Scenario: Description follows template
- **WHEN** a ticket's description includes all required sections from the project's template
- **THEN** the system reports description template compliance as passing

#### Scenario: Description missing required sections
- **WHEN** a ticket's description is missing required template sections
- **THEN** the system reports which sections are missing and provides the template structure for reference

### Requirement: Configurable ICE rules
The system SHALL support externalized ICE compliance rules in YAML configuration, allowing rules to be updated without code changes.

#### Scenario: Load ICE rules from config
- **WHEN** the system performs a compliance check
- **THEN** it loads the current ICE rules from the YAML config file, not from hardcoded values
