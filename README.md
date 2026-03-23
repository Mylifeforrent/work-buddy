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

### Evidence Generation

Work Buddy captures comprehensive testing evidence including:

| Evidence Type | Description | Location |
|---------------|-------------|----------|
| **Screenshots** | PNG images at each test step | `evidence/*.png` |
| **Video Recordings** | WebM videos of test flows | `evidence/recordings/` |
| **GIF Previews** | Animated GIFs for easy sharing | `evidence/gifs/` |
| **Summary Reports** | HTML report aggregating all evidence | `evidence/evidence_summary.html` |

#### Video Recording Features

- **Visible Mouse Cursor**: Recordings show a cursor overlay that moves to each element before clicking, making it easy to follow the test flow
- **Click Animation**: Cursor changes color and size when clicking to highlight interactions
- **GIF Conversion**: Videos are automatically converted to GIF format for embedding in reports

#### Requirements for GIF Conversion

GIF conversion requires `ffmpeg`. Install it with:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

If ffmpeg is not installed, video recordings will still be generated (WebM format), but GIF conversion will be skipped.

#### Generating Evidence

```bash
# Run the evidence generator script
python3 scripts/generate_evidence.py
```

### Mock React UI

Work Buddy includes a realistic enterprise mock React UI built with Ant Design for testing browser automation. The mock UI simulates common enterprise application patterns.

#### Features

| Page | Description | Components Used |
|------|-------------|-----------------|
| **Login** | Authentication with any credentials | Form, Input, Button |
| **Dashboard** | Statistics, charts, recent activity | Cards, Statistic, List, Progress |
| **Data List** | Sortable table with row selection | Table, Tag, Button, Search |
| **Form** | Multi-field form with validation | Form, Input, TextArea |
| **Analytics** | Charts and metrics visualization | Bar charts, Progress, Descriptions |

#### UI Styling

- **Consistent Theming**: Uses Ant Design's ConfigProvider with custom theme tokens
- **Professional Appearance**: Shadows, gradients, hover effects, proper spacing
- **Visual Feedback**: Loading states, transition animations, hover highlights
- **Responsive Layout**: Collapsible sidebar, mobile-friendly design

#### Running the Mock UI

```bash
# Start the mock UI development server
cd mock_servers/ui
npm install
npm run dev
```

The mock UI will be available at `http://localhost:5173`. Use any username/password to log in.
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

# LLM Configuration
llm_provider: openai  # Options: openai, dashscope
llm_model: gpt-4o     # OpenAI: gpt-4o, gpt-4-turbo | Qwen: qwen-turbo, qwen-plus, qwen-max

# Mock server URLs (used when mode: mock)
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

# View PVT schedules
workbuddy pvt schedule

# View schedule for specific project
workbuddy pvt schedule --project payment-service

# Start the PVT scheduler daemon
workbuddy pvt start-scheduler

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

### Run All Tests

```bash
# Unit tests (fast, mocked dependencies)
pytest tests/unit -v

# Integration tests (mocked services)
pytest tests/integration -v

# E2E tests (requires mock services)
docker-compose up -d
pytest tests/e2e -v

# All tests with coverage
pytest tests/ -v --cov=src/work_buddy --cov-report=html
```

### Testing Individual Agents

Each agent has dedicated unit tests that can be run independently:

```bash
# Test browser automation agent
pytest tests/unit/test_browser_agent.py -v

# Test Jira task agent
pytest tests/unit/test_jira_agent.py -v

# Test ICE compliance agent
pytest tests/unit/test_ice_compliance.py -v

# Test release prep agent
pytest tests/unit/test_release_prep.py -v

# Test log analyst agent
pytest tests/unit/test_log_analyst.py -v

# Test Confluence RAG agent
pytest tests/unit/test_confluence_rag.py -v

# Test evidence gatherer
pytest tests/unit/test_evidence_gatherer.py -v
```

### Running with Different LLM Providers

Tests mock the LLM calls, so no API key is required for testing. However, to test with real LLM responses:

```bash
# With OpenAI
export OPENAI_API_KEY="your-key"
pytest tests/ -v -k "not mock"

# With Qwen/DashScope
export DASHSCOPE_API_KEY="your-key"
# Update configs/app.yaml to use llm_provider: dashscope
pytest tests/ -v -k "not mock"
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

Work Buddy supports multiple LLM providers. Set the appropriate environment variable based on your chosen provider:

### OpenAI (Default)

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

Configure in `configs/app.yaml`:
```yaml
llm_provider: openai
llm_model: gpt-4o  # or gpt-4-turbo, gpt-3.5-turbo
```

### DashScope / Qwen (Alibaba Cloud)

DashScope provides Qwen models with an OpenAI-compatible API.

```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

Configure in `configs/app.yaml`:
```yaml
llm_provider: dashscope
llm_model: qwen-plus  # or qwen-turbo, qwen-max
```

**Available Qwen Models:**
| Model | Description | Best For |
|-------|-------------|----------|
| `qwen-turbo` | Fast, cost-effective | Simple tasks, high volume |
| `qwen-plus` | Balanced performance | General purpose (recommended) |
| `qwen-max` | Most capable | Complex reasoning, analysis |

**Getting a DashScope API Key:**
1. Visit [DashScope Console](https://dashscope.console.aliyun.com/)
2. Create an account or sign in
3. Navigate to API Key Management
4. Create a new API key

### Switching Providers

Simply change the `llm_provider` and `llm_model` in `configs/app.yaml` and ensure the corresponding API key is set in your environment. The LLM factory will automatically configure the correct endpoint and authentication.

## Scheduled PVT (Post Verification Testing)

Work Buddy supports automated, cron-based PVT health checks. Configure scheduling per project to run automated health checks after maintenance windows or at regular intervals.

### Enable Scheduled PVT

Edit your project configuration (`configs/projects/<project>.yaml`):

```yaml
pvt_schedule:
  enabled: true  # Set to false to disable
  cron: "0 6 * * *"  # Run at 6 AM daily (cron expression)
  timezone: "Asia/Shanghai"  # Timezone for schedule execution
  notify:
    slack_channel: "#payment-alerts"  # Optional: Slack notifications
    jira_comment: true  # Optional: Post results as Jira comment
    email: "team@example.com"  # Optional: Email notifications
```

### Cron Expression Examples

| Expression | Description |
|------------|-------------|
| `0 6 * * *` | Daily at 6 AM |
| `*/30 * * * *` | Every 30 minutes |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 0 1 * *` | Monthly on the 1st at midnight |

### Managing the Scheduler

```bash
# View all project schedules
workbuddy pvt schedule

# View schedule for a specific project
workbuddy pvt schedule --project payment-service

# Start the scheduler daemon (runs in foreground)
workbuddy pvt start-scheduler

# Stop with Ctrl+C
```

### Scheduler Behavior

- The scheduler runs as a long-lived background process
- Each project with `enabled: true` gets its own scheduled task
- Timezone-aware execution ensures checks run at the correct local time
- On failure, errors are logged but the scheduler continues running
- Notifications (Slack, Jira, email) are best-effort and don't block execution

### Important Notes

- The scheduler is designed for development/testing convenience, not production-grade scheduling
- If the main process dies, scheduled tasks stop (no persistence)
- For production reliability, consider running under systemd or a process manager

## License

MIT License