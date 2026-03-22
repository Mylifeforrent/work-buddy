import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.messages import AIMessage

from work_buddy.agents.release_prep_agent import ReleasePrepAgent
from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
from work_buddy.agents.ice_compliance_agent import IceComplianceAgent
from work_buddy.services.jira_service import JiraTicket
from work_buddy.core.config import AppConfig

@pytest.fixture
def mock_jira():
    return MockJiraAdapter(base_url="http://fake")

@pytest.fixture
def mock_compliance():
    agent = AsyncMock(spec=IceComplianceAgent)
    agent.validate_ticket.return_value = (True, [])
    return agent

@pytest.fixture
@patch("work_buddy.agents.release_prep_agent.load_app_config")
def agent(mock_load_config, mock_jira, mock_compliance):
    mock_load_config.return_value = AppConfig(mode="mock", llm_model="gpt-3.5-mock")
    ag = ReleasePrepAgent(jira_service=mock_jira, compliance_agent=mock_compliance)
    # Mock LLM to avoid real API calls
    ag.llm.ainvoke = AsyncMock(return_value=AIMessage(content="Generated mock text."))
    return ag

@pytest.mark.asyncio
async def test_generate_release_notes(agent):
    ticket = JiraTicket(key="PROJ-1", project="PROJ", summary="Test", description="Test desc")
    notes = await agent.generate_release_notes(ticket, "abc1234 - Add feature")
    assert notes == "Generated mock text."
    agent.llm.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_prepare_release_ticket_success(agent, mock_jira):
    # Mock the get_ticket to return a valid ticket
    mock_jira.get_ticket = AsyncMock(return_value=JiraTicket(
        key="CR-123", project="PROJ", summary="Release", epic_link="EPIC-1"
    ))
    mock_jira.update_description = AsyncMock()
    
    # Mock git parser
    agent._parse_git_history = MagicMock(return_value="git history")
    
    def mock_confirm(msg):
        return True
        
    success = await agent.prepare_release_ticket("CR-123", "/tmp/repo", "v1.0.0", mock_confirm)
    
    assert success is True
    agent.compliance.validate_ticket.assert_called_once_with("CR-123")
    mock_jira.update_description.assert_called_once()
    
    updated_desc = mock_jira.update_description.call_args[0][1]
    assert "h2. Background" in updated_desc
    assert "h2. Release Notes" in updated_desc
    assert "Generated mock text." in updated_desc

@pytest.mark.asyncio
async def test_prepare_release_ticket_fails_compliance(agent):
    agent.compliance.validate_ticket.return_value = (False, ["Gap1"])
    
    success = await agent.prepare_release_ticket("CR-123", "/tmp/repo", "v1.0.0", lambda x: True)
    assert success is False
