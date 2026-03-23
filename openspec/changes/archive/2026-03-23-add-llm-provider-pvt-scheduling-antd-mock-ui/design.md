## Context

Work Buddy currently uses a hardcoded OpenAI LLM integration. Users with different LLM preferences (e.g., DashScope/Qwen for Chinese users) cannot use the system without code changes. Additionally, PVT health checks are manually triggered, requiring operational overhead for scheduled maintenance windows. The mock UI testing infrastructure lacks realistic enterprise UI components and authentication flows.

**Current State:**
- Single LLM provider (OpenAI) hardcoded in agents
- No scheduled execution for PVT
- Mock UI uses custom styling without proper authentication simulation

**Constraints:**
- Must support OpenAI-compatible API endpoints for provider flexibility
- Scheduling must be timezone-aware for global teams
- UI must simulate realistic enterprise authentication

## Goals / Non-Goals

**Goals:**
- Enable seamless LLM provider switching via configuration
- Provide cron-based PVT scheduling with per-project enable/disable
- Generate HTML evidence summaries for test reporting
- Simulate realistic enterprise UI with Ant Design and login flows

**Non-Goals:**
- Real-time alerting system (notification is best-effort)
- Production-grade scheduler (this is for development/testing convenience)
- Support for non-OpenAI-compatible LLM APIs

## Decisions

### D1: LLM Factory Pattern
**Decision:** Use a factory function (`get_llm()`, `get_embeddings()`) that returns LangChain's `ChatOpenAI` / `OpenAIEmbeddings` instances configured for the selected provider.

**Rationale:**
- DashScope provides an OpenAI-compatible API endpoint
- Factory pattern allows zero-code-change provider switching
- LangChain's abstractions already handle provider differences

**Alternatives Considered:**
- Provider-specific client classes: More code, harder to maintain
- Direct API calls: Lose LangChain tool integration benefits

### D2: Cron-based Scheduling with Asyncio
**Decision:** Implement scheduler using `croniter` for parsing and `asyncio` for execution, running as a long-lived background task.

**Rationale:**
- Lightweight, no external dependencies (Redis, Celery)
- Fits the development/testing use case
- Per-project enable/disable via YAML config

**Alternatives Considered:**
- External scheduler (cron, systemd): Requires system configuration
- Celery/Redis: Overkill for this use case, adds deployment complexity

### D3: Ant Design for Mock UI
**Decision:** Rewrite mock React UI using Ant Design components with multiple test pages and authentication context.

**Rationale:**
- Ant Design is widely used in enterprise applications
- Provides realistic form, table, and layout components
- Authentication context enables proper login flow testing

**Alternatives Considered:**
- Custom CSS: Less realistic, doesn't test real component interactions
- Material UI: Different design language than typical enterprise apps

### D4: Session-based Mock Authentication
**Decision:** Use `sessionStorage` to persist mock login state, with React Context for auth state management.

**Rationale:**
- Simple implementation for testing purposes
- Session cleared on browser close (appropriate for testing)
- React Context pattern matches real-world implementations

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Scheduler stops if main process dies | Document as development tool, not production scheduler |
| API key exposure in logs | Never log API keys, use environment variables only |
| Mock UI drift from real UI patterns | Document as testing scaffold, not production UI template |
| Cron timezone confusion | Default to project-configured timezone, show in status |

## Migration Plan

1. **Phase 1:** Add LLM factory (no breaking changes, backward compatible with OpenAI default)
2. **Phase 2:** Add scheduler module (opt-in via project config)
3. **Phase 3:** Update mock UI (existing mock servers continue to work)

**Rollback:** All changes are additive. Disable via config:
- `llm_provider: openai` (default)
- `pvt_schedule.enabled: false` (default)