import os
from typing import List, Dict, Optional
from datetime import datetime

from work_buddy.services.jira_service import JiraService
from work_buddy.services.browser_service import EvidencePackage

class EvidenceGathererAgent:
    """Agent responsible for gathering test evidence and posting it to Jira."""

    def __init__(self, jira_service: JiraService):
        self.jira = jira_service

    async def post_evidence(self, ticket_key: str, packages: List[EvidencePackage], evidence_type: str = "Dev") -> None:
        """
        Format and post a series of evidence packages as a single structured Jira comment.
        Valid evidence types: Dev, UAT, Regression, Performance
        """
        
        # 1. Format the comment body
        body = self._format_comment(packages, evidence_type)
        
        # 2. Upload all screenshots / attachments
        attachment_names = []
        for pkg in packages:
            for shot in pkg.screenshots:
                if os.path.exists(shot.path):
                    # Jira attachment API returns response with filename
                    # In mock it just returns {"filename": "...", "status": "attached_mock"}
                    await self.jira.attach_file(ticket_key, shot.path, os.path.basename(shot.path))
                    attachment_names.append(os.path.basename(shot.path))
            
            # If Newman HTML report exists
            report_path = pkg.metadata.get("report_path")
            if report_path and os.path.exists(report_path):
                await self.jira.attach_file(ticket_key, report_path, os.path.basename(report_path))
                attachment_names.append(os.path.basename(report_path))
                
        # 3. Post the comment
        await self.jira.add_comment(ticket_key, body, attachments=attachment_names)
        
        # 4. Add evidence type label
        label = f"evidence-{evidence_type.lower()}"
        await self.jira.add_labels(ticket_key, [label])

    def _format_comment(self, packages: List[EvidencePackage], evidence_type: str) -> str:
        """Format the Jira comment body with markdown based on evidence type."""
        date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Jira uses a specific markup, but standard markdown is often converted or supported in Jira Cloud
        lines = [
            f"h2. {evidence_type} Testing Evidence",
            f"*Date Submitted:* {date_str}",
            ""
        ]
        
        for pkg in packages:
            lines.append(f"h3. {pkg.source_tool.title()} - {pkg.flow_name}")
            status_text = "{color:green}PASSED{color}" if pkg.passed else "{color:red}FAILED{color}"
            lines.append(f"*Status:* {status_text}")
            
            if not pkg.passed and pkg.errors:
                lines.append("{panel:title=Errors|borderStyle=solid|borderColor=#ccc|titleBGColor=#ffcccc}")
                for err in pkg.errors:
                    lines.append(f"- {err}")
                lines.append("{panel}")
            
            if pkg.screenshots:
                lines.append("*Screenshots:*")
                for shot in pkg.screenshots:
                    fname = os.path.basename(shot.path)
                    lines.append(f"!{fname}|width=800!")
                    
            if pkg.metadata.get("report_path"):
                report_name = os.path.basename(pkg.metadata["report_path"])
                lines.append(f"*Automated Report:* [^{report_name}]")
                
            lines.append("----")
            
        return "\\n".join(lines)
