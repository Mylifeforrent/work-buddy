"""Integration tests for multi-agent workflows with mock services."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from work_buddy.agents.coordinator import (
    AgentCoordinator,
    RequestParser,
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
        description="Background:\nTest background\n\nImplementation:\nStep 1",
        labels=["ice-compliant", "evidence-dev"],
        project="testproj",
        epic_link=None,
        custom_fields={}
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

    def test_complete_workflow(self):
        """Test completing workflow."""
        display = ProgressDisplay()
        display.complete_workflow(True, "Success")


# ── Coordinator Tests ───────────────────────────────────────────────────────────

class TestCoordinatorBasics:
    """Basic tests for coordinator functionality."""

    def test_coordinator_created(self, coordinator):
        """Test that coordinator is created successfully."""
        assert coordinator is not None
        assert coordinator._graphs is not None
        assert "compliance_workflow" in coordinator._graphs

    def test_workflows_built(self, coordinator):
        """Test that all workflows are built."""
        assert "browser_test_workflow" in coordinator._graphs
        assert "jira_task_workflow" in coordinator._graphs
        assert "compliance_workflow" in coordinator._graphs
        assert "release_prep_workflow" in coordinator._graphs
        assert "pvt_workflow" in coordinator._graphs
        assert "docs_workflow" in coordinator._graphs
        assert "alert_triage_workflow" in coordinator._graphs


class TestCoordinatorWorkflows:
    """Tests for coordinator workflows."""

    @pytest.mark.asyncio
    async def test_compliance_workflow(self, coordinator, mock_container):
        """Test compliance workflow execution."""
        # Need to also mock load_project_config for some workflows
        with patch("work_buddy.agents.coordinator.load_project_config") as mock_proj:
            mock_proj.return_value = MagicMock(name="testproj", type="backend")

            result = coordinator.execute("compliance", ticket="TEST-123")

            assert result is not None

    @pytest.mark.asyncio
    async def test_unknown_workflow(self, coordinator):
        """Test handling of unknown workflow type."""
        result = coordinator.execute("unknown_command")

        # Unknown workflow returns an error
        assert result.get("success") is False or "error" in result


# ── Error Handling Tests ────────────────────────────────────────────────────────

class TestErrorHandling:
    """Tests for error handling in workflows."""

    @pytest.mark.asyncio
    async def test_service_error_handling(self, mock_container):
        """Test handling service errors."""
        mock_container.jira_service.get_ticket = AsyncMock(side_effect=Exception("Jira API Error"))

        with patch("work_buddy.agents.coordinator.load_app_config") as mock_load:
            mock_load.return_value = mock_container.config
            coordinator = AgentCoordinator(container=mock_container, confirm_fn=lambda x: True)

            result = coordinator.execute("compliance", ticket="TEST-123")

            assert result["success"] is False
            assert "error" in result