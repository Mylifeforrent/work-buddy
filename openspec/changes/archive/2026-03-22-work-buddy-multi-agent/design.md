## Context

We manage 13+ applications: 3 React web apps with browser UIs and 10+ backend services exposing APIs only. Each project cycle involves significant manual effort for Jira management, testing evidence capture (screenshots from OpenSearch, SpringBoot Admin, Grafana dashboards), ICE compliance validation, release documentation, Confluence search, PVT health checks, and production alert triage.

All external tools (Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin) use Corporate SSO for authentication, with **no session sharing** between tools — each requires a separate SSO login flow.

This system will be built as an **enterprise-grade reference architecture** with mocked external services, enabling fully local execution. The architecture must allow seamless swapping from mock to real implementations via configuration.

**Constraints:**
- 3 React web apps (browser UI testing) + 10+ backend API services (dashboard-based evidence)
- Testing evidence for backend services = screenshots from OpenSearch logs, SpringBoot Admin R2DB status, Grafana metrics
- Corporate SSO authentication, separate login per tool, no session sharing
- Only some services share the same OpenSearch/SpringBoot Admin/Grafana instances — per-project tool URL mapping required
- Must run fully locally with mock services via Docker Compose
- Must be designed as enterprise-grade reference, not a toy demo

## Goals / Non-Goals

**Goals:**
- Build a modular multi-agent system with clean hexagonal architecture (ports & adapters)
- All external dependencies abstracted behind service interfaces (Python ABCs)
- Complete mock implementations for every external service (Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin, SSO)
- Docker Compose setup for one-command local dev environment
- Switch between mock and real implementations via a single config flag
- Per-project YAML config supporting different tool instance URLs, keywords, and test flows
- Automate browser-based screenshot capture for both React app UIs and monitoring dashboards
- Handle corporate SSO with per-tool separate authentication flows
- CLI-first interaction with enterprise patterns (logging, tracing, error handling)
- Phased delivery starting with highest-ROI components

**Non-Goals:**
- Replacing human judgment for critical release decisions — agents assist, humans approve
- Full end-to-end CI/CD pipeline management — agents integrate with existing pipelines
- Building a production-grade SaaS product — this is an internal productivity reference architecture
- Mobile app testing — scope is web UIs and API services only
- Automated code generation or code review — scope is SDLC operations
- Implementing real integrations — mock layer only, user swaps in real implementations

## Decisions

### 1. Architecture: Hexagonal (Ports & Adapters)

**Decision**: Use hexagonal architecture with service interfaces as ports and mock/real implementations as adapters.

**Rationale**: The core requirement is to run fully locally with mocks but be swappable to real services. Hexagonal architecture is the textbook pattern for this — agents depend on abstract interfaces, never on concrete implementations. Dependency injection selects mock or real adapters based on configuration.

```
Agents → Service Interfaces (ABCs) → Mock Adapters (local)
                                    → Real Adapters (production)
```

**Alternatives considered**:
- *Direct API calls with feature flags*: Simpler but couples agents to specific implementations, harder to test
- *Plugin architecture*: More flexible but over-engineered for the known set of services

### 2. Agent Framework: LangGraph

**Decision**: Use LangGraph for agent orchestration.

**Rationale**: LangGraph provides a graph-based execution model well-suited for multi-agent workflows with inter-agent data dependencies (e.g., Browser Test Agent → Evidence Gatherer → ICE Compliance). Supports checkpointing, human-in-the-loop, and streaming.

**Alternatives considered**:
- *CrewAI*: Simpler but less control over execution flow; harder to model complex agent dependencies
- *AutoGen*: Good for conversations but overly focused on chat-based agent interaction vs. task orchestration
- *Custom*: Maximum control but significant effort to build orchestration, state management, and error handling

### 3. Browser Automation: Playwright

**Decision**: Use Playwright for all browser-based screenshot capture — both React app UIs and monitoring dashboards (OpenSearch, SpringBoot Admin, Grafana).

**Rationale**: Playwright handles SPAs, SSO redirects, form logins, and provides built-in screenshot APIs. It can automate OpenSearch searches (type query, wait for results, screenshot) and SpringBoot Admin navigation (find service, check R2DB status, screenshot) just as easily as React app pages.

**Alternatives considered**:
- *Selenium*: Mature but slower, more brittle with modern SPAs
- *Direct API calls for monitoring tools*: Faster but doesn't produce screenshots (which are required as Jira evidence)

### 4. Mock Services: FastAPI-Based Mock Servers

