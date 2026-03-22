# Contributing to Work Buddy

This guide covers how to extend Work Buddy, particularly adding real adapters for production services.

## Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd work-buddy
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install

# Start mock services for testing
docker-compose up -d
```

## Architecture Overview

Work Buddy uses **hexagonal architecture** (ports & adapters):

1. **Service Interfaces (Ports)**: Abstract base classes in `src/work_buddy/services/`
2. **Adapters**: Concrete implementations in `src/work_buddy/adapters/`
   - `mock/`: Mock adapters for local development
   - `real/`: Real adapters for production services

Agents depend only on service interfaces, never on concrete implementations.

## Adding a Real Adapter

### Step 1: Choose the Service Interface

Review the service interface in `src/work_buddy/services/`:

```python
# services/jira_service.py
class JiraService(ABC):
    @abstractmethod
    async def create_task(self, project_key: str, summary: str, ...) -> JiraTicket:
        ...

    @abstractmethod
    async def get_ticket(self, ticket_key: str) -> JiraTicket:
        ...
```

### Step 2: Implement the Adapter

Create `src/work_buddy/adapters/real/real_jira.py`:

```python
from typing import Optional, List
import httpx

from work_buddy.services.jira_service import JiraService, JiraTicket

class RealJiraAdapter(JiraService):
    """Real Jira adapter connecting to enterprise Jira instance."""

    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    async def create_task(
        self,
        project_key: str,
        summary: str,
        description: str = "",
        ticket_type: str = "Task",
        **kwargs
    ) -> JiraTicket:
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": ticket_type},
            }
        }

        # Add optional fields
        if kwargs.get("epic_link"):
            payload["fields"]["customfield_10000"] = kwargs["epic_link"]
        if kwargs.get("labels"):
            payload["fields"]["labels"] = kwargs["labels"]
        if kwargs.get("components"):
            payload["fields"]["components"] = [{"name": c} for c in kwargs["components"]]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rest/api/2/issue",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

        return JiraTicket(
            key=data["key"],
            summary=summary,
            description=description,
            labels=kwargs.get("labels", []),
            status="Open",
            project=project_key,
            epic_link=kwargs.get("epic_link"),
            custom_fields={}
        )

    async def get_ticket(self, ticket_key: str) -> JiraTicket:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/rest/api/2/issue/{ticket_key}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

        fields = data["fields"]
        return JiraTicket(
            key=data["key"],
            summary=fields.get("summary", ""),
            description=fields.get("description", ""),
            labels=fields.get("labels", []),
            status=fields.get("status", {}).get("name", "Unknown"),
            project=fields.get("project", {}).get("key", ""),
            epic_link=fields.get("customfield_10000"),
            custom_fields={}
        )

    # Implement remaining abstract methods...
```

### Step 3: Update the Container

Edit `src/work_buddy/core/container.py`:

```python
@property
def jira_service(self):
    if self._jira_service is None:
        if self.config.mode == "mock":
            from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
            self._jira_service = MockJiraAdapter(base_url=self.config.mock_jira_url)
        else:
            from work_buddy.adapters.real.real_jira import RealJiraAdapter
            # Get credentials from credential store or environment
            import os
            self._jira_service = RealJiraAdapter(
                base_url=os.environ.get("JIRA_URL"),
                api_token=os.environ.get("JIRA_API_TOKEN")
            )
    return self._jira_service
```

### Step 4: Add Configuration

Update `configs/app.yaml`:

```yaml
mode: live

# Production URLs
jira_url: "${JIRA_URL}"
confluence_url: "${CONFLUENCE_URL}"
```

### Step 5: Write Tests

Add tests in `tests/unit/test_real_jira.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from work_buddy.adapters.real.real_jira import RealJiraAdapter

@pytest.fixture
def adapter():
    return RealJiraAdapter(
        base_url="https://jira.example.com",
        api_token="test-token"
    )

@pytest.mark.asyncio
async def test_create_task(adapter):
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "TEST-123"}
        mock_response.raise_for_status = MagicMock()

        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_context)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_context.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_context

        ticket = await adapter.create_task(
            project_key="TEST",
            summary="Test Task",
            description="Test description"
        )

        assert ticket.key == "TEST-123"
        assert ticket.summary == "Test Task"
