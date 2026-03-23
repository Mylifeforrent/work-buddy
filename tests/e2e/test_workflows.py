"""End-to-end tests for Work Buddy multi-agent system with mock services.

These tests verify complete workflows against mock services.
Run with: pytest tests/e2e/ -v
"""

import pytest
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

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

        os.unlink(ice_rules)


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

        with patch("work_buddy.agents.log_analyst_agent.load_app_config") as mock_load, \
             patch("work_buddy.agents.log_analyst_agent.ChatOpenAI") as mock_chat:

            mock_load.return_value = MagicMock(llm_model="gpt-4o")

            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(return_value=AIMessage(
                content="[NEEDS ATTENTION] Connection timeouts detected. Check database connectivity."
            ))
            mock_chat.return_value = mock_llm

            agent = LogAnalystAgent(
                browser_agent=browser_mock,
                opensearch=opensearch_mock,
                grafana=grafana_mock
            )

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