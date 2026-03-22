## Context

We manage 9 React web application projects across the full software development lifecycle. Each project cycle involves significant manual work for Jira management, testing evidence capture, ICE compliance validation, release documentation, Confluence search, PVT health checks, and production alert triage. These tasks follow predictable patterns but are multiplied across 9 projects, making them ideal candidates for agent-based automation.

The current state is fully manual — all Jira fields, testing evidence, compliance checks, and release documentation are prepared by hand. Production alert investigations require manual log correlation across Grafana, Prometheus, and OpenSearch.

**Constraints:**
- All 9 apps are React-based web applications
- Jira, Confluence, Grafana, Prometheus, and OpenSearch are the existing tools
- ICE (Internal Compliance Engine) standards must be followed precisely
- Agents must support per-project configuration (different URLs, auth, test flows)

## Goals / Non-Goals

**Goals:**
- Build a modular multi-agent system where each agent handles one SDLC phase
- Automate Jira task creation with correct tags, epics, sprints, and descriptions
- Automate browser-based testing and screenshot capture across 9 React apps
- Automate evidence gathering and Jira comment formatting for Dev/UAT/Regression/Performance tests
- Validate ICE compliance before production releases
- Generate release documentation (background, implementation steps, release notes, PVT steps, rollback steps)
- Enable RAG-powered search of Confluence documentation
- Automate PVT health checks and production alert triage
- Support per-project YAML configuration for all 9 apps
- Provide a phased delivery approach — start with highest-ROI agents, grow incrementally

**Non-Goals:**
- Replacing human judgment for critical release decisions — agents assist, humans approve
- Full end-to-end CI/CD pipeline management — agents integrate with existing pipelines, not replace them
- Building a production-grade SaaS product — this is an internal productivity tool
- Mobile app testing — scope is limited to web (React) applications
- Automated code generation or code review — scope is SDLC operations, not writing code

## Decisions

### 1. Agent Framework: LangGraph

**Decision**: Use LangGraph for agent orchestration.

**Rationale**: LangGraph provides a graph-based execution model well-suited for multi-agent workflows with inter-agent data dependencies (e.g., Browser Test Agent → Evidence Gatherer → ICE Compliance). It supports checkpointing, human-in-the-loop, and streaming — all useful for this use case.

**Alternatives considered**:
- *CrewAI*: Simpler but less control over execution flow; harder to model complex agent dependencies
- *AutoGen*: Good for conversations but overly focused on chat-based agent interaction vs. task orchestration
- *Custom*: Maximum control but significant effort to build orchestration, state management, and error handling

### 2. Browser Automation: Playwright

**Decision**: Use Playwright for all browser-based testing and screenshot capture.

**Rationale**: Playwright has excellent React support, handles SPAs with async rendering, provides built-in screenshot APIs, supports both headless and headful modes, and has a robust Python API. It can handle login flows, form interactions, and page waits natively.

**Alternatives considered**:
- *Selenium*: Mature but slower, more brittle with React SPAs
- *Puppeteer*: Good but Node.js only; we want a Python-native stack
- *Cypress*: Developer testing tool, not suitable for agent-driven automation

### 3. Per-Project Configuration: YAML Files

**Decision**: Use YAML configuration files per project to define test flows, Jira settings, URLs, and auth credentials.

**Rationale**: 9 projects × multiple configurations (test flows, Jira templates, PVT steps) requires a declarative, human-readable format. YAML is easy to maintain and version-control. Each project gets its own config directory.

### 4. LLM Usage: Targeted, Not Universal

**Decision**: Use LLM (OpenAI/Claude) only where reasoning is needed — release note generation, log analysis, document retrieval (RAG). Use deterministic logic for template-filling, validation, and browser automation.

**Rationale**: Most tasks (Jira field filling, compliance checking, screenshot capture) are rule-based and don't benefit from LLM reasoning. Using LLMs selectively reduces cost, latency, and unpredictability.

### 5. Phased Delivery

**Decision**: Deliver in 6 phases, starting with Browser Test Agent (highest ROI).

**Rationale**: The Browser Test Agent produces screenshots that feed into Evidence Gatherer and ICE Compliance — building it first creates the data pipeline for subsequent agents. Each phase builds on the previous one.

| Phase | Agent(s) | Depends On |
|---|---|---|
| 1 | Browser Test Agent + shared infra | — |
| 2 | Jira Task Agent + Evidence Gatherer | Phase 1 |
| 3 | ICE Compliance Agent | Phase 2 |
| 4 | Release Prep Agent | Phase 2-3 |
| 5 | Log Analyst + PVT Agent | Phase 1 |
| 6 | Confluence Doc Retriever (RAG) | — |

### 6. Interaction Model: CLI First

**Decision**: Start with a CLI interface, with optional web dashboard later.

**Rationale**: CLI is fastest to build, works in terminal workflows, and is easy to script. A web dashboard can be added in a later phase for visualization (test reports, compliance dashboards).

## Risks / Trade-offs

- **Jira API rate limits** → Implement request batching and caching. Monitor usage patterns.
- **Auth credential management for 9 apps** → Use a secure local credential store (e.g., keyring or .env with restricted permissions). Never hardcode credentials.
- **React SPA rendering timing** → Playwright's `wait_for_selector` and `network_idle` mitigate this, but some apps may need custom wait strategies.
- **ICE standard changes** → ICE rules should be externalized in config, not hardcoded. When standards change, update config, not code.
- **LLM output quality for release notes** → Always present generated content for human review before posting to Jira. Never auto-post LLM-generated content.
- **Maintenance burden of 9 project configs** → Provide config validation tooling and templates to minimize drift.
- **Scope creep** → Phased delivery with clear boundaries per phase. Each phase has a defined "done" state.