```

## Real Adapter Guidelines

### Authentication

- Use the `CredentialStore` service for retrieving credentials
- Support environment variables for local development
- Never hardcode credentials

```python
async def _get_auth_headers(self) -> dict:
    creds = await self.credential_store.get_credentials("jira")
    return {"Authorization": f"Bearer {creds.token}"}
```

### Error Handling

- Raise appropriate exceptions for API errors
- Log errors with context
- Handle rate limiting gracefully

```python
async def get_ticket(self, ticket_key: str) -> JiraTicket:
    try:
        response = await self._request("GET", f"/issue/{ticket_key}")
        return self._parse_ticket(response)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise TicketNotFoundError(f"Ticket {ticket_key} not found")
        raise
```

### Rate Limiting

For services with rate limits:

```python
import asyncio

class RealJiraAdapter(JiraService):
    def __init__(self, ...):
        self._rate_limiter = asyncio.Semaphore(10)  # Max 10 concurrent

    async def _request(self, method: str, path: str, **kwargs):
        async with self._rate_limiter:
            # Make request
            pass
```

## Adding a New Service Interface

1. Create the ABC in `src/work_buddy/services/`:

```python
# services/my_service.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class MyData:
    id: str
    name: str

class MyService(ABC):
    @abstractmethod
    async def get_data(self, id: str) -> MyData:
        ...

    @abstractmethod
    async def list_data(self) -> list[MyData]:
        ...
```

2. Create mock adapter:

```python
# adapters/mock/mock_my_service.py
from work_buddy.services.my_service import MyService, MyData

class MockMyService(MyService):
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url

    async def get_data(self, id: str) -> MyData:
        # Call mock server
        pass

    async def list_data(self) -> list[MyData]:
        # Call mock server
        pass
```

3. Create real adapter stub:

```python
# adapters/real/real_my_service.py
from work_buddy.services.my_service import MyService, MyData

class RealMyService(MyService):
    """TODO: Implement real adapter for MyService."""

    async def get_data(self, id: str) -> MyData:
        raise NotImplementedError("Real adapter not yet implemented")

    async def list_data(self) -> list[MyData]:
        raise NotImplementedError("Real adapter not yet implemented")
```

4. Register in container:

```python
@property
def my_service(self):
    if self._my_service is None:
        if self.config.mode == "mock":
            from work_buddy.adapters.mock.mock_my_service import MockMyService
            self._my_service = MockMyService()
        else:
            from work_buddy.adapters.real.real_my_service import RealMyService
            self._my_service = RealMyService()
    return self._my_service
```

## Adding a New Agent

1. Create the agent in `src/work_buddy/agents/`:

```python
# agents/my_agent.py
from work_buddy.services.jira_service import JiraService

class MyAgent:
    def __init__(self, jira: JiraService):
        self.jira = jira

    async def do_something(self, ticket_key: str) -> dict:
        ticket = await self.jira.get_ticket(ticket_key)
        # Agent logic here
        return {"result": "done"}
```

2. Register in the coordinator:

```python
# agents/coordinator.py
@property
def my_agent(self):
    if self._my_agent is None:
        from work_buddy.agents.my_agent import MyAgent
        self._my_agent = MyAgent(jira=self.container.jira_service)
    return self._my_agent
```

3. Add CLI command:

```python
# cli/main.py
@my_app.command("action")
def my_action(
    ticket: str = typer.Option(..., "--ticket", "-t")
):
    coordinator.execute("my_action", ticket=ticket)
```

4. Write tests:

```python
# tests/unit/test_my_agent.py
import pytest
from unittest.mock import AsyncMock

from work_buddy.agents.my_agent import MyAgent

@pytest.fixture
def agent():
    jira_mock = AsyncMock()
    return MyAgent(jira=jira_mock)

@pytest.mark.asyncio
async def test_do_something(agent):
    result = await agent.do_something("TEST-123")
    assert result["result"] == "done"
```

## Code Style

- Use type hints for all function signatures
- Write docstrings for public methods
- Follow PEP 8 conventions
- Use `async` for all service methods (even if not strictly needed)
- Keep agents stateless where possible

## Pull Request Process

1. Create a feature branch from `main`
2. Make changes with tests
3. Run tests: `pytest tests/`
4. Update documentation if needed
5. Submit PR with description of changes

## Questions?

Open an issue for discussion before major changes.