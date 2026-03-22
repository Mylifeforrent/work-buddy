import pytest
from unittest.mock import AsyncMock

from work_buddy.agents.evidence_gatherer_agent import EvidenceGathererAgent
from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
from work_buddy.services.browser_service import EvidencePackage, Screenshot

@pytest.fixture
def mock_jira():
    jira = MockJiraAdapter(base_url="http://fake")
    jira.attach_file = AsyncMock(return_value={"filename": "mock.png"})
    jira.add_comment = AsyncMock(return_value={"id": "1", "body": "comment"})
    jira.add_labels = AsyncMock()
    return jira

@pytest.fixture
def agent(mock_jira):
    return EvidenceGathererAgent(jira_service=mock_jira)

@pytest.mark.asyncio
async def test_post_evidence(agent, mock_jira, tmp_path):
    # Dummy file
    img_path = tmp_path / "test.png"
    img_path.write_text("dummy")
    
    pkg1 = EvidencePackage(
        project_name="proj1",
        flow_name="login",
        source_tool="react-app",
        passed=True,
        screenshots=[Screenshot(path=str(img_path), label="test", timestamp="now")]
    )
    
    pkg2 = EvidencePackage(
        project_name="proj1",
        flow_name="api_tests",
        source_tool="postman",
        passed=False,
        errors=["Assertion fake failed"],
        metadata={"report_path": str(img_path)}
    )
    
    await agent.post_evidence("PROJ-123", [pkg1, pkg2], "UAT")
    
    # Check attach calls (1 image, 1 report, both using the dummy file for testing)
    assert mock_jira.attach_file.call_count == 2
    
    # Check add_comment
    assert mock_jira.add_comment.call_count == 1
    call_args = mock_jira.add_comment.call_args[0]
    assert call_args[0] == "PROJ-123"
    assert "UAT Testing Evidence" in call_args[1]
    assert "{color:green}PASSED{color}" in call_args[1]
    assert "{color:red}FAILED{color}" in call_args[1]
    assert "Assertion fake failed" in call_args[1]
    assert "!test.png|width=800!" in call_args[1]
    
    # Check labels
    mock_jira.add_labels.assert_called_once_with("PROJ-123", ["evidence-uat"])
