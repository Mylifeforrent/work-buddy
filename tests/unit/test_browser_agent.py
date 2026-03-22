import pytest
import os
from unittest.mock import AsyncMock, MagicMock

from work_buddy.agents.browser_test_agent import BrowserTestAgent
from work_buddy.core.config import ProjectConfig, TestFlow, TestStep, AuthConfig, ToolUrls

@pytest.fixture
def mock_browser():
    browser = AsyncMock()
    browser.get_current_url.return_value = "http://localhost:8080/somepage"
    browser.assert_text.return_value = True
    browser.screenshot.return_value = MagicMock(path="mock_path.png", label="mock", timestamp="2023-01-01T00:00:00Z", url="http://mock")
    return browser

@pytest.fixture
def agent(mock_browser, tmp_path):
    return BrowserTestAgent(browser=mock_browser, output_dir=str(tmp_path))

@pytest.mark.asyncio
async def test_execute_react_flow_success(agent, mock_browser):
    project = ProjectConfig(
        name="test-project",
        type="react-app",
        base_url="http://localhost:3000",
        auth=AuthConfig(type="none")
    )
    flow = TestFlow(
        name="login_flow",
        steps=[
            TestStep(action="navigate", target="/login"),
            TestStep(action="type", target="#username", value="user"),
            TestStep(action="click", target="#submit"),
            TestStep(action="wait_for", target=".dashboard"),
            TestStep(action="screenshot", label="dashboard_view")
        ]
    )
    
    pkg = await agent.execute_react_flow(project, flow)
    
    assert pkg.passed is True
    assert pkg.project_name == "test-project"
    assert pkg.flow_name == "login_flow"
    assert len(pkg.errors) == 0
    assert len(pkg.screenshots) == 1
    
    # Verify browser interactions
    assert mock_browser.navigate.call_count >= 2 # once for base_url, once for step
    mock_browser.type_text.assert_called_with("#username", "user")
    mock_browser.click.assert_called_with("#submit")
    mock_browser.wait_for.assert_called_with(".dashboard")
    mock_browser.screenshot.assert_called()

@pytest.mark.asyncio
async def test_capture_opensearch(agent, mock_browser):
    project = ProjectConfig(
        name="backend-server",
        type="backend",
        tool_urls=ToolUrls(opensearch="http://localhost:9200/dashboards"),
        auth=AuthConfig(type="none"),
        evidence_checks={"opensearch": [MagicMock(query="error OR Exception", screenshot_label="errors", name="chk1")]}
    )
    
    pkg = await agent.capture_opensearch(project)
    
    assert pkg.passed is True
    assert pkg.source_tool == "opensearch"
    assert len(pkg.screenshots) == 1
    mock_browser.navigate.assert_called_with("http://localhost:9200/dashboards")
