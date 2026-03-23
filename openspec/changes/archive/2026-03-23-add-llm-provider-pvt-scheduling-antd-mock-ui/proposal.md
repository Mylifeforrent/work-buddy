## Why

Work Buddy needs to support multiple LLM providers (OpenAI, DashScope/Qwen) to enable users to choose their preferred AI backend. Additionally, the system needs automated PVT scheduling with enable/disable switches for operational flexibility, and the mock React UI must be enhanced with Ant Design for realistic enterprise testing scenarios with proper login authentication flow.

## What Changes

- Add multi-provider LLM support via factory pattern (OpenAI, DashScope/Qwen)
- Generate HTML evidence summary reports after test execution
- Add cron-based scheduled PVT execution with enable/disable configuration per project
- Update mock React UI to use Ant Design components
- Add multiple test pages to mock UI (Dashboard, Data List, Form, Analytics)
- Implement login status check before UI testing

## Capabilities

### New Capabilities
- `llm-provider`: Multi-provider LLM factory supporting OpenAI and DashScope/Qwen with configurable model selection and environment-based authentication

### Modified Capabilities
- `browser-test-agent`: Add evidence summary HTML generation, Ant Design mock UI requirements, multiple test pages, and login status verification
- `log-analysis-and-pvt`: Add cron-based scheduled PVT execution with enable/disable switch, timezone support, and notification configuration

## Impact

- **Core**: New `llm.py` factory, new `scheduler.py` for PVT scheduling
- **Config**: New `PVTScheduleConfig` and `PVTNotifyConfig` models in `config.py`
- **CLI**: New `pvt schedule` and `pvt start-scheduler` commands
- **Dependencies**: Add `croniter` for cron parsing
- **Mock UI**: Rewrite with Ant Design, add authentication context and protected routes
- **Project Configs**: Add `pvt_schedule` section with enable/disable switch