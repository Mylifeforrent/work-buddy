import pytest
import datetime
from unittest.mock import patch, MagicMock

from work_buddy.agents.jira_task_agent import JiraTaskAgent
from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
from work_buddy.core.config import ProjectConfig, JiraConfig

@pytest.fixture
def mock_jira():
    return MockJiraAdapter(base_url="http://fake")

@pytest.fixture
def agent(mock_jira):
    return JiraTaskAgent(jira_service=mock_jira)

@pytest.mark.asyncio
@patch("work_buddy.agents.jira_task_agent.load_project_config")
async def test_bulk_create_with_template_and_defaults(mock_load_config, agent, mock_jira):
    # Setup mock project config
    mock_load_config.return_value = ProjectConfig(
        name="testproj",
        type="backend",
        jira=JiraConfig(
            project_key="TEST",
            epic="TEST-1",
            labels=["backend", "auto-generated"],
            components=["API"],
            description_template="**Context:**\\n{{ description }}\\n\\n*Priority:* {{ requirement.priority }}"
        )
    )
    
    # Needs to mock the httpx calls in MockJiraAdapter or we use an AsyncMock for the adapter
    # Wait, MockJiraAdapter itself uses httpx. Let's just mock the adapter methods entirely.
    mock_jira.create_task = AsyncMock()
    mock_ticket = MagicMock()
    mock_jira.create_task.return_value = mock_ticket
    
    reqs = [
        {"summary": "Task 1", "description": "Do something", "priority": "High"},
        {"summary": "Task 2", "description": "Do another thing", "priority": "Low", "labels": ["extra"]}
    ]
    
    tickets = await agent.create_tasks_from_requirements("testproj", reqs)
    
    assert len(tickets) == 2
    assert mock_jira.create_task.call_count == 2
    
    # Check populated fields for first task
    call_args_1 = mock_jira.create_task.call_args_list[0][1]
    assert call_args_1["project_key"] == "TEST"
    assert call_args_1["epic_link"] == "TEST-1"
    assert "backend" in call_args_1["labels"]
    assert "API" in call_args_1["components"]
    assert "**Context:**\\nDo something\\n\\n*Priority:* High" in call_args_1["description"]
    
    # Check labels merged for second task
    call_args_2 = mock_jira.create_task.call_args_list[1][1]
    assert "extra" in call_args_2["labels"]
    assert "backend" in call_args_2["labels"]

@pytest.mark.asyncio
async def test_validation_unknown_project(agent):
    with pytest.raises(ValueError, match="Unknown project name"):
        await agent.create_tasks_from_requirements("nonexistent", [])

# Utility class to mock async functions cleanly if needed
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
