# Work Buddy 🤖

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

## Mode Switching

```yaml
# configs/app.yaml
mode: mock   # Use mock services locally
mode: live   # Connect to real enterprise services
```
