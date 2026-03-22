import yaml
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from work_buddy.services.jira_service import JiraService, JiraTicket

@dataclass
class ValidationGap:
    type: str # 'label', 'description_section', 'evidence', 'field'
    message: str
    remediation: str

class IceComplianceAgent:
    """Agent that validates Jira tickets against ICE (Internal Compliance Engine) rules."""
    
    def __init__(self, jira_service: JiraService, rules_path: str = "configs/ice_rules.yaml"):
        self.jira = jira_service
        self.rules = self._load_rules(rules_path)
        
    def _load_rules(self, rules_path: str) -> Dict[str, Any]:
        """Load ICE compliance rules from YAML."""
        with open(rules_path, "r") as f:
            return yaml.safe_load(f)

    async def validate_ticket(self, ticket_key: str) -> Tuple[bool, List[ValidationGap]]:
        """Validate a ticket against all loaded rules and return pass/fail and list of gaps."""
        ticket = await self.jira.get_ticket(ticket_key)
        gaps = []
        
        gaps.extend(self._check_labels(ticket))
        gaps.extend(self._check_description_sections(ticket))
        gaps.extend(self._check_evidence(ticket))
        gaps.extend(self._check_fields(ticket))
        
        return len(gaps) == 0, gaps

    def _check_labels(self, ticket: JiraTicket) -> List[ValidationGap]:
        gaps = []
        required = self.rules.get("required_labels", [])
        for label in required:
            if label not in ticket.labels:
                gaps.append(ValidationGap(
                    type="label",
                    message=f"Missing required label: {label}",
                    remediation=f"Add label '{label}' to the ticket"
                ))
        return gaps

    def _check_description_sections(self, ticket: JiraTicket) -> List[ValidationGap]:
        gaps = []
        required = self.rules.get("required_description_sections", [])
        desc = ticket.description or ""
        for section in required:
            # Simple check if the section name appears in the description
            if section.lower() not in desc.lower():
                gaps.append(ValidationGap(
                    type="description_section",
                    message=f"Missing section in description: {section}",
                    remediation=f"Add a '{section}' section to the ticket description"
                ))
        return gaps

    def _check_evidence(self, ticket: JiraTicket) -> List[ValidationGap]:
        gaps = []
        required = self.rules.get("required_evidence", [])
        
        # Check if ticket has evidence labels (added by EvidenceGathererAgent)
        for req in required:
            if req.get("required", False):
                ev_type = req["type"]
                label_to_find = f"evidence-{ev_type}".replace("_", "-")
                
                has_evidence = False
                for label in ticket.labels:
                    if label_to_find in label.lower() or ev_type.lower() in label.lower():
                        has_evidence = True
                        break
                        
                if not has_evidence:
                    gaps.append(ValidationGap(
                        type="evidence",
                        message=f"Missing required testing evidence: {req['label']}",
                        remediation=f"Run the '{ev_type}' Agent to gather and attach {req['label']}"
                    ))
        return gaps

    def _check_fields(self, ticket: JiraTicket) -> List[ValidationGap]:
        gaps = []
        required = self.rules.get("cr_fields", [])
        desc = ticket.description or ""
        
        for req in required:
            if req.get("required", False):
                field_name = req["field"]
                # For mock purposes, check Custom Fields OR if the field name is mentioned in the description
                if field_name not in ticket.custom_fields and field_name.replace("_", " ").lower() not in desc.lower():
                    gaps.append(ValidationGap(
                        type="field",
                        message=f"Missing required field/data: {req['description']}",
                        remediation=f"Ensure {req['description']} is provided in custom fields or description"
                    ))
        return gaps

    async def auto_fix_ticket(self, ticket_key: str, confirm_fn) -> bool:
        """Attempt to auto-fix missing labels/tags if human interaction confirms it."""
        valid, gaps = await self.validate_ticket(ticket_key)
        if valid:
            return True
            
        labels_to_add = []
        for gap in gaps:
            if gap.type == "label":
                label = gap.message.split(": ")[1]
                labels_to_add.append(label)
                
        if labels_to_add:
            # Human in the loop confirm
            if confirm_fn(f"Auto-add missing labels {labels_to_add} to {ticket_key}?"):
                await self.jira.add_labels(ticket_key, labels_to_add)
                
        # Re-validate
        valid, _ = await self.validate_ticket(ticket_key)
        return valid
