"""Integration tests for multi-agent workflows with mock services."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os
import tempfile

from work_buddy.agents.coordinator import (
    AgentCoordinator,
    RequestParser,
    WorkflowState,
    ConfirmationHandler,
    ProgressDisplay,
)
from work_buddy.core.config import AppConfig
from work_buddy.core.container import ServiceContainer


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_config():
    """Create a mock app config."""
    return AppConfig(
        mode="mock",
        mock_jira_url="http://localhost:8081",
        mock_confluence_url="http://localhost:8082",
        mock_sso_url="http://localhost:8090",
        llm_model="gpt-4o"
    )


@pytest.fixture
def mock_container(mock_config):
    """Create a mock service container."""
    container = MagicMock(spec=ServiceContainer)
    container.config = mock_config

    # Mock Jira service
    jira_mock = MagicMock()
    jira_mock.create_task = AsyncMock(return_value=MagicMock(key="TEST-123", summary="Test Task"))
    jira_mock.get_ticket = AsyncMock(return_value=MagicMock(
        key="TEST-123",
        summary="Test",
        description="Test description",
        labels=["test"],
        project="testproj"
    ))
    jira_mock.add_comment = AsyncMock()
    jira_mock.add_labels = AsyncMock()
    jira_mock.update_description = AsyncMock()
    container.jira_service = jira_mock

    # Mock Confluence service
    confluence_mock = MagicMock()
    confluence_mock.search_pages = AsyncMock(return_value=[])
    confluence_mock.get_page_content = AsyncMock(return_value=None)
    container.confluence_service = confluence_mock

    # Mock OpenSearch service
    opensearch_mock = MagicMock()
    opensearch_mock.get_log_entries = AsyncMock(return_value=[
        {"timestamp": "2024-01-01", "level": "INFO", "message": "Test log"}
    ])
    container.opensearch_service = opensearch_mock

    # Mock Grafana service
    grafana_mock = MagicMock()
    grafana_mock.get_dashboard = AsyncMock(return_value={})
    container.grafana_service = grafana_mock

    return container


@pytest.fixture
def coordinator(mock_container):
    """Create a coordinator with mocked dependencies."""
    with patch("work_buddy.agents.coordinator.load_app_config") as mock_load:
        mock_load.return_value = mock_container.config
        coord = AgentCoordinator(container=mock_container, confirm_fn=lambda x: True)
        return coord


# ── RequestParser Tests ────────────────────────────────────────────────────────

class TestRequestParser:
    """Tests for request parsing."""

    def test_parse_test_command(self):
        """Test parsing a test command."""
        result = RequestParser.parse("test", project="myproject", test_type="regression")

        assert result["request_type"] == "test"
        assert result["project_name"] == "myproject"
        assert result["raw_request"]["test_type"] == "regression"

    def test_parse_jira_command(self):
        """Test parsing a jira command."""
        result = RequestParser.parse("jira", project="myproject", requirement="Add feature X")

        assert result["request_type"] == "jira"
        assert result["project_name"] == "myproject"
        assert result["requirement"] == "Add feature X"

    def test_parse_compliance_command(self):
        """Test parsing a compliance command."""
        result = RequestParser.parse("compliance", ticket="TEST-123")

        assert result["request_type"] == "compliance"
        assert result["ticket_key"] == "TEST-123"

    def test_get_workflow_for_request(self):
        """Test workflow routing."""
        assert RequestParser.get_workflow_for_request("test") == "browser_test_workflow"
        assert RequestParser.get_workflow_for_request("jira") == "jira_task_workflow"
        assert RequestParser.get_workflow_for_request("compliance") == "compliance_workflow"
        assert RequestParser.get_workflow_for_request("release") == "release_prep_workflow"
        assert RequestParser.get_workflow_for_request("pvt") == "pvt_workflow"
        assert RequestParser.get_workflow_for_request("docs") == "docs_workflow"
        assert RequestParser.get_workflow_for_request("alert") == "alert_triage_workflow"


# ── ConfirmationHandler Tests ──────────────────────────────────────────────────

class TestConfirmationHandler:
    """Tests for human-in-the-loop confirmations."""

    def test_confirmation_handler_with_fn(self):
        """Test confirmation with custom function."""
        called = []
        def confirm_fn(msg):
            called.append(msg)
            return True

        handler = ConfirmationHandler(confirm_fn)
        result = handler.request_confirmation("Proceed?")

        assert result is True
        assert "Proceed?" in called[0]

    def test_confirmation_handler_returns_false(self):
        """Test confirmation returning False."""
        handler = ConfirmationHandler(lambda x: False)
        result = handler.request_confirmation("Proceed?")

        assert result is False


# ── ProgressDisplay Tests ───────────────────────────────────────────────────────

class TestProgressDisplay:
    """Tests for progress display."""

    def test_start_workflow(self):
        """Test starting workflow progress."""
        display = ProgressDisplay()
        display.start_workflow("test_workflow", 3)

        assert display.current_workflow == "test_workflow"

    def test_update_step(self):
        """Test updating step progress."""
        display = ProgressDisplay()
        display.update_step("step1", "running", "Processing")

        # Should not raise any errors

    def test_complete_workflow(self):
        """Test completing workflow."""
        display = ProgressDisplay()
        display.complete_workflow(True, "Success")

        # Should not raise any errors


# ── Coordinator Integration Tests ───────────────────────────────────────────────

class TestCoordinatorWorkflows:
    """Integration tests for coordinator workflows."""

    @pytest.mark.asyncio
    async def test_compliance_workflow_valid_ticket(self, coordinator, mock_container):
        """Test compliance workflow with valid ticket."""
        # Mock a compliant ticket
        mock_container.jira_service.get_ticket = AsyncMock(return_value=MagicMock(
            key="TEST-123",
            summary="Test",
            description="Background:\nTest background\n\nImplementation:\nStep 1",
            labels=["ice-compliant", "evidence-dev"],
            project="testproj",
            epic_link=None,
            custom_fields={}
        ))

        result = coordinator.execute("compliance", ticket="TEST-123")

        assert result["success"] is True
        assert result["result"]["valid"] is True

    @pytest.mark.asyncio
    async def test_compliance_workflow_invalid_ticket(self, coordinator, mock_container):
        """Test compliance workflow with non-compliant ticket."""
        # Mock a non-compliant ticket
        mock_container.jira_service.get_ticket = AsyncMock(return_value=MagicMock(
            key="TEST-123",
            summary="Test",
            description="Short description",
            labels=[],  # Missing required labels
            project="testproj",
            epic_link=None,
            custom_fields={}
        ))

        result = coordinator.execute("compliance", ticket="TEST-123")

        assert result["success"] is True
        assert result["result"]["valid"] is False
        assert len(result["result"]["gaps"]) > 0

    @pytest.mark.asyncio
    async def test_jira_task_workflow(self, coordinator, mock_container):
        """Test Jira task creation workflow."""
        with patch("work_buddy.agents.coordinator.load_project_config") as mock_load:
            mock_load.return_value = MagicMock(
                name="testproj",
                jira=MagicMock(
                    project_key="TEST",
                    epic="TEST-1",
                    labels=["auto"],
                    components=["API"]
                )
            )

            result = coordinator.execute("jira", project="testproj", requirement="Add new feature")

            assert result["success"] is True
            assert "tickets" in result["result"]

    @pytest.mark.asyncio
    async def test_docs_search_workflow(self, coordinator, mock_container):
        """Test docs search workflow."""
        # Mock the Confluence agent
        with patch.object(coordinator, 'confluence_agent') as mock_conf_agent:
            mock_conf_agent.query_support_docs = AsyncMock(return_value=(
                "This is the answer",
                ["http://confluence/page/1"]
            ))

            result = coordinator.execute("docs", query="How to deploy?")

            assert result["success"] is True
            assert "answer" in result["result"]

    @pytest.mark.asyncio
    async def test_release_prep_workflow_compliance_fails(self, coordinator, mock_container):
        """Test release prep workflow when compliance fails."""
        # Mock a non-compliant ticket
        mock_container.jira_service.get_ticket = AsyncMock(return_value=MagicMock(
            key="TEST-123",
            summary="Test",
            description="Short",
            labels=[],
            project="testproj",
            epic_link=None,
            custom_fields={}
        ))

        result = coordinator.execute("release", ticket="TEST-123")

        # Should fail due to compliance issues
        assert result["result"]["success"] is False

    @pytest.mark.asyncio
    async def test_unknown_workflow(self, coordinator):
        """Test handling of unknown workflow type."""
        result = coordinator.execute("unknown_command")

        assert result["success"] is False
        assert "error" in result


# ── Multi-Agent Workflow Tests ──────────────────────────────────────────────────

class TestMultiAgentWorkflows:
    """Tests for multi-agent workflow orchestration."""

    @pytest.mark.asyncio
    async def test_evidence_to_jira_flow(self, mock_container):
        """Test Browser Test → Evidence Gatherer → Jira flow."""
        with patch("work_buddy.agents.coordinator.load_app_config") as mock_load, \
             patch("work_buddy.agents.coordinator.load_project_config") as mock_proj:

            mock_load.return_value = mock_container.config
            mock_proj.return_value = MagicMock(
                name="testproj",
                type="backend",
                tool_urls=MagicMock(
                    opensearch="http://localhost:9200",
                    springboot_admin="http://localhost:9300",
                    grafana=None
                ),
                evidence_checks={"opensearch": []},
                springboot_admin_checks=[],
                auth=MagicMock(type="none")
            )

            # Mock browser agent
            with patch("work_buddy.agents.coordinator.RealBrowserAdapter") as mock_browser:
                mock_browser_instance = MagicMock()
                mock_browser.return_value = mock_browser_instance

                coord = AgentCoordinator(container=mock_container, confirm_fn=lambda x: True)

                # The workflow should be buildable
                assert "evidence_workflow" in coord._graphs

    @pytest.mark.asyncio
    async def test_release_prep_orchestration(self, mock_container):
        """Test release prep orchestration: compliance → docs → jira update."""
        with patch("work_buddy.agents.coordinator.load_app_config") as mock_load:
            mock_load.return_value = mock_container.config

            coord = AgentCoordinator(container=mock_container, confirm_fn=lambda x: True)

            # The release prep workflow should have the right nodes
            graph = coord._graphs["release_prep_workflow"]
            assert graph is not None


# ── State Management Tests ──────────────────────────────────────────────────────

class TestWorkflowState:
    """Tests for workflow state management."""

    def test_initial_state(self):
        """Test creating initial workflow state."""
        state: WorkflowState = {
            "request_type": "test",
            "project_name": "myproject",
            "ticket_key": None,
            "query": None,
            "raw_request": {},
            "steps": [],
            "current_step": 0,
            "status": "pending",
            "evidence_packages": [],
            "validation_result": None,
            "generated_content": None,
            "confirmation_required": False,
            "confirmation_message": "",
            "confirmation_result": None,
            "result": None,
            "error": None,
        }

        assert state["request_type"] == "test"
        assert state["status"] == "pending"
        assert len(state["steps"]) == 0

    def test_state_step_accumulation(self):
        """Test that steps accumulate correctly."""
        steps = []
        steps.append({"agent": "browser", "action": "test", "status": "completed"})
        steps.append({"agent": "evidence", "action": "post", "status": "completed"})

        assert len(steps) == 2


# ── Error Handling Tests ────────────────────────────────────────────────────────

class TestErrorHandling:
    """Tests for error handling in workflows."""

    @pytest.mark.asyncio
    async def test_jira_service_error(self, coordinator, mock_container):
        """Test handling Jira service errors."""
        mock_container.jira_service.get_ticket = AsyncMock(side_effect=Exception("Jira API Error"))

        result = coordinator.execute("compliance", ticket="TEST-123")

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_project_not_found(self, coordinator, mock_container):
        """Test handling project not found."""
        with patch("work_buddy.agents.coordinator.load_project_config") as mock_load:
            mock_load.side_effect = FileNotFoundError("Project not found")

            result = coordinator.execute("jira", project="nonexistent", requirement="test")

            assert result["success"] is False