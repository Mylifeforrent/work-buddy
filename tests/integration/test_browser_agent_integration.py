import pytest
import os
import shutil

from work_buddy.agents.browser_test_agent import BrowserTestAgent
from work_buddy.adapters.real.real_browser import RealBrowserAdapter
from work_buddy.core.config import ProjectConfig, AuthConfig, ToolUrls, EvidenceCheck, SpringBootAdminCheck, GrafanaCheck

@pytest.mark.asyncio
async def test_integration_browser_agent_mock_services():
    """
    Integration test utilizing the RealBrowserAdapter (Playwright) 
    against the locally running mock services via docker-compose.
    """
    output_dir = "tests/integration/evidence_output"
    os.makedirs(output_dir, exist_ok=True)
    
    browser = RealBrowserAdapter()
    await browser.launch(headless=True)
    
    agent = BrowserTestAgent(browser=browser, output_dir=output_dir)
    
    # Create a project config pointing to local mock services
    project = ProjectConfig(
        name="backend-integration-test",
        type="backend",
        auth=AuthConfig(
            type="corporate-sso",
            sso_url="http://localhost:8090",
            username_selector="#username",
            password_selector="#password",
            submit_selector="#submit"
        ),
        tool_urls=ToolUrls(
            opensearch="http://localhost:9200/app/dashboards",
            springboot_admin="http://localhost:9300/applications",
            grafana="http://localhost:3001"
        ),
        evidence_checks={"opensearch": [EvidenceCheck(name="error_logs", query="ERROR", screenshot_label="err_logs")]},
        springboot_admin_checks=[SpringBootAdminCheck(service_name="payment-service")],
        grafana_checks=[GrafanaCheck(dashboard_id="db_main", screenshot_label="main_dash")]
    )
    
    try:
        # 1. OpenSearch Capture
        os_pkg = await agent.capture_opensearch(project)
        assert os_pkg.passed is True
        assert len(os_pkg.screenshots) > 0
        
        # 2. SpringBoot Admin Capture
        sba_pkg = await agent.capture_springboot_admin(project)
        assert sba_pkg.passed is True
        assert len(sba_pkg.screenshots) > 0
        
        # 3. Grafana Capture
        grafana_pkg = await agent.capture_grafana(project)
        assert grafana_pkg.passed is True
        assert len(grafana_pkg.screenshots) > 0
        
    finally:
        await browser.close()
        shutil.rmtree(output_dir, ignore_errors=True)
