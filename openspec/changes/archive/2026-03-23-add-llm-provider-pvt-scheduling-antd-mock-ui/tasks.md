## 1. LLM Provider Factory

- [x] 1.1 Create `src/work_buddy/core/llm.py` with `get_llm()` factory function
- [x] 1.2 Implement OpenAI provider branch with default configuration
- [x] 1.3 Implement DashScope provider branch with OpenAI-compatible endpoint
- [x] 1.4 Add `get_embeddings()` factory function for vector embeddings
- [x] 1.5 Add error handling for missing API keys with clear messages
- [x] 1.6 Update existing agents to use LLM factory instead of direct ChatOpenAI

## 2. PVT Scheduling

- [x] 2.1 Create `src/work_buddy/core/scheduler.py` with `PVTScheduler` class
- [x] 2.2 Add `PVTScheduleConfig` and `PVTNotifyConfig` to `config.py`
- [x] 2.3 Implement cron-based scheduling with `croniter` library
- [x] 2.4 Add timezone-aware execution support
- [x] 2.5 Add `pvt schedule` CLI command to view schedules
- [x] 2.6 Add `pvt start-scheduler` CLI command to run scheduler daemon
- [x] 2.7 Add `croniter` dependency to `pyproject.toml`
- [x] 2.8 Update project config example with `pvt_schedule` section

## 3. Evidence Summary Reports

- [x] 3.1 Add `generate_summary_report()` function to browser test agent
- [x] 3.2 Create HTML template with project/flow status and screenshots
- [x] 3.3 Integrate summary generation into test flow completion
- [x] 3.4 Update `scripts/generate_evidence.py` to use summary generation

## 4. Mock React UI with Ant Design

- [x] 4.1 Add `antd` and `@ant-design/icons` to `mock_servers/ui/package.json`
- [x] 4.2 Create `AuthContext` for session management
- [x] 4.3 Create `LoginPage` component with Ant Design Form
- [x] 4.4 Create `MainLayout` with Ant Design Sider and Header
- [x] 4.5 Create `DashboardPage` with Ant Design statistics and list
- [x] 4.6 Create `DataListPage` with Ant Design Table
- [x] 4.7 Create `FormPage` with Ant Design Form components
- [x] 4.8 Create `AnalyticsPage` with metrics visualization
- [x] 4.9 Implement protected routes with login status check
- [x] 4.10 Update `main.jsx` to use React Router for multi-page navigation

## 5. Testing and Documentation

- [x] 5.1 Update unit tests for LLM factory
- [x] 5.2 Update unit tests for scheduler module
- [x] 5.3 Update unit tests for browser test agent changes
- [x] 5.4 Update README with LLM provider configuration instructions
- [x] 5.5 Update README with scheduled PVT instructions
- [x] 5.6 Run all tests to verify no regressions