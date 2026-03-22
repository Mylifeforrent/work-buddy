"""Confluence Service Interface (Port).

Defines the abstract interface for Confluence page operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConfluencePage:
    """Represents a Confluence page."""
    id: str
    title: str
    space_key: str
    body: str = ""
    url: str = ""
    last_modified: str = ""
    labels: list[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Represents a Confluence search result."""
    page: ConfluencePage
    excerpt: str = ""
    score: float = 0.0


class ConfluenceService(ABC):
    """Abstract interface for Confluence operations.

    Implementations:
    - MockConfluenceAdapter: Calls mock Confluence server
    - RealConfluenceAdapter: Calls real Confluence REST API (stub)
    """

    @abstractmethod
    async def search_pages(self, query: str, space_key: Optional[str] = None, limit: int = 10) -> list[SearchResult]:
        """Search for Confluence pages matching a query."""
        ...

    @abstractmethod
    async def get_page_content(self, page_id: str) -> ConfluencePage:
        """Get the full content of a page by ID."""
        ...

    @abstractmethod
    async def get_page_by_title(self, title: str, space_key: str) -> Optional[ConfluencePage]:
        """Get a page by its exact title within a space."""
        ...

    @abstractmethod
    async def list_pages(self, space_key: str, limit: int = 50) -> list[ConfluencePage]:
        """List all pages in a space."""
        ...
