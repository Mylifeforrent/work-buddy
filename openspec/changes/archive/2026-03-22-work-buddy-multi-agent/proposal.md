## Why

We manage 13+ applications (3 React web apps + 10+ backend API services) across the full SDLC. Each project cycle involves significant repetitive, manual, compliance-driven work: creating Jira tasks with specific tags/epics/sprints, capturing testing evidence from web dashboards (OpenSearch logs, SpringBoot Admin status, Grafana metrics) and app UIs, validating ICE compliance before production releases, writing release documentation, locating project specs in Confluence, and triaging production alerts. These tasks follow well-known patterns but collectively consume hours per cycle, multiplied across 13+ projects.

A multi-agent system ("Work Buddy") can automate the majority of this work. The system will be built as an **enterprise-grade reference architecture** with mocked external services, enabling fully local development and testing. All external dependencies (Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin, Corporate SSO) are abstracted behind service interfaces (ports & adapters / hexagonal architecture), allowing seamless swapping between mock and real implementations.

## What Changes

- **New multi-agent system** with 7+ specialized agents covering the full SDLC
- **Hexagonal architecture** with service interfaces (ABCs) and pluggable adapters (mock/real)
- **Browser-based screenshot capture** for both React app UIs (3 apps) and monitoring dashboards (OpenSearch, SpringBoot Admin, Grafana) across all services
- **Mock service layer** for all external dependencies — Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin, Corporate SSO — enabling fully local execution
- **Docker Compose** for local development with all mock services
- **Corporate SSO abstraction** supporting per-tool separate authentication (no session sharing)
- **Jira automation** for task creation, evidence attachment, and compliance validation
- **Release documentation generation** from git history and Jira context
- **Confluence document retrieval** via RAG-enhanced search
- **Production log analysis** integrating Grafana, Prometheus, and OpenSearch APIs
- **Per-project YAML configuration** supporting 3 React apps and 10+ backend services with different tool instance mappings
- **Postman/Newman integration** for backend API testing evidence
- **Coordinator/orchestrator layer** using LangGraph for agent communication and task routing

## Capabilities

### New Capabilities
- `jira-task-automation`: Automated Jira task creation with correct tags, epics, sprints, descriptions, and labels based on project-specific templates
- `evidence-gathering`: Collection and formatting of Dev/UAT/Regression/Performance test results from CI/CD pipelines and browser screenshots into structured Jira comments with attachments
- `browser-test-agent`: Playwright-based browser automation that captures screenshots from React app UIs (3 apps) AND monitoring dashboards (OpenSearch, SpringBoot Admin, Grafana) for 10+ backend services — with per-project config and per-service keyword-based log searches
- `ice-compliance-validation`: Pre-release validation of Jira tickets against ICE standards — checking evidence completeness, template conformance, labels, tags, and CR details
- `release-prep`: Generation of release documentation (background, implementation steps, release notes, PVT steps, rollback steps) from git history, PR descriptions, and Jira context
- `confluence-doc-retrieval`: RAG-enhanced search and retrieval of project specs and articles from Confluence pages
- `log-analysis-and-pvt`: Production alert triage via Grafana/Prometheus/OpenSearch log correlation, plus scheduled PVT health checks with screenshot capture and keyword verification
- `agent-coordinator`: Orchestration layer that routes user requests to appropriate agents, manages inter-agent data flow, and provides a unified CLI interface
- `mock-services`: Complete mock implementations of all external services (Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin, SSO) as React-based web applications with realistic UIs and simulated APIs, enabling fully local development and visual verification of agent browser flows
- `service-abstractions`: Hexagonal architecture with service interfaces (ports) and pluggable adapters, allowing one-config switch between mock and real implementations
- `mcp-service-transport`: MCP (Model Context Protocol) server integration for external services — Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin can be accessed via MCP servers as an alternative transport layer, enabling AI coding assistants to directly invoke Work Buddy capabilities as MCP tools
- `video-gif-evidence`: Video recording (WebM) and GIF screenshot capture during browser test flows — Playwright native video recording with ffmpeg-based GIF conversion, providing full video for detailed review and GIF previews for Jira evidence comments

### Modified Capabilities
- `browser-test-agent`: Enhanced with video recording lifecycle — each test flow is now recorded as WebM video and converted to GIF for evidence verification
- `evidence-gathering`: Evidence packages now include recordings (WebM) and GIF previews alongside static PNG screenshots

## Impact

- **New codebase**: Full multi-agent system with Python backend, hexagonal architecture
- **External API abstractions**: Service interfaces for Jira, Confluence, Grafana, Prometheus, OpenSearch, SpringBoot Admin
- **MCP integration**: External services accessible via MCP servers — agents can connect through MCP protocol alongside direct adapter pattern, enabling AI assistant composability
- **Mock servers**: FastAPI-based mock services runnable via Docker Compose
- **Browser automation**: Playwright for React UIs + monitoring dashboard screenshot capture + video/GIF recording
- **LLM dependency**: For release note generation, log analysis reasoning, and document retrieval (RAG)
- **Configuration surface**: Per-project YAML configs for 13+ apps (URLs, auth, test flows, tool instance mappings, keywords)
- **Auth complexity**: Corporate SSO with separate sessions per tool — abstracted for mock/real swap
- **Local infrastructure**: Docker Compose with mock Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin, SSO servers
- **ffmpeg dependency**: Required for video-to-GIF conversion in evidence capture pipeline
