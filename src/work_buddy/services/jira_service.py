"""Jira Service Interface (Port).

Defines the abstract interface for all Jira operations.
Agents use this interface, never concrete implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JiraTicket:
    """Represents a Jira ticket."""
    key: str
    project: str
    summary: str
    description: str = ""
    status: str = "To Do"
    ticket_type: str = "Task"
    epic_link: Optional[str] = None
    sprint: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    comments: list[dict] = field(default_factory=list)
    attachments: list[dict] = field(default_factory=list)
    custom_fields: dict = field(default_factory=dict)


@dataclass
class JiraComment:
    """Represents a Jira comment."""
    id: str
    body: str
    author: str = "workbuddy"
    created: str = ""
    attachments: list[str] = field(default_factory=list)


class JiraService(ABC):
    """Abstract interface for Jira operations.

    Implementations:
    - MockJiraAdapter: Calls mock Jira server for local development
    - RealJiraAdapter: Calls real Jira REST API (stub)
    """

    @abstractmethod
    async def create_task(
        self,
        project_key: str,
        summary: str,
        description: str = "",
        ticket_type: str = "Task",
        epic_link: Optional[str] = None,
        sprint: Optional[str] = None,
        labels: Optional[list[str]] = None,
        components: Optional[list[str]] = None,
        custom_fields: Optional[dict] = None,
    ) -> JiraTicket:
        """Create a new Jira task.

        Returns:
            Created JiraTicket with assigned key
        """
        ...

    @abstractmethod
    async def get_ticket(self, ticket_key: str) -> JiraTicket:
        """Get a Jira ticket by key (e.g., 'PROJ-123')."""
        ...

    @abstractmethod
    async def search_tickets(self, jql: str) -> list[JiraTicket]:
        """Search for tickets using JQL."""
        ...

    @abstractmethod
    async def add_comment(
        self,
        ticket_key: str,
        body: str,
        attachments: Optional[list[str]] = None,
    ) -> JiraComment:
        """Add a comment to a ticket, optionally with file attachments."""
        ...

    @abstractmethod
    async def attach_file(self, ticket_key: str, file_path: str, filename: Optional[str] = None) -> dict:
        """Attach a file to a ticket."""
        ...

    @abstractmethod
    async def update_labels(self, ticket_key: str, labels: list[str]) -> JiraTicket:
        """Set labels on a ticket (replaces existing labels)."""
        ...

    @abstractmethod
    async def add_labels(self, ticket_key: str, labels: list[str]) -> JiraTicket:
        """Add labels to a ticket (preserves existing labels)."""
        ...

    @abstractmethod
    async def update_description(self, ticket_key: str, description: str) -> JiraTicket:
        """Update the description of a ticket."""
        ...
