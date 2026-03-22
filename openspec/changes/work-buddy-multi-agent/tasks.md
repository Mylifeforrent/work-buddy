## 1. Project Setup & Shared Infrastructure

- [ ] 1.1 Initialize Python project with pyproject.toml (dependencies: langchain, langgraph, playwright, jira, atlassian-python-api, pyyaml, chromadb)
- [ ] 1.2 Create project directory structure (src/agents/, src/core/, src/config/, configs/projects/, tests/)
- [ ] 1.3 Implement shared configuration loader for per-project YAML configs
- [ ] 1.4 Create project config schema and validation (base_url, auth, jira_settings, test_flows)
- [ ] 1.5 Set up credential management (keyring or .env-based secure storage)
- [ ] 1.6 Create sample project config YAML for one reference project
- [ ] 1.7 Implement shared Jira API client with authentication and rate limiting
- [ ] 1.8 Set up CLI entry point using Click or Typer framework

## 2. Browser Test Agent (Phase 1)

- [ ] 2.1 Set up Playwright browser manager (launch, context, page lifecycle)
- [ ] 2.2 Implement test flow executor that reads YAML step definitions (navigate, click, type, wait, screenshot)
- [ ] 2.3 Implement authentication handler (form login, configurable selectors)
- [ ] 2.4 Implement screenshot capture with timestamps and step labels
- [ ] 2.5 Build evidence package generator (screenshots + metadata JSON)
- [ ] 2.6 Implement baseline capture mode (save screenshots with "baseline" label for upgrade comparisons)
- [ ] 2.7 Implement post-upgrade comparison mode with side-by-side HTML report generation
- [ ] 2.8 Add support for running test flows across all 9 projects with aggregate reporting
- [ ] 2.9 Create test configs for all 9 React projects (URLs, auth, critical pages)
- [ ] 2.10 Write unit tests for test flow executor and evidence packaging
- [ ] 2.11 Write integration test with a sample React app

## 3. Jira Task Agent (Phase 2a)

- [ ] 3.1 Implement Jira task creator with field mapping (Epic, Sprint, Labels, Components, Description)
- [ ] 3.2 Build project-specific template engine for Jira Description field
- [ ] 3.3 Implement bulk task creation from a list of requirements
- [ ] 3.4 Add validation for unknown project names with helpful error messages
- [ ] 3.5 Write unit tests for task creation and template rendering

## 4. Evidence Gatherer Agent (Phase 2b)

- [ ] 4.1 Implement test result collector interface (pluggable for different CI/CD tools)
- [ ] 4.2 Build Jira comment formatter for structured evidence (Dev, UAT, Regression, Performance sections)
- [ ] 4.3 Implement screenshot/file attachment to Jira comments via API
- [ ] 4.4 Build integration with Browser Test Agent output (consume evidence packages)
- [ ] 4.5 Add evidence type labeling on Jira comments
- [ ] 4.6 Write unit tests for formatting and Jira comment posting

## 5. ICE Compliance Agent (Phase 3)

- [ ] 5.1 Define ICE compliance rules schema in YAML format
- [ ] 5.2 Implement compliance rule loader from external YAML config
- [ ] 5.3 Build Jira ticket validator (check evidence presence, labels, tags, description template)
- [ ] 5.4 Implement gap detection with specific remediation guidance
- [ ] 5.5 Implement auto-fix for missing labels and tags (with user confirmation)
- [ ] 5.6 Build description template conformance checker
- [ ] 5.7 Write unit tests for compliance validation with pass/fail/gap scenarios

## 6. Release Prep Agent (Phase 4)

- [ ] 6.1 Implement git history parser (PRs, commits for a version/Epic)
- [ ] 6.2 Build release notes generator using LLM (from Jira tasks + git context)
- [ ] 6.3 Build implementation steps generator (from PR descriptions)
- [ ] 6.4 Implement PVT steps generator from project template with contextual customization
- [ ] 6.5 Implement rollback steps generator from deployment config and template
- [ ] 6.6 Build background/context generator (from Jira Epic description)
- [ ] 6.7 Integrate with ICE Compliance Agent for pre-release validation
- [ ] 6.8 Implement Jira update with generated release content (after user review)
- [ ] 6.9 Write unit tests for document generation

## 7. Log Analyst & PVT Agent (Phase 5)

- [ ] 7.1 Implement Grafana API client for querying dashboard data
- [ ] 7.2 Implement Prometheus API client for querying metrics
- [ ] 7.3 Implement OpenSearch API client for querying log entries
- [ ] 7.4 Build PVT health check executor (login screenshot, keyword search, log extraction — reuses Playwright)
- [ ] 7.5 Implement alert triage engine using LLM (correlate data from Grafana, Prometheus, OpenSearch)
- [ ] 7.6 Build triage recommendation generator (ignore / needs attention / critical)
- [ ] 7.7 Implement PVT report generator (HTML/PDF with screenshots, keyword results, logs)
- [ ] 7.8 Implement alert triage report generator
- [ ] 7.9 Write unit tests for API clients and triage logic

## 8. Confluence Doc Retriever Agent (Phase 6)

- [ ] 8.1 Implement Confluence API client for page retrieval
- [ ] 8.2 Set up ChromaDB vector store for Confluence content indexing
- [ ] 8.3 Build Confluence content indexer (fetch, chunk, embed, store)
- [ ] 8.4 Implement RAG search pipeline (query → embed → retrieve → re-rank → respond)
- [ ] 8.5 Build document summarizer using LLM
- [ ] 8.6 Write unit tests for retrieval and summarization

## 9. Agent Coordinator & Orchestration

- [ ] 9.1 Implement LangGraph coordinator with agent routing logic
- [ ] 9.2 Build request parser to identify target agent from user input
- [ ] 9.3 Implement inter-agent data flow (Browser Test → Evidence Gatherer → Jira)
- [ ] 9.4 Build multi-agent workflow orchestration (e.g., release prep pipeline)
- [ ] 9.5 Implement human-in-the-loop confirmation for side-effect actions
- [ ] 9.6 Build progress display for multi-agent workflows
- [ ] 9.7 Write integration tests for multi-agent workflows

## 10. End-to-End Testing & Polish

- [ ] 10.1 Create configs for all 9 projects (test flows, Jira settings, ICE rules)
- [ ] 10.2 End-to-end test: Browser Test Agent → Evidence Gatherer → Jira comment
- [ ] 10.3 End-to-end test: Release prep pipeline (ICE check → doc generation → Jira update)
- [ ] 10.4 End-to-end test: PVT health check flow
- [ ] 10.5 Add README.md with setup instructions, project config guide, and usage examples
- [ ] 10.6 Add CLI help documentation for all commands
