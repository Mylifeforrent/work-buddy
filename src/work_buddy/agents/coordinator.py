"""Agent Coordinator using LangGraph for multi-agent orchestration.

This module implements the central coordinator that:
- Routes user requests to appropriate agents
- Manages inter-agent data flow
- Orchestrates multi-agent workflows
- Provides progress feedback
- Handles human-in-the-loop confirmations
"""

import asyncio
from typing import TypedDict, Optional, List, Dict, Any, Callable, Annotated
from dataclasses import dataclass, field
from enum import Enum
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from work_buddy.core.config import load_app_config, load_project_config, ProjectConfig
from work_buddy.core.container import ServiceContainer, create_container
from work_buddy.core.logging import get_logger

logger = get_logger(__name__)


# ── Workflow State ─────────────────────────────────────────────────────────────

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentStep:
    """Represents a single step in a multi-agent workflow."""
    agent_name: str
    action: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowState(TypedDict):
    """State that flows through the LangGraph workflow."""
    # Request info
    request_type: str
    project_name: Optional[str]
    ticket_key: Optional[str]
    query: Optional[str]
    raw_request: Optional[str]

    # Progress tracking
    steps: Annotated[List[Dict], operator.add]
    current_step: int
    status: str

    # Data flowing between agents
    evidence_packages: List[Dict]
    validation_result: Optional[Dict]
    generated_content: Optional[Dict]

    # Human-in-the-loop
    confirmation_required: bool
    confirmation_message: str
    confirmation_result: Optional[bool]

    # Final output
    result: Optional[Dict]
    error: Optional[str]


# ── Request Parser ──────────────────────────────────────────────────────────────

class RequestParser:
    """Parses CLI commands and routes to appropriate agents."""

    WORKFLOW_TYPES = {
        "test": ["regression", "smoke", "upgrade"],
        "jira": ["create", "bulk-create"],
        "compliance": ["check", "fix"],
        "release": ["prepare"],
        "pvt": ["run"],
        "docs": ["search", "summarize"],
        "alert": ["triage"],
    }

    @classmethod
    def parse(cls, command: str, **kwargs) -> Dict[str, Any]:
        """Parse a CLI command into workflow parameters.

        Args:
            command: The command type (test, jira, compliance, etc.)
            **kwargs: Command-specific arguments

        Returns:
            Dict with workflow type and parameters
        """
        return {
            "request_type": command,
            "project_name": kwargs.get("project"),
            "ticket_key": kwargs.get("ticket"),
            "query": kwargs.get("query"),
            "test_type": kwargs.get("test_type", "regression"),
            "requirement": kwargs.get("requirement"),
            "alert_details": kwargs.get("alert_details"),
            "raw_request": kwargs,
        }

    @classmethod
    def get_workflow_for_request(cls, request_type: str) -> str:
        """Determine which workflow graph to use for a request type."""
        workflow_map = {
            "test": "browser_test_workflow",
            "jira": "jira_task_workflow",
            "compliance": "compliance_workflow",
            "release": "release_prep_workflow",
            "pvt": "pvt_workflow",
            "docs": "docs_workflow",
            "alert": "alert_triage_workflow",
        }
        return workflow_map.get(request_type, "default_workflow")


# ── Confirmation Handler ────────────────────────────────────────────────────────

class ConfirmationHandler:
    """Handles human-in-the-loop confirmations."""

    def __init__(self, confirm_fn: Optional[Callable[[str], bool]] = None):
        self.confirm_fn = confirm_fn or self._default_confirm

    def _default_confirm(self, message: str) -> bool:
        """Default confirmation using console input."""
        print(f"\n{message}")
        response = input("Proceed? [y/N]: ").strip().lower()
        return response in ("y", "yes")

    def request_confirmation(self, message: str) -> bool:
        """Request confirmation from user."""
        logger.info(f"Requesting confirmation: {message}")
        return self.confirm_fn(message)


# ── Progress Display ────────────────────────────────────────────────────────────

