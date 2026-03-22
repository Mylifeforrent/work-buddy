import json
from typing import Optional, List
import httpx

from work_buddy.services.jira_service import JiraService, JiraTicket, JiraComment

class MockJiraAdapter(JiraService):
    """Mock implementation of JiraService calling the local FastAPI mock server."""
    
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
    
    async def create_task(self, project_key: str, summary: str, description: str = "",
                          ticket_type: str = "Task", epic_link: Optional[str] = None,
                          sprint: Optional[str] = None, labels: Optional[List[str]] = None,
                          components: Optional[List[str]] = None, custom_fields: Optional[dict] = None) -> JiraTicket:
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": ticket_type},
        }
        if labels: fields["labels"] = labels
        if epic_link: fields["customfield_10014"] = epic_link
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/rest/api/3/issue", json={"fields": fields})
            resp.raise_for_status()
            data = resp.json()
            
            return JiraTicket(
                key=data["key"],
                project=project_key,
                summary=summary,
                description=description,
                status="To Do",
                ticket_type=ticket_type,
                labels=labels or []
            )

    async def get_ticket(self, ticket_key: str) -> JiraTicket:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/rest/api/3/issue/{ticket_key}")
            resp.raise_for_status()
            data = resp.json()
            
            fields = data.get("fields", {})
            return JiraTicket(
                key=data["key"],
                project=fields.get("project", {}).get("key", ""),
                summary=fields.get("summary", ""),
                description=fields.get("description", ""),
                labels=fields.get("labels", [])
            )

    async def search_tickets(self, jql: str) -> List[JiraTicket]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/rest/api/3/search", params={"jql": jql})
            resp.raise_for_status()
            data = resp.json()
            
            tickets = []
            for item in data.get("issues", []):
                fields = item.get("fields", {})
                tickets.append(JiraTicket(
                    key=item["key"],
                    project=fields.get("project", {}).get("key", ""),
                    summary=fields.get("summary", ""),
                    description=fields.get("description", ""),
                    labels=fields.get("labels", [])
                ))
            return tickets

    async def add_comment(self, ticket_key: str, body: str, attachments: Optional[List[str]] = None) -> JiraComment:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/rest/api/3/issue/{ticket_key}/comment", json={"body": body})
            resp.raise_for_status()
            data = resp.json()
            return JiraComment(id=data["id"], body=data["body"])

    async def attach_file(self, ticket_key: str, file_path: str, filename: Optional[str] = None) -> dict:
        return {"filename": filename or file_path, "status": "attached_mock"}

    async def update_labels(self, ticket_key: str, labels: List[str]) -> JiraTicket:
        async with httpx.AsyncClient() as client:
            await client.put(f"{self.base_url}/rest/api/3/issue/{ticket_key}", json={"fields": {"labels": labels}})
            return await self.get_ticket(ticket_key)

    async def add_labels(self, ticket_key: str, labels: List[str]) -> JiraTicket:
        ticket = await self.get_ticket(ticket_key)
        new_labels = list(set(ticket.labels + labels))
        return await self.update_labels(ticket_key, new_labels)

    async def update_description(self, ticket_key: str, description: str) -> JiraTicket:
        async with httpx.AsyncClient() as client:
            await client.put(f"{self.base_url}/rest/api/3/issue/{ticket_key}", json={"fields": {"description": description}})
            return await self.get_ticket(ticket_key)
