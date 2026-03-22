import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os
from langchain_core.messages import AIMessage

from work_buddy.agents.log_analyst_agent import LogAnalystAgent
from work_buddy.core.config import AppConfig, ProjectConfig
from work_buddy.services.browser_service import EvidencePackage

@pytest.fixture
def mock_browser_agent():
    agent = AsyncMock()
    agent.output_dir = "/tmp"
    
    pkg = EvidencePackage("proj", "flow", "tool", passed=True)
    agent.capture_opensearch.return_value = pkg
    agent.capture_springboot_admin.return_value = pkg
    return agent

@pytest.fixture
def mock_opensearch():
    os_mock = AsyncMock()
    os_mock.get_log_entries.return_value = [{"level": "ERROR", "message": "DB Conn failed"}]
    return os_mock

@pytest.fixture
def mock_grafana():
    g_mock = AsyncMock()
    g_mock.get_dashboard.return_value = {"status": "ok"}
    return g_mock

@pytest.fixture
@patch("work_buddy.agents.log_analyst_agent.load_app_config")
def agent(mock_load_config, mock_browser_agent, mock_opensearch, mock_grafana):
    mock_load_config.return_value = AppConfig(mode="mock", llm_model="gpt-4")
    ag = LogAnalystAgent(mock_browser_agent, mock_opensearch, mock_grafana)
    ag.llm.ainvoke = AsyncMock(return_value=AIMessage(content="[CRITICAL] DB is down."))
    return ag

@pytest.mark.asyncio
async def test_run_pvt_healthcheck(agent):
    proj = ProjectConfig(name="backend-svc", type="backend")
    
    report_path = await agent.run_pvt_healthcheck(proj)
    
    assert report_path == "/tmp/backend-svc_pvt_report.html"
    agent.browser_agent.capture_opensearch.assert_called_once_with(proj)
    agent.browser_agent.capture_springboot_admin.assert_called_once_with(proj)
    agent.opensearch.get_log_entries.assert_called_once_with("backend-svc", limit=20)

@pytest.mark.asyncio
async def test_triage_alert(agent):
    proj = ProjectConfig(name="backend-svc", type="backend")
    
    report_path = await agent.triage_alert(proj, "High CPU Alert")
    
    assert report_path == "/tmp/backend-svc_triage_report.html"
    agent.opensearch.get_log_entries.assert_called_with("backend-svc", limit=50)
    agent.llm.ainvoke.assert_called_once()
    
    # Check if report contains recommendation
    with open(report_path, "r") as f:
        content = f.read()
        assert "[CRITICAL] DB is down." in content