class ProgressDisplay:
    """Displays progress for multi-agent workflows."""

    def __init__(self):
        self.current_workflow = None
        self.steps = []

    def start_workflow(self, workflow_name: str, total_steps: int):
        """Initialize progress display for a workflow."""
        self.current_workflow = workflow_name
        self.steps = []
        logger.info(f"Starting workflow: {workflow_name} ({total_steps} steps)")

    def update_step(self, step_name: str, status: str, message: str = ""):
        """Update progress for a step."""
        status_icons = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "waiting": "⏸️",
        }
        icon = status_icons.get(status, "•")
        logger.info(f"{icon} {step_name}: {status}" + (f" - {message}" if message else ""))

    def complete_workflow(self, success: bool, message: str = ""):
        """Mark workflow as complete."""
        icon = "✅" if success else "❌"
        logger.info(f"{icon} Workflow {'completed' if success else 'failed'}" + (f": {message}" if message else ""))


# ── Agent Coordinator ──────────────────────────────────────────────────────────

class AgentCoordinator:
    """Central coordinator for all multi-agent workflows using LangGraph."""

    def __init__(self, container: ServiceContainer = None, confirm_fn: Callable = None):
        self.config = load_app_config()
        self.container = container or create_container(self.config)
        self.confirmation_handler = ConfirmationHandler(confirm_fn)
        self.progress = ProgressDisplay()

        # Lazy-loaded agents
        self._jira_agent = None
        self._evidence_agent = None
        self._compliance_agent = None
        self._release_agent = None
        self._browser_agent = None
        self._log_agent = None
        self._confluence_agent = None

        # Build workflow graphs
        self._graphs = {}
        self._build_workflows()

    # ── Agent Properties (Lazy Loading) ────────────────────────────────────────

    @property
    def jira_agent(self):
        if self._jira_agent is None:
            from work_buddy.agents.jira_task_agent import JiraTaskAgent
            self._jira_agent = JiraTaskAgent(jira_service=self.container.jira_service)
        return self._jira_agent

    @property
    def evidence_agent(self):
        if self._evidence_agent is None:
            from work_buddy.agents.evidence_gatherer_agent import EvidenceGathererAgent
            self._evidence_agent = EvidenceGathererAgent(jira_service=self.container.jira_service)
        return self._evidence_agent

    @property
    def compliance_agent(self):
        if self._compliance_agent is None:
            from work_buddy.agents.ice_compliance_agent import IceComplianceAgent
            self._compliance_agent = IceComplianceAgent(jira_service=self.container.jira_service)
        return self._compliance_agent

    @property
    def release_agent(self):
        if self._release_agent is None:
            from work_buddy.agents.release_prep_agent import ReleasePrepAgent
            self._release_agent = ReleasePrepAgent(
                jira_service=self.container.jira_service,
                compliance_agent=self._compliance_agent or self.compliance_agent
            )
        return self._release_agent

    @property
    def browser_agent(self):
        if self._browser_agent is None:
            from work_buddy.agents.browser_test_agent import BrowserTestAgent
            # Need browser service from real adapter
            from work_buddy.adapters.real.real_browser import RealBrowserAdapter
            browser = RealBrowserAdapter()
            self._browser_agent = BrowserTestAgent(browser=browser)
        return self._browser_agent

    @property
    def log_agent(self):
        if self._log_agent is None:
            from work_buddy.agents.log_analyst_agent import LogAnalystAgent
            self._log_agent = LogAnalystAgent(
                browser_agent=self._browser_agent or self.browser_agent,
                opensearch=self.container.opensearch_service,
                grafana=self.container.grafana_service
            )
        return self._log_agent

    @property
    def confluence_agent(self):
        if self._confluence_agent is None:
            from work_buddy.agents.confluence_rag_agent import ConfluenceRagAgent
            self._confluence_agent = ConfluenceRagAgent(
                confluence=self.container.confluence_service
            )
        return self._confluence_agent

    # ── Workflow Building ──────────────────────────────────────────────────────

    def _build_workflows(self):
        """Build all LangGraph workflow graphs."""
        self._graphs["browser_test_workflow"] = self._build_browser_test_workflow()
        self._graphs["evidence_workflow"] = self._build_evidence_workflow()
        self._graphs["release_prep_workflow"] = self._build_release_prep_workflow()
        self._graphs["compliance_workflow"] = self._build_compliance_workflow()
        self._graphs["docs_workflow"] = self._build_docs_workflow()
        self._graphs["pvt_workflow"] = self._build_pvt_workflow()
        self._graphs["alert_triage_workflow"] = self._build_alert_triage_workflow()
        self._graphs["jira_task_workflow"] = self._build_jira_task_workflow()

    def _build_browser_test_workflow(self) -> StateGraph:
        """Build browser test workflow: run tests → capture evidence."""
        workflow = StateGraph(WorkflowState)

        def run_tests(state: WorkflowState) -> dict:
            self.progress.update_step("Browser Tests", "running")
            try:
                project_name = state["project_name"]
                test_type = state["raw_request"].get("test_type", "regression")
                project = load_project_config(project_name)

                packages = []

                # Run React app flows if applicable
                if project.type == "react-app":
                    for flow in project.test_flows:
                        pkg = asyncio.run(self.browser_agent.execute_react_flow(project, flow))
                        packages.append(pkg.__dict__)

                # Capture dashboard evidence for backend services
                if project.tool_urls.opensearch:
                    pkg = asyncio.run(self.browser_agent.capture_opensearch(project))
                    packages.append(pkg.__dict__)

                if project.tool_urls.springboot_admin:
                    pkg = asyncio.run(self.browser_agent.capture_springboot_admin(project))
                    packages.append(pkg.__dict__)

                if project.tool_urls.grafana:
                    pkg = asyncio.run(self.browser_agent.capture_grafana(project))
                    packages.append(pkg.__dict__)

                self.progress.update_step("Browser Tests", "completed", f"{len(packages)} evidence packages")
                return {
                    "evidence_packages": packages,
                    "steps": [{"agent": "browser_test", "action": "run_tests", "status": "completed"}]
                }
            except Exception as e:
                self.progress.update_step("Browser Tests", "failed", str(e))
                return {"error": str(e), "steps": [{"agent": "browser_test", "action": "run_tests", "status": "failed"}]}

        workflow.add_node("run_tests", run_tests)
        workflow.set_entry_point("run_tests")
        workflow.add_edge("run_tests", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _build_evidence_workflow(self) -> StateGraph:
        """Build evidence gathering workflow: Browser Test → Evidence Gatherer → Jira."""
        workflow = StateGraph(WorkflowState)

        def capture_evidence(state: WorkflowState) -> dict:
            self.progress.update_step("Capture Evidence", "running")
            # Reuse browser test logic
            project_name = state["project_name"]
            project = load_project_config(project_name)

            packages = []
            if project.tool_urls.opensearch:
                pkg = asyncio.run(self.browser_agent.capture_opensearch(project))
                packages.append(pkg)

            if project.tool_urls.springboot_admin:
                pkg = asyncio.run(self.browser_agent.capture_springboot_admin(project))
                packages.append(pkg)

            self.progress.update_step("Capture Evidence", "completed")
            return {"evidence_packages": [p.__dict__ for p in packages]}

        def post_to_jira(state: WorkflowState) -> dict:
            self.progress.update_step("Post to Jira", "running")
            ticket_key = state["ticket_key"]
            packages = state.get("evidence_packages", [])
            evidence_type = state["raw_request"].get("evidence_type", "Dev")

            # Convert back to EvidencePackage objects
            from work_buddy.services.browser_service import EvidencePackage
            pkg_objs = []
            for p in packages:
                pkg_objs.append(EvidencePackage(**p))

            asyncio.run(self.evidence_agent.post_evidence(ticket_key, pkg_objs, evidence_type))

            self.progress.update_step("Post to Jira", "completed")
            return {
                "steps": [{"agent": "evidence_gatherer", "action": "post_evidence", "status": "completed"}]
            }

        workflow.add_node("capture_evidence", capture_evidence)
        workflow.add_node("post_to_jira", post_to_jira)

        workflow.set_entry_point("capture_evidence")
        workflow.add_edge("capture_evidence", "post_to_jira")
        workflow.add_edge("post_to_jira", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _build_release_prep_workflow(self) -> StateGraph:
        """Build release prep workflow: Compliance → Doc Gen → Jira Update."""
        workflow = StateGraph(WorkflowState)

        def check_compliance(state: WorkflowState) -> dict:
            self.progress.update_step("ICE Compliance Check", "running")
            ticket_key = state["ticket_key"]

            valid, gaps = asyncio.run(self.compliance_agent.validate_ticket(ticket_key))

            if not valid:
                self.progress.update_step("ICE Compliance Check", "failed", f"{len(gaps)} gaps found")
                return {
                    "validation_result": {"valid": False, "gaps": [{"type": g.type, "message": g.message} for g in gaps]},
                    "status": "compliance_failed",
                    "steps": [{"agent": "compliance", "action": "validate", "status": "failed"}]
                }

            self.progress.update_step("ICE Compliance Check", "completed")
            return {
                "validation_result": {"valid": True, "gaps": []},
                "steps": [{"agent": "compliance", "action": "validate", "status": "completed"}]
            }

        def generate_docs(state: WorkflowState) -> dict:
            if state.get("validation_result", {}).get("valid") is False:
                return {"status": "skipped"}

            self.progress.update_step("Generate Release Docs", "running")
            ticket_key = state["ticket_key"]
            repo_path = state["raw_request"].get("repo_path", ".")
            since_tag = state["raw_request"].get("since_tag", "HEAD~10")

            # Generate docs (without auto-posting)
            generated = {}
            try:
                ticket = asyncio.run(self.container.jira_service.get_ticket(ticket_key))
                git_history = self.release_agent._parse_git_history(repo_path, since_tag)
                generated["release_notes"] = asyncio.run(self.release_agent.generate_release_notes(ticket, git_history))
                generated["implementation_steps"] = asyncio.run(self.release_agent.generate_implementation_steps(
                    load_project_config(state.get("project_name", ticket.project))
                ))
                generated["rollback_steps"] = asyncio.run(self.release_agent.generate_rollback_steps(
                    load_project_config(state.get("project_name", ticket.project))
                ))
            except Exception as e:
                return {"error": str(e)}

            self.progress.update_step("Generate Release Docs", "completed")
            return {
                "generated_content": generated,
                "steps": [{"agent": "release_prep", "action": "generate_docs", "status": "completed"}]
            }

        def confirm_and_update(state: WorkflowState) -> dict:
            if state.get("validation_result", {}).get("valid") is False:
                return {"result": {"success": False, "reason": "Compliance check failed"}}

            content = state.get("generated_content", {})
            ticket_key = state["ticket_key"]

            # Request confirmation
            message = f"Update {ticket_key} with generated release documentation?"
            if self.confirmation_handler.request_confirmation(message):
                # Combine content
                new_desc = f"""
h2. Release Notes
{content.get('release_notes', '')}

h2. Implementation Steps
{content.get('implementation_steps', '')}

h2. Rollback Steps
{content.get('rollback_steps', '')}
"""
                asyncio.run(self.container.jira_service.update_description(ticket_key, new_desc.strip()))
                self.progress.update_step("Update Jira", "completed")
                return {
                    "result": {"success": True},
                    "steps": [{"agent": "release_prep", "action": "update_jira", "status": "completed"}]
                }
            else:
                self.progress.update_step("Update Jira", "skipped", "User cancelled")
                return {
                    "result": {"success": False, "reason": "User cancelled"},
                    "steps": [{"agent": "release_prep", "action": "update_jira", "status": "skipped"}]
                }

        workflow.add_node("check_compliance", check_compliance)
        workflow.add_node("generate_docs", generate_docs)
        workflow.add_node("confirm_and_update", confirm_and_update)

        workflow.set_entry_point("check_compliance")
        workflow.add_edge("check_compliance", "generate_docs")
        workflow.add_edge("generate_docs", "confirm_and_update")
        workflow.add_edge("confirm_and_update", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _build_compliance_workflow(self) -> StateGraph:
        """Build compliance check workflow."""
        workflow = StateGraph(WorkflowState)

        def validate_ticket(state: WorkflowState) -> dict:
            self.progress.update_step("Validate Ticket", "running")
            ticket_key = state["ticket_key"]

            valid, gaps = asyncio.run(self.compliance_agent.validate_ticket(ticket_key))

            result = {
                "valid": valid,
                "gaps": [{"type": g.type, "message": g.message, "remediation": g.remediation} for g in gaps]
            }

            self.progress.update_step("Validate Ticket", "completed" if valid else "failed")
            return {"validation_result": result, "result": result}

        workflow.add_node("validate_ticket", validate_ticket)
        workflow.set_entry_point("validate_ticket")
        workflow.add_edge("validate_ticket", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _build_docs_workflow(self) -> StateGraph:
        """Build Confluence docs workflow."""
        workflow = StateGraph(WorkflowState)

        def search_or_summarize(state: WorkflowState) -> dict:
            query = state["query"]
            page_id = state["raw_request"].get("page_id")

            if page_id:
                self.progress.update_step("Summarize Document", "running")
                result = asyncio.run(self.confluence_agent.summarize_document(page_id))
                self.progress.update_step("Summarize Document", "completed")
                return {"result": result}
            else:
                self.progress.update_step("Search Docs", "running")
                answer, sources = asyncio.run(self.confluence_agent.query_support_docs(query))
                self.progress.update_step("Search Docs", "completed")
                return {"result": {"answer": answer, "sources": sources}}

        workflow.add_node("search_or_summarize", search_or_summarize)
        workflow.set_entry_point("search_or_summarize")
        workflow.add_edge("search_or_summarize", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _build_pvt_workflow(self) -> StateGraph:
        """Build PVT health check workflow."""
        workflow = StateGraph(WorkflowState)

        def run_pvt(state: WorkflowState) -> dict:
            self.progress.update_step("PVT Health Check", "running")
            project_name = state["project_name"]
            project = load_project_config(project_name)

            report_path = asyncio.run(self.log_agent.run_pvt_healthcheck(project))

            self.progress.update_step("PVT Health Check", "completed")
            return {"result": {"report_path": report_path}}

        workflow.add_node("run_pvt", run_pvt)
        workflow.set_entry_point("run_pvt")
        workflow.add_edge("run_pvt", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _build_alert_triage_workflow(self) -> StateGraph:
        """Build alert triage workflow."""
        workflow = StateGraph(WorkflowState)

        def triage_alert(state: WorkflowState) -> dict:
            self.progress.update_step("Alert Triage", "running")
            project_name = state["project_name"]
            alert_details = state["raw_request"].get("alert_details", state.get("query", ""))

            project = load_project_config(project_name)
            report_path = asyncio.run(self.log_agent.triage_alert(project, alert_details))

            self.progress.update_step("Alert Triage", "completed")
            return {"result": {"report_path": report_path}}

        workflow.add_node("triage_alert", triage_alert)
        workflow.set_entry_point("triage_alert")
        workflow.add_edge("triage_alert", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _build_jira_task_workflow(self) -> StateGraph:
        """Build Jira task creation workflow."""
        workflow = StateGraph(WorkflowState)

        def create_task(state: WorkflowState) -> dict:
            self.progress.update_step("Create Jira Task", "running")
            project_name = state["project_name"]
            requirement = state["raw_request"].get("requirement", state.get("query", ""))

            requirements = [{"summary": requirement, "description": requirement}]
            tickets = asyncio.run(self.jira_agent.create_tasks_from_requirements(project_name, requirements))

            self.progress.update_step("Create Jira Task", "completed")
            return {
                "result": {
                    "success": True,
                    "tickets": [{"key": t.key, "summary": t.summary} for t in tickets]
                }
            }

        workflow.add_node("create_task", create_task)
        workflow.set_entry_point("create_task")
        workflow.add_edge("create_task", END)

        return workflow.compile(checkpointer=MemorySaver())

    # ── Public API ──────────────────────────────────────────────────────────────

    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a command through the appropriate workflow.

        Args:
            command: The command type (test, jira, compliance, release, pvt, docs, alert)
            **kwargs: Command-specific arguments

        Returns:
            Dict with workflow result
        """
        # Parse request
        params = RequestParser.parse(command, **kwargs)
        workflow_name = RequestParser.get_workflow_for_request(command)

        # Get workflow graph
        graph = self._graphs.get(workflow_name)
        if not graph:
            return {"error": f"Unknown workflow: {workflow_name}"}

        # Initialize state
        initial_state: WorkflowState = {
            "request_type": command,
            "project_name": params.get("project_name"),
            "ticket_key": params.get("ticket_key"),
            "query": params.get("query"),
            "raw_request": params,
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

        # Execute workflow
        self.progress.start_workflow(workflow_name, len(graph.nodes))

        try:
            config = {"configurable": {"thread_id": f"{command}_{params.get('project_name', 'default')}"}}
            result = graph.invoke(initial_state, config)

            self.progress.complete_workflow(result.get("error") is None)

            return {
                "success": result.get("error") is None,
                "result": result.get("result"),
                "error": result.get("error"),
                "steps": result.get("steps", []),
            }
        except Exception as e:
            self.progress.complete_workflow(False, str(e))
            return {"success": False, "error": str(e)}

    async def execute_async(self, command: str, **kwargs) -> Dict[str, Any]:
        """Async version of execute."""
        return self.execute(command, **kwargs)

    def get_workflow_status(self, thread_id: str) -> Optional[Dict]:
        """Get the current status of a running workflow."""
        # Would use LangGraph's state inspection
        # For now, return None as workflows run synchronously
        return None