"""End-to-end tests for Work Buddy multi-agent system with mock services.

These tests verify complete workflows against mock services.
Run with: pytest tests/e2e/ -v
"""

import pytest
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

# ── E2E Test: Browser Test → Evidence Gatherer → Jira (Task 13.2) ─────────────

class TestBrowserTestToJiraFlow:
    """E2E test: Browser Test Agent captures screenshots → Evidence Gatherer formats → Mock Jira comment."""

    @pytest.mark.asyncio
    async def test_full_evidence_flow(self):
        """Test complete flow from browser capture to Jira comment."""
        from work_buddy.services.browser_service import EvidencePackage, Screenshot
        from work_buddy.agents.evidence_gatherer_agent import EvidenceGathererAgent
        from work_buddy.adapters.mock.mock_jira import MockJiraAdapter

        # Setup mock Jira
        jira = MockJiraAdapter(base_url="http://localhost:8081")

        # Mock the httpx calls
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json = MagicMock(return_value={
                "id": "12345",
                "key": "TEST-100",
                "summary": "Test Ticket",
                "description": "Test description",
                "labels": ["test"],
                "status": {"name": "Open"},
                "project": "TEST"
            })
            mock_response.raise_for_status = MagicMock()

            mock_context = MagicMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_context)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_context.get = AsyncMock(return_value=mock_response)
            mock_context.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            # Create evidence package (simulating browser test output)
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create a test screenshot
                screenshot_path = os.path.join(tmpdir, "test_screenshot.png")
                with open(screenshot_path, "wb") as f:
                    f.write(b"fake png content")

                package = EvidencePackage(
                    project_name="test-project",
                    flow_name="regression",
                    source_tool="opensearch",
                    screenshots=[Screenshot(path=screenshot_path, label="test_shot")],
                    passed=True,
                    errors=[],
                    metadata={"timestamp": "2024-01-01T00:00:00Z"}
                )

                # Post evidence to Jira
                agent = EvidenceGathererAgent(jira_service=jira)
                await agent.post_evidence("TEST-100", [package], evidence_type="Dev")

                # Verify comment was added
                mock_context.post.assert_called()


# ── E2E Test: Jira Task Agent (Task 13.3) ───────────────────────────────────────

class TestJiraTaskAgentE2E:
    """E2E test: Jira Task Agent creates tasks in Mock Jira with correct fields."""

    @pytest.mark.asyncio
    async def test_create_task_with_all_fields(self):
        """Test creating a Jira task with all auto-populated fields."""
        from work_buddy.agents.jira_task_agent import JiraTaskAgent
        from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
        from work_buddy.core.config import ProjectConfig, JiraConfig

        jira = MockJiraAdapter(base_url="http://localhost:8081")

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json = MagicMock(return_value={
                "id": "12346",
                "key": "PAY-456",
                "summary": "Add caching layer",
                "description": "Description here",
                "labels": ["payment", "backend", "api", "cache"],
                "status": {"name": "Open"},
                "project": "PAY"
            })
            mock_response.raise_for_status = MagicMock()

            mock_context = MagicMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_context)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_context.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            agent = JiraTaskAgent(jira_service=jira)

            with patch("work_buddy.agents.jira_task_agent.load_project_config") as mock_load:
                mock_load.return_value = ProjectConfig(
                    name="payment-service",
                    type="backend",
                    jira=JiraConfig(
                        project_key="PAY",
                        epic="PAY-200",
                        labels=["payment", "backend", "api"],
                        components=["API", "Database"]
                    )
                )

                # Mock the create_task method
                jira.create_task = AsyncMock(return_value=MagicMock(
                    key="PAY-456",
                    summary="Add caching layer"
                ))

                tickets = await agent.create_tasks_from_requirements(
                    "payment-service",
                    [{"summary": "Add caching layer", "description": "Add Redis caching", "labels": ["cache"]}]
                )

                assert len(tickets) == 1
                jira.create_task.assert_called_once()

                # Verify the call included merged labels
                call_kwargs = jira.create_task.call_args[1]
                assert "cache" in call_kwargs["labels"]
                assert "payment" in call_kwargs["labels"]


# ── E2E Test: ICE Compliance Agent (Task 13.4) ──────────────────────────────────

