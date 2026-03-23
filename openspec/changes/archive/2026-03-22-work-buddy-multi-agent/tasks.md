## 1. Project Setup & Shared Infrastructure

- [x] 1.1 Initialize Python project with pyproject.toml (dependencies: langgraph, playwright, jira, atlassian-python-api, pyyaml, chromadb, fastapi, uvicorn, httpx, typer, pydantic)
- [x] 1.2 Create project directory structure: src/{agents, core, services, adapters/mock, adapters/real, cli}, configs/projects, mock_servers, tests/{unit, integration, e2e}
- [x] 1.3 Set up Typer CLI entry point with command structure (test, jira, compliance, release, pvt, docs, alert)
- [x] 1.4 Implement structured logging module with agent execution tracing
- [x] 1.5 Create Dockerfile and docker-compose.yml scaffold for mock services

## 2. Service Abstractions (Ports & Adapters)

- [x] 2.1 Define JiraService ABC (create_task, add_comment, attach_file, update_labels, get_ticket, search_tickets)
- [x] 2.2 Define ConfluenceService ABC (search_pages, get_page_content, get_page_by_id)
- [x] 2.3 Define OpenSearchService ABC (search_logs, get_log_entries)
- [x] 2.4 Define GrafanaService ABC (get_dashboard, get_metrics)
- [x] 2.5 Define SpringBootAdminService ABC (list_services, get_service_health, get_r2db_status)
- [x] 2.6 Define SSOAuthService ABC (authenticate, is_authenticated, get_session)
- [x] 2.7 Define BrowserService ABC (navigate, screenshot, click, type_text, wait_for, assert_text)
- [x] 2.8 Define CredentialStore ABC (get_credentials, store_credentials)
- [x] 2.9 Implement dependency injection container / factory that reads app.yaml mode (mock/live) and instantiates correct adapters
- [x] 2.10 Implement shared configuration loader with Pydantic schema validation for project YAML configs
- [x] 2.11 Create app.yaml global config with mode flag (mock/live) and common settings
- [x] 2.12 Create sample project configs: 1 React app config + 1 backend service config with tool URL mappings and keywords

## 3. Mock Services (Docker Compose)

- [x] 3.1 Build Mock SSO server (FastAPI) — login form UI, session cookie issuance, accepts any staffid/password
- [x] 3.2 Build Mock Jira server (FastAPI) — REST API for tickets, comments, attachments, labels, epics, sprints; seeded with sample data
- [x] 3.3 Build Mock Confluence server (FastAPI) — REST API for page search and content retrieval; seeded with sample markdown pages
- [x] 3.4 Build Mock OpenSearch server (FastAPI) — REST API for log search + minimal Dashboards web UI with search bar and results table; SSO-protected; seeded with sample log entries per service
- [x] 3.5 Build Mock SpringBoot Admin server (FastAPI) — Web UI showing registered services with health details and R2DB status; SSO-protected; configurable service list
- [x] 3.6 Build Mock Grafana server (FastAPI) — Web UI with simple metric dashboards per service; SSO-protected; configurable chart data
- [x] 3.7 Create seed data YAML files for all mock services (sample tickets, log entries, services, metrics, Confluence pages)
- [x] 3.8 Create Dockerfiles for each mock service
- [x] 3.9 Create docker-compose.yml wiring all mock services with correct ports and seed data volumes
- [x] 3.10 Write startup health check script to verify all mock services are running

## 4. Mock Adapters (In-Process)

- [x] 4.1 Implement MockJiraAdapter (JiraService ABC) — calls Mock Jira server API via httpx
- [x] 4.2 Implement MockConfluenceAdapter (ConfluenceService ABC) — calls Mock Confluence server API
- [x] 4.3 Implement MockOpenSearchAdapter (OpenSearchService ABC) — calls Mock OpenSearch server API
- [x] 4.4 Implement MockGrafanaAdapter (GrafanaService ABC) — calls Mock Grafana server API
- [x] 4.5 Implement MockSpringBootAdminAdapter (SpringBootAdminService ABC) — calls Mock SpringBoot Admin server API
- [x] 4.6 Implement MockSSOAuthAdapter (SSOAuthService ABC) — calls Mock SSO server
- [x] 4.7 Implement MockCredentialStore (CredentialStore ABC) — returns test credentials from config
- [x] 4.8 Create real adapter stubs with TODO comments for all services (real_jira.py, real_confluence.py, etc.)

## 5. Browser Test Agent

- [x] 5.1 Set up Playwright browser manager (launch, context, page lifecycle) implementing BrowserService
- [x] 5.2 Implement SSO authentication handler for Playwright (detect SSO redirect → login → return to tool)
- [x] 5.3 Implement React app UI test flow executor (navigate pages, interact, screenshot)
- [x] 5.4 Implement OpenSearch dashboard test flow (open Dashboards UI, search with keywords, screenshot results)
- [x] 5.5 Implement SpringBoot Admin test flow (navigate to service, check R2DB status, screenshot)
- [x] 5.6 Implement Grafana dashboard test flow (navigate to service dashboard, screenshot metrics)
- [x] 5.7 Implement evidence package generator (screenshots + metadata JSON with source tool labels)
- [x] 5.8 Implement baseline capture mode for upgrade comparisons
- [x] 5.9 Implement post-upgrade comparison with side-by-side HTML report
- [x] 5.10 Implement Newman/Postman collection runner with report capture
- [x] 5.11 Add per-project test flow configuration with tool URL routing
- [x] 5.12 Write unit tests for test flow executor with mock browser
- [x] 5.13 Write integration test against mock services via Docker Compose

## 6. Jira Task Agent

- [x] 6.1 Implement Jira Task Agent using JiraService interface
- [x] 6.2 Build project-specific template engine for Jira Description field
- [x] 6.3 Implement auto-population of Epic, Sprint, Labels, Components from project config
- [x] 6.4 Implement bulk task creation from requirement list
- [x] 6.5 Add validation for unknown project names
- [x] 6.6 Write unit tests with MockJiraAdapter

## 7. Evidence Gatherer Agent

- [x] 7.1 Implement Evidence Gatherer Agent using JiraService interface
- [x] 7.2 Build Jira comment formatter with structured sections (Dev, UAT, Regression, Performance)
- [x] 7.3 Implement screenshot/file attachment to Jira comments
- [x] 7.4 Build integration with Browser Test Agent evidence packages (React app + dashboard screenshots)
- [x] 7.5 Build integration with Newman test report output
- [x] 7.6 Add evidence type labeling on comments
- [x] 7.7 Write unit tests with MockJiraAdapter

## 8. ICE Compliance Agent

- [x] 8.1 Define ICE compliance rules YAML schema
- [x] 8.2 Implement compliance rule loader from external config
- [x] 8.3 Build Jira ticket validator using JiraService interface (evidence, labels, tags, template)
- [x] 8.4 Implement gap detection with remediation guidance
- [x] 8.5 Implement auto-fix for missing labels/tags (with human-in-the-loop confirmation)
- [x] 8.6 Build description template conformance checker
- [x] 8.7 Write unit tests with MockJiraAdapter and sample ICE rules

## 9. Release Prep Agent

- [x] 9.1 Implement git history parser (PRs, commits for a version/Epic)
- [x] 9.2 Build LLM-powered release notes generator (from Jira tasks + git context)
- [x] 9.3 Build implementation steps generator (from PR descriptions)
- [x] 9.4 Implement PVT steps generator from project template
- [x] 9.5 Implement rollback steps generator from deployment config template
- [x] 9.6 Build background/context generator (from Jira Epic description)
- [x] 9.7 Integrate with ICE Compliance Agent for pre-release validation
- [x] 9.8 Implement Jira update with generated content (after human review)
- [x] 9.9 Write unit tests for document generation

## 10. Log Analyst & PVT Agent

- [x] 10.1 Implement PVT health check executor using Browser Test Agent (login screenshot, keyword search, log extraction)
- [x] 10.2 Implement alert triage engine using LLM (correlate data from Grafana, OpenSearch via service interfaces)
- [x] 10.3 Build triage recommendation generator (ignore / needs attention / critical)
- [x] 10.4 Implement PVT report generator (HTML with screenshots, keyword results, logs)
- [x] 10.5 Implement alert triage report generator
- [x] 10.6 Write unit tests with mock service adapters

## 11. Confluence Doc Retriever Agent (RAG)

- [x] 11.1 Implement Confluence indexer using ConfluenceService interface (fetch, chunk, embed, store in ChromaDB)
- [x] 11.2 Build RAG search pipeline (query → embed → retrieve → re-rank → respond)
- [x] 11.3 Build LLM-powered document summarizer
- [x] 11.4 Write unit tests with MockConfluenceAdapter

## 12. Agent Coordinator & Orchestration (LangGraph)

- [x] 12.1 Implement LangGraph coordinator graph with agent nodes
- [x] 12.2 Build request parser to route user CLI commands to appropriate agents
- [x] 12.3 Implement inter-agent data flow (Browser Test → Evidence Gatherer → Jira)
- [x] 12.4 Build multi-agent workflow orchestration (e.g., release prep: compliance → docs → Jira update)
- [x] 12.5 Implement human-in-the-loop confirmation for side-effect actions
- [x] 12.6 Build progress display for multi-agent workflows
- [x] 12.7 Write integration tests for multi-agent workflows with mock services

## 13. End-to-End Testing & Documentation

- [x] 13.1 Create project configs for sample React app and sample backend services
- [x] 13.2 E2E test: Browser Test Agent captures screenshots from mock OpenSearch + mock SpringBoot Admin → Evidence Gatherer formats → Mock Jira comment
- [x] 13.3 E2E test: Jira Task Agent creates tasks in Mock Jira with correct fields
- [x] 13.4 E2E test: ICE Compliance Agent validates Mock Jira ticket
- [x] 13.5 E2E test: Release prep pipeline (compliance → doc gen → Jira update)
- [x] 13.6 E2E test: PVT health check flow with mock services
- [x] 13.7 Write README.md with architecture overview, setup instructions, config guide, usage examples
- [x] 13.8 Write CONTRIBUTING.md with guide for adding real adapters

## 14. MCP Integration Design

- [x] 14.1 Update design.md with MCP as Service Transport decision (Decision 9)
- [x] 14.2 Update architecture diagram to show MCP client adapter layer alongside direct adapters
- [x] 14.3 Update proposal.md with mcp-service-transport capability
- [x] 14.4 Document Skills layer (composable capabilities) in design diagram
- [x] 14.5 Add MCP-related risks/trade-offs to design.md

## 15. Video/GIF Evidence Recording

- [ ] 15.1 Add Recording dataclass and recording methods to BrowserService ABC
- [ ] 15.2 Extend EvidencePackage with recordings and gifs fields
- [ ] 15.3 Implement Playwright video recording in RealBrowserAdapter (start_recording, stop_recording)
- [ ] 15.4 Implement ffmpeg-based GIF conversion in RealBrowserAdapter (convert_to_gif)
- [ ] 15.5 Wrap BrowserTestAgent flow methods with recording lifecycle
- [ ] 15.6 Update README.md architecture diagram with video/GIF recording capability
- [ ] 15.7 Write unit tests for recording lifecycle in test_browser_agent.py

## 16. React-based Mock Services Implementation

- [ ] 16.1 Create unified React project structure in `mock_servers/ui`
- [ ] 16.2 Implement Mock SSO UI (Login page)
- [ ] 16.3 Implement Mock Jira UI (Issue dashboard/view)
- [ ] 16.4 Implement Mock Confluence UI (Page list/view)
- [ ] 16.5 Implement Mock OpenSearch UI (Logs/Dashboards)
- [ ] 16.6 Implement Mock SpringBoot Admin UI (Health dashboard)
- [ ] 16.7 Implement Mock Grafana UI (Metrics dashboards)
- [ ] 16.8 Update Python mock servers to serve React build as static files
- [ ] 16.9 Update Dockerfiles for multi-stage React builds
- [ ] 16.10 Verify browser agent navigation and screenshot capture against React UIs

