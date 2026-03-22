## Why

Managing 9 React web application projects across the full SDLC involves significant repetitive, manual, compliance-driven work: creating Jira tasks with specific tags/epics/sprints, capturing and attaching testing evidence (Dev, UAT, Regression, Performance), validating ICE compliance before production releases, writing release documentation (background, implementation steps, PVT, rollback), locating project specs in Confluence, and triaging production alerts from Grafana/Prometheus/OpenSearch. These tasks follow well-known patterns but collectively consume hours per project cycle, multiplied across 9 projects.

A multi-agent system ("Work Buddy") can automate the majority of this work — each agent specializing in one phase of the workflow, with shared infrastructure for Jira integration, browser automation, and configuration management.

## What Changes

- **New multi-agent system** with 7 specialized agents covering the full SDLC
- **Browser-based test automation** for capturing regression/performance screenshots across 9 React apps
- **Jira automation** for task creation, evidence attachment, and compliance validation
- **Release documentation generation** from git history and Jira context
- **Confluence document retrieval** via RAG-enhanced search
- **Production log analysis** integrating Grafana, Prometheus, and OpenSearch APIs
- **Per-project configuration** supporting 9 distinct React web applications
- **Coordinator/orchestrator layer** for agent communication and task routing

## Capabilities

### New Capabilities
- `jira-task-automation`: Automated Jira task creation with correct tags, epics, sprints, descriptions, and labels based on project-specific templates
- `evidence-gathering`: Collection and formatting of Dev/UAT/Regression/Performance test results from CI/CD pipelines into structured Jira comments with attachments
- `browser-test-agent`: Playwright-based browser automation that navigates React apps, executes test flows, and captures timestamped screenshots as evidence — with per-project config for 9 apps
- `ice-compliance-validation`: Pre-release validation of Jira tickets against ICE standards — checking evidence completeness, template conformance, labels, tags, and CR details
- `release-prep`: Generation of release documentation (background, implementation steps, release notes, PVT steps, rollback steps) from git history, PR descriptions, and Jira context
- `confluence-doc-retrieval`: RAG-enhanced search and retrieval of project specs and articles from Confluence pages
- `log-analysis-and-pvt`: Production alert triage via Grafana/Prometheus/OpenSearch log correlation, plus scheduled PVT health checks with screenshot capture and keyword verification
- `agent-coordinator`: Orchestration layer that routes user requests to appropriate agents, manages inter-agent data flow, and provides a unified interaction interface

### Modified Capabilities
_(none — this is a greenfield project)_

## Impact

- **New codebase**: Full multi-agent system with Python backend
- **External API dependencies**: Jira REST API, Confluence API, Grafana API, Prometheus API, OpenSearch API
- **Browser automation dependency**: Playwright for headless/headful browser testing
- **LLM dependency**: Required for release note generation, log analysis reasoning, and document retrieval (RAG)
- **Configuration surface**: Per-project YAML configs for 9 React apps (URLs, auth, test flows)
- **Infrastructure**: Needs a runtime environment (local machine, internal server, or Docker) with access to internal tools