class TestICEComplianceE2E:
    """E2E test: ICE Compliance Agent validates Mock Jira ticket."""

    @pytest.fixture
    def ice_rules(self):
        """Create temp ICE rules file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
required_labels:
  - ice-compliant
required_description_sections:
  - Background
  - Implementation
required_evidence:
  - type: dev
    label: "Dev Testing"
    required: true
cr_fields:
  - field: rollback_plan
    description: "Rollback Plan"
    required: true
""")
            return f.name

    @pytest.mark.asyncio
    async def test_validate_compliant_ticket(self, ice_rules):
        """Test validating a compliant ticket."""
        from work_buddy.agents.ice_compliance_agent import IceComplianceAgent
        from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
        from work_buddy.services.jira_service import JiraTicket

        jira = MockJiraAdapter(base_url="http://localhost:8081")

        # Mock a compliant ticket
        compliant_ticket = JiraTicket(
            key="PAY-100",
            summary="Compliant Task",
            description="Background: Test\n\nImplementation: Steps here\n\nRollback Plan: Revert",
            labels=["ice-compliant", "evidence-dev"],
            status="Open",
            project="PAY",
            epic_link=None,
            custom_fields={"rollback_plan": "Revert deployment"}
        )

        jira.get_ticket = AsyncMock(return_value=compliant_ticket)

        agent = IceComplianceAgent(jira_service=jira, rules_path=ice_rules)
        valid, gaps = await agent.validate_ticket("PAY-100")

        assert valid is True
        assert len(gaps) == 0

        os.unlink(ice_rules)

    @pytest.mark.asyncio
    async def test_validate_non_compliant_ticket(self, ice_rules):
        """Test validating a non-compliant ticket."""
        from work_buddy.agents.ice_compliance_agent import IceComplianceAgent
        from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
        from work_buddy.services.jira_service import JiraTicket

        jira = MockJiraAdapter(base_url="http://localhost:8081")

        # Mock a non-compliant ticket
        non_compliant_ticket = JiraTicket(
            key="PAY-101",
            summary="Non-Compliant Task",
            description="Short description",
            labels=[],
            status="Open",
            project="PAY",
            epic_link=None,
            custom_fields={}
        )

        jira.get_ticket = AsyncMock(return_value=non_compliant_ticket)

        agent = IceComplianceAgent(jira_service=jira, rules_path=ice_rules)
        valid, gaps = await agent.validate_ticket("PAY-101")

        assert valid is False
        assert len(gaps) > 0

        # Check specific gaps
        gap_types = [g.type for g in gaps]
        assert "label" in gap_types

        os.unlink(ice_rules)


# ── E2E Test: Release Prep Pipeline (Task 13.5) ─────────────────────────────────

class TestReleasePrepPipelineE2E:
    """E2E test: Release prep pipeline (compliance → doc gen → Jira update)."""

    @pytest.mark.asyncio
    async def test_release_prep_pipeline(self):
        """Test the full release prep pipeline."""
        from work_buddy.agents.coordinator import AgentCoordinator
        from work_buddy.core.config import AppConfig
        from work_buddy.core.container import ServiceContainer
        from work_buddy.services.jira_service import JiraTicket

        # Setup
        config = AppConfig(mode="mock", llm_model="gpt-4o")
        container = MagicMock(spec=ServiceContainer)
        container.config = config

        # Mock Jira service
        jira_mock = MagicMock()
        jira_mock.get_ticket = AsyncMock(return_value=JiraTicket(
            key="PAY-500",
            summary="Release 2.0",
            description="Background: Release\nImplementation: Steps\n\nRollback Plan: Revert",
            labels=["ice-compliant", "evidence-dev"],
            status="Open",
            project="PAY",
            epic_link=None,
            custom_fields={}
        ))
        jira_mock.update_description = AsyncMock()
        container.jira_service = jira_mock

        # Mock other services
        container.confluence_service = MagicMock()
        container.opensearch_service = MagicMock()
        container.grafana_service = MagicMock()

        with patch("work_buddy.agents.coordinator.load_app_config") as mock_load, \
             patch("work_buddy.agents.coordinator.load_project_config") as mock_proj:

            mock_load.return_value = config
            mock_proj.return_value = MagicMock(
                name="payment-service",
                type="backend"
            )

            # Always confirm
            coordinator = AgentCoordinator(
                container=container,
                confirm_fn=lambda x: True
            )

            # Mock the release agent's LLM calls
            with patch.object(coordinator, 'release_agent') as release_mock:
                release_mock._parse_git_history = MagicMock(return_value="abc123 - Fix bug\nabc124 - Add feature")
                release_mock.generate_release_notes = AsyncMock(return_value="Release notes content")
                release_mock.generate_implementation_steps = AsyncMock(return_value="1. Deploy")
                release_mock.generate_rollback_steps = AsyncMock(return_value="1. Revert")
                release_mock.generate_pvt_steps = AsyncMock(return_value="1. Test")

                result = coordinator.execute("release", ticket="PAY-500")

                # The workflow should execute
                assert result is not None


