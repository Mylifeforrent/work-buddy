# Work Buddy

Multi-agent system for automating SDLC workflows — Jira tasks, testing evidence, compliance validation, release prep, and production support.

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Start mock services
docker compose up -d

# Run CLI
workbuddy status
workbuddy test run --project user-portal --type regression
workbuddy jira create --project payment-service --requirement "Add caching layer"
workbuddy compliance check --ticket PAY-1234
```

## Architecture

Work Buddy follows a **hexagonal architecture** (ports & adapters) pattern:

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
│   (FastAPI)          │     ┌────────────────────┐               │
│                      │     │ Direct API Clients  │               │
│                      │     ├────────────────────┤               │
│                      │     │ MCP Client Adapter  │               │
│                      │     │ (MCP Server ↔ Tool) │               │
│                      │     └────────────────────┘               │
└──────────────────────┴──────────────────────────────────────────┘
```

### Project Structure

```
src/work_buddy/
├── agents/          # Agent implementations (LangGraph)
├── core/            # Config, logging, DI container
├── services/        # Service interfaces (ABCs / ports)
├── adapters/
│   ├── mock/        # Mock adapters → mock servers
│   └── real/        # Real adapters → enterprise services (stubs)
└── cli/             # Typer CLI entry points

mock_servers/        # FastAPI mock services (Docker)
configs/
├── app.yaml         # Global config (mode: mock/live)
├── ice_rules.yaml   # ICE compliance rules
└── projects/        # Per-project YAML configs
```

### Agents

| Agent | Description |
|-------|-------------|
| **Jira Task Agent** | Automated task creation with templates and field population |
| **Evidence Gatherer** | Collects test evidence and posts to Jira |
| **Browser Test Agent** | Playwright-based UI testing, screenshot capture, video recording & GIF conversion |
| **ICE Compliance Agent** | Validates tickets against compliance rules |
| **Release Prep Agent** | Generates release notes, rollback steps, PVT steps |
| **Confluence RAG Agent** | Semantic search and summarization of documentation |
| **Log Analyst Agent** | Alert triage and PVT health checks |
| **Coordinator** | LangGraph-based orchestrator for multi-agent workflows |

## Configuration

### Global Config (`configs/app.yaml`)

```yaml
mode: mock  # Switch to "live" for production
log_level: INFO
llm_model: gpt-4o

mock_jira_url: "http://localhost:8081"
mock_confluence_url: "http://localhost:8082"
mock_sso_url: "http://localhost:8090"
```

### Project Config (`configs/projects/<project>.yaml`)

```yaml
name: "Payment Service"
type: backend  # or "react-app"

jira:
  project_key: "PAY"
  epic: "PAY-200"
  labels: ["payment", "backend"]
  components: ["API", "Database"]

tool_urls:
  opensearch: "http://localhost:9200"
  springboot_admin: "http://localhost:9300"
  grafana: "http://localhost:3001"

evidence_checks:
  opensearch:
    - name: "Error Logs"
      query: "service:payment AND level:ERROR"
```

## Mode Switching

```yaml
# configs/app.yaml
mode: mock   # Use mock services locally
mode: live   # Connect to real enterprise services
```

When switching to `live`, implement real adapters in `src/work_buddy/adapters/real/`.

## CLI Commands

```bash
# Show status
workbuddy status

# Run browser tests
workbuddy test run --project payment-service --type regression

# Create Jira task
workbuddy jira create --project payment-service --requirement "Add caching layer"

# Check ICE compliance
workbuddy compliance check --ticket PAY-1234

# Prepare release documentation
workbuddy release prepare --ticket PAY-1234 --repo ./ --since v1.0.0

# Run PVT health check
workbuddy pvt run --project payment-service

# Search Confluence docs
workbuddy docs search "deployment process"

# Summarize a Confluence page
workbuddy docs summarize <page-id>

# Triage alert
workbuddy alert triage --service payment-service --alert "High error rate"
```

## Multi-Agent Workflows

The coordinator orchestrates complex workflows:

```
Release Prep Workflow:
  1. ICE Compliance Check → 2. Generate Docs → 3. Human Confirmation → 4. Update Jira

Evidence Flow:
  1. Browser Test Agent → 2. Evidence Gatherer → 3. Jira Comment
```

## Testing

```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# E2E tests (requires mock services)
docker-compose up -d
pytest tests/e2e -v
```

## Switching to Production

1. Update `configs/app.yaml`:

```yaml
mode: live
```

2. Implement real adapters in `src/work_buddy/adapters/real/`:
   - `real_jira.py` - Connect to your Jira instance
   - `real_confluence.py` - Connect to your Confluence
   - `real_opensearch.py` - Connect to your OpenSearch
   - etc.

3. Update tool URLs in project configs to production endpoints

4. Set up authentication:
   - SSO: Implement `real_sso.py` for your corporate SSO
   - Credentials: Implement `real_credentials.py` for your secret store

## Environment Variables

```bash
export OPENAI_API_KEY="your-api-key"
```

## License

MIT License