**Decision**: Implement mock services as FastAPI applications, each providing realistic API responses and (where applicable) a minimal web UI for browser-based screenshot capture.

**Mock services needed:**

| Mock | What It Simulates | Web UI Needed? |
|---|---|---|
| Mock Jira | REST API for tasks, comments, attachments, labels | No (API only) |
| Mock Confluence | REST API for page search and retrieval | No (API only) |
| Mock OpenSearch | Log search API + minimal Dashboards UI for screenshots | **Yes** |
| Mock Grafana | Metrics API + minimal dashboard UI for screenshots | **Yes** |
| Mock SpringBoot Admin | Minimal web UI showing services with R2DB status | **Yes** |
| Mock SSO | Simple login form that issues session cookies | **Yes** |

**Rationale**: Mock services with web UIs allow end-to-end testing of the screenshot capture workflow locally. FastAPI is lightweight, fast, and supports both REST APIs and HTML rendering (via Jinja2).

### 5. Per-Project Configuration with Tool Instance Mapping

**Decision**: Each project has a YAML config file specifying its tool instance URLs, since not all services share the same OpenSearch/Grafana/SpringBoot Admin instances.

```yaml
# Example: payment-service.yaml
name: "Payment Service"
type: "backend"             # backend | react-app
jira:
  project_key: "PAY"
  epic: "PAY-100"
  labels: ["payment", "backend"]
tool_urls:
  opensearch: "http://localhost:9201"      # Mock OpenSearch instance A
  springboot_admin: "http://localhost:9301" # Mock SpringBoot Admin A
  grafana: "http://localhost:3001"          # Mock Grafana instance A
evidence_checks:
  opensearch:
    - name: "Business Logs"
      query: "service:payment AND message:*transaction*"
    - name: "Error Check"
      query: "service:payment AND level:ERROR"
  springboot_admin:
    - service_name: "payment-service"
      check: "r2db_status"
      expected: "UP"
```

### 6. SSO Authentication Abstraction

**Decision**: Create an SSO handler abstraction that supports per-tool authentication (no session sharing). Mock SSO accepts any staffid/password. Real SSO handles corporate SSO redirects.

**Rationale**: User confirmed each tool requires separate SSO login. The abstraction must handle: detect SSO redirect → navigate to login page → enter credentials → handle possible MFA prompt → return to tool. In mock mode, this is a simple form submission.

### 7. Interaction Model: CLI First (Typer)

**Decision**: Use Typer for CLI with structured commands per agent capability.

```bash
workbuddy test --project payment-service --type regression
workbuddy jira create --project payment-service --requirement "Add caching layer"
workbuddy compliance check --ticket PAY-1234
workbuddy release prepare --ticket PAY-1234
workbuddy pvt run --project payment-service
workbuddy docs search "payment API specification"
workbuddy alert triage --service payment-service
```

### 8. Docker Compose for Local Dev

**Decision**: Provide a Docker Compose file that starts all mock services with a single command.

```yaml
# docker-compose.yml starts:
# - Mock Jira (port 8081)
# - Mock Confluence (port 8082)
# - Mock OpenSearch with Dashboards UI (port 9200/9201)
# - Mock Grafana (port 3000/3001)
# - Mock SpringBoot Admin (port 9300/9301)
# - Mock SSO (port 8090)
```

## Risks / Trade-offs

- **Mock fidelity** → Mocks must be realistic enough to validate agent logic, but don't need to replicate every API quirk. Focus on the endpoints agents actually use.
- **Corporate SSO complexity** → Real SSO may involve MFA, SAML, OAuth2 redirects. Mock SSO simplifies this. When switching to real SSO, may need per-organization customization.
- **Screenshot-based evidence** → Screenshots are inherently fragile (UI changes break selectors). Use resilient selectors and configurable wait strategies.
- **10+ project configs** → Maintaining YAML configs for 13+ projects requires discipline. Provide config validation tooling and templates.
- **LLM output quality for release notes** → Always present generated content for human review before posting to Jira.
- **Multiple monitoring tool instances** → Projects mapping to different tool URLs adds configuration complexity. Validate configs at startup.
- **Docker resource usage** → Running 6+ mock services locally requires reasonable system resources. Keep mock servers lightweight.
- **Video recording storage** → WebM videos + GIF conversions increase storage requirements. Implement cleanup policies for old evidence.
- **ffmpeg dependency** → GIF conversion requires ffmpeg installed on the host. Document this as a prerequisite; provide graceful fallback (video-only) if not available.
- **MCP server availability** → MCP integration adds dependency on MCP server implementations. If MCP server is unavailable, fall back to direct adapter pattern.

