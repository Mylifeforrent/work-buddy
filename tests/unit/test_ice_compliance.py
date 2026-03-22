import pytest
import os
import yaml
from unittest.mock import AsyncMock, patch
from dataclasses import dataclass

from work_buddy.agents.ice_compliance_agent import IceComplianceAgent
from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
from work_buddy.services.jira_service import JiraTicket

@pytest.fixture
def mock_rules_path(tmp_path):
    rules = {
        "required_labels": ["release-ready"],
        "required_description_sections": ["Background"],
        "required_evidence": [
            {"type": "dev_testing", "required": True, "label": "Dev Testing Evidence"}
        ],
        "cr_fields": [
            {"field": "release_notes", "required": True, "description": "Release notes"}
        ]
    }
    path = tmp_path / "ice_rules.yaml"
    with open(path, "w") as f:
        yaml.dump(rules, f)
    return str(path)

@pytest.fixture
def agent(mock_rules_path):
    jira_mock = MockJiraAdapter(base_url="http://fake")
    return IceComplianceAgent(jira_service=jira_mock, rules_path=mock_rules_path)

@pytest.mark.asyncio
async def test_validate_ticket_perfect(agent):
    agent.jira.get_ticket = AsyncMock(return_value=JiraTicket(
        key="TEST-1",
        project="TEST",
        summary="Test Ticket",
        description="Background: we did this.\\nRelease notes: included",
        labels=["release-ready", "evidence-dev-testing"]
    ))
    
    valid, gaps = await agent.validate_ticket("TEST-1")
    assert valid is True
    assert len(gaps) == 0

@pytest.mark.asyncio
async def test_validate_ticket_gaps(agent):
    agent.jira.get_ticket = AsyncMock(return_value=JiraTicket(
        key="TEST-2",
        project="TEST",
        summary="Test Bad Ticket",
        description="Just doing some work",
        labels=[]
    ))
    
    valid, gaps = await agent.validate_ticket("TEST-2")
    assert valid is False
    assert len(gaps) == 4
    
    gap_types = [g.type for g in gaps]
    assert "label" in gap_types
    assert "description_section" in gap_types
    assert "evidence" in gap_types
    assert "field" in gap_types

@pytest.mark.asyncio
async def test_auto_fix_labels(agent):
    agent.jira.get_ticket = AsyncMock(return_value=JiraTicket(
        key="TEST-3",
        project="TEST",
        summary="Test Label Missing",
        description="Background: ...\\nRelease notes: ...",
        labels=["evidence-dev-testing"] # Missing release-ready
    ))
    agent.jira.add_labels = AsyncMock()
    
    # Confirm always True
    def mock_confirm(msg):
        return True
        
    await agent.auto_fix_ticket("TEST-3", mock_confirm)
    
    agent.jira.add_labels.assert_called_once_with("TEST-3", ["release-ready"])