# ── E2E Test: PVT Health Check Flow (Task 13.6) ────────────────────────────────

class TestPVTHealthCheckE2E:
    """E2E test: PVT health check flow with mock services."""

    @pytest.mark.asyncio
    async def test_pvt_health_check(self):
        """Test PVT health check execution."""
        from work_buddy.agents.log_analyst_agent import LogAnalystAgent
        from work_buddy.agents.browser_test_agent import BrowserTestAgent
        from work_buddy.core.config import ProjectConfig, ToolUrls

        # Mock browser agent
        browser_mock = MagicMock(spec=BrowserTestAgent)
        browser_mock.output_dir = tempfile.mkdtemp()
        browser_mock.capture_opensearch = AsyncMock(return_value=MagicMock(
            screenshots=[],
            passed=True,
            errors=[],
            __dict__={"screenshots": [], "passed": True, "errors": []}
        ))
        browser_mock.capture_springboot_admin = AsyncMock(return_value=MagicMock(
            screenshots=[],
            passed=True,
            errors=[],
            __dict__={"screenshots": [], "passed": True, "errors": []}
        ))

        # Mock OpenSearch service
        opensearch_mock = MagicMock()
        opensearch_mock.get_log_entries = AsyncMock(return_value=[
            {"timestamp": "2024-01-01T10:00:00", "level": "INFO", "message": "Service started"},
            {"timestamp": "2024-01-01T10:00:01", "level": "INFO", "message": "Connected to DB"},
        ])

        # Mock Grafana service
        grafana_mock = MagicMock()
        grafana_mock.get_dashboard = AsyncMock(return_value={"dashboard": "data"})

        agent = LogAnalystAgent(
            browser_agent=browser_mock,
            opensearch=opensearch_mock,
            grafana=grafana_mock
        )

        project = ProjectConfig(
            name="test-service",
            type="backend",
            tool_urls=ToolUrls(
                opensearch="http://localhost:9200",
                springboot_admin="http://localhost:9300"
            )
        )

        report_path = await agent.run_pvt_healthcheck(project)

        # Verify report was generated
        assert report_path is not None
        assert report_path.endswith(".html")

        # Cleanup
        import shutil
        shutil.rmtree(browser_mock.output_dir, ignore_errors=True)


# ── E2E Test: Alert Triage ─────────────────────────────────────────────────────

class TestAlertTriageE2E:
    """E2E test: Alert triage with LLM analysis."""

    @pytest.mark.asyncio
    async def test_alert_triage(self):
        """Test alert triage flow."""
        from work_buddy.agents.log_analyst_agent import LogAnalystAgent
        from work_buddy.agents.browser_test_agent import BrowserTestAgent
        from work_buddy.core.config import ProjectConfig, GrafanaCheck
        from langchain_core.messages import AIMessage

        # Mock browser agent
        browser_mock = MagicMock(spec=BrowserTestAgent)
        browser_mock.output_dir = tempfile.mkdtemp()

        # Mock OpenSearch service
        opensearch_mock = MagicMock()
        opensearch_mock.get_log_entries = AsyncMock(return_value=[
            {"timestamp": "2024-01-01T10:00:00", "level": "ERROR", "message": "Connection timeout"},
            {"timestamp": "2024-01-01T10:00:01", "level": "ERROR", "message": "Retry failed"},
        ])

        # Mock Grafana service
        grafana_mock = MagicMock()
        grafana_mock.get_dashboard = AsyncMock(return_value={"panels": []})

        agent = LogAnalystAgent(
            browser_agent=browser_mock,
            opensearch=opensearch_mock,
            grafana=grafana_mock
        )

        # Mock LLM response
        with patch.object(agent, 'llm') as mock_llm:
            mock_llm.ainvoke = AsyncMock(return_value=AIMessage(
                content="[NEEDS ATTENTION] Connection timeouts detected. Check database connectivity."
            ))

            project = ProjectConfig(
                name="payment-service",
                type="backend",
                grafana_checks=[GrafanaCheck(dashboard_id="payment-overview")]
            )

            report_path = await agent.triage_alert(
                project,
                "High error rate detected in payment-service"
            )

            assert report_path is not None
            assert report_path.endswith(".html")

        # Cleanup
        import shutil
        shutil.rmtree(browser_mock.output_dir, ignore_errors=True)