## Architecture Diagram (V2 — with MCP & Video Recording)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI (Typer)                              │
├─────────────────────────────────────────────────────────────────┤
│                Agent Coordinator (LangGraph)                     │
├────────┬─────────┬──────────┬─────────┬──────────┬─────────────┤
│ Jira   │Evidence │  ICE     │ Release │Confluence│ Log Analyst │
│ Task   │Gatherer │Compliance│  Prep   │ RAG      │ & PVT       │
│ Agent  │ Agent   │  Agent   │  Agent  │  Agent   │   Agent     │
├────────┴─────────┴──────────┴─────────┴──────────┴─────────────┤
│            Browser Test Agent  ──┬── Screenshots (PNG)          │
│                                  ├── Video Recording (WebM)     │
│                                  └── GIF Previews (ffmpeg)      │
├─────────────────────────────────────────────────────────────────┤
│                   Service Interfaces (ABCs)                      │
├──────────────────────┬──────────────────────────────────────────┤
│   Mock Adapters      │          Real Adapters                    │
│   (FastAPI in-proc)  │     ┌────────────────────┐               │
│                      │     │ Direct API Clients  │               │
│                      │     ├────────────────────┤               │
│                      │     │ MCP Client Adapter  │  ← NEW       │
│                      │     │ (MCP Server ↔ Tool) │               │
│                      │     └────────────────────┘               │
└──────────────────────┴──────────────────────────────────────────┘

MCP Integration (alternative transport):
┌──────────────┐     MCP Protocol     ┌──────────────────────┐
│  Work Buddy  │─────────────────────▶│  MCP Server: Jira    │
│  Agent       │    tools/resources   ├──────────────────────┤
│              │─────────────────────▶│  MCP Server: Conflu  │
│              │─────────────────────▶│  MCP Server: Search  │
│              │─────────────────────▶│  MCP Server: Grafana │
└──────────────┘                      └──────────────────────┘

Skills (composable capabilities):
┌─────────────────────────────────────────────────────┐
│  Skills Layer (reusable, declarative capabilities)   │
├─────────────────────────────────────────────────────┤
│  screenshot-and-upload  │  Capture + attach to Jira │
│  sso-login-flow         │  SSO auth for any tool    │
│  evidence-package       │  Screenshots → Package    │
│  video-record-flow      │  Record + convert to GIF  │
│  log-keyword-search     │  OpenSearch query + proof │
└─────────────────────────────────────────────────────┘
```

### 9. MCP as Service Transport

**Decision**: Support MCP (Model Context Protocol) as an alternative transport for accessing external services. Each external tool (Jira, Confluence, OpenSearch, Grafana, SpringBoot Admin) can be fronted by an MCP server that exposes the service's capabilities as MCP tools and resources.

**Rationale**: MCP enables AI coding assistants (Claude Code, Gemini CLI, etc.) to directly invoke Work Buddy capabilities. Instead of only the CLI, any MCP-compatible client can call `jira.create_task`, `confluence.search`, `opensearch.query` etc. This makes the system composable in the broader AI tooling ecosystem.

**Architecture**: MCP servers sit alongside the existing adapter pattern — both are valid ways to reach external services:
- **Direct Adapter** (existing): Agent → ABC → MockAdapter/RealAdapter → Service
- **MCP Adapter** (new): Agent → ABC → MCPClientAdapter → MCP Server → Service

The hexagonal architecture already supports this naturally — the MCP client adapter is just another implementation of the service ABC.

### 10. Video/GIF Evidence Recording

**Decision**: Add video recording (WebM) and GIF conversion to the browser evidence capture pipeline using Playwright's native video recording and ffmpeg.

**Rationale**: Static screenshots capture point-in-time state, but video recordings capture the entire agent workflow — navigation, SSO login, search queries, page transitions. This is critical for:
- **Verification**: Reviewing whether the AI agent followed the correct pathway
- **Debugging**: Understanding failures in multi-step browser flows
- **Evidence**: Richer evidence for Jira comments (GIF previews + full video links)

**Implementation**:
- Playwright's `record_video_dir` on `BrowserContext` for zero-overhead WebM capture
- `ffmpeg` subprocess for WebM → GIF conversion (configurable FPS, scale)
- `EvidencePackage` extended with `recordings` (WebM) and `gifs` (GIF) fields
- Graceful fallback: if ffmpeg is unavailable, skip GIF conversion, keep video only
