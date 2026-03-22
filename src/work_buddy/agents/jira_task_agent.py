import yaml
from typing import List, Dict, Any, Optional
import jinja2

from work_buddy.services.jira_service import JiraService, JiraTicket
from work_buddy.core.config import ProjectConfig, load_project_config

class JiraTaskAgent:
    """Agent responsible for automated Jira task creation based on requirements."""

    def __init__(self, jira_service: JiraService):
        self.jira = jira_service

    async def create_tasks_from_requirements(self, project_name: str, requirements: List[Dict[str, Any]]) -> List[JiraTicket]:
        """Bulk create tasks based on a list of requirements."""
        try:
            config = load_project_config(project_name)
        except FileNotFoundError:
            raise ValueError(f"Unknown project name '{project_name}' or missing configuration.")
            
        if not config.jira:
            raise ValueError(f"Project '{project_name}' has no Jira configuration defined.")
            
        jira_cfg = config.jira
        created_tickets = []
        
        # Setup Jinja2 template engine for description validation
        template_str = jira_cfg.description_template or "{{ description }}"
        template = jinja2.Template(template_str)

        for req in requirements:
            # Render templated description
            description_context = {"requirement": req, "description": req.get("description", "")}
            rendered_description = template.render(**description_context)
            
            # Auto-populate labels, avoiding duplicates but keeping requirement specific ones
            req_labels = req.get("labels", [])
            merged_labels = list(set(jira_cfg.labels + req_labels))
            
            # Auto-populate components
            req_components = req.get("components", [])
            merged_components = list(set(jira_cfg.components + req_components))
            
            # Epic link
            epic_link = req.get("epic") or jira_cfg.epic
            
            # Sprint (simplistic representation, normally Jira requires sprint ID)
            sprint = req.get("sprint") or jira_cfg.sprint_board
            
            ticket = await self.jira.create_task(
                project_key=jira_cfg.project_key,
                summary=req.get("summary", "Automated Task"),
                description=rendered_description,
                ticket_type=req.get("type", "Task"),
                epic_link=epic_link,
                sprint=sprint,
                labels=merged_labels,
                components=merged_components,
                custom_fields=req.get("custom_fields")
            )
            created_tickets.append(ticket)

        return created_tickets
