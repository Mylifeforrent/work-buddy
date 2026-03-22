"""OpenSearch Service Interface (Port).

Defines the abstract interface for log search operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogEntry:
    """Represents a single log entry from OpenSearch."""
    timestamp: str
    level: str
    service: str
    message: str
    fields: dict = field(default_factory=dict)


@dataclass
class LogSearchResult:
    """Result of an OpenSearch log query."""
    query: str
    total_hits: int
    entries: list[LogEntry] = field(default_factory=list)


class OpenSearchService(ABC):
    """Abstract interface for OpenSearch log operations.

    Implementations:
    - MockOpenSearchAdapter: Calls mock OpenSearch server
    - RealOpenSearchAdapter: Calls real OpenSearch API (stub)
    """

    @abstractmethod
    async def search_logs(
        self,
        query: str,
        base_url: Optional[str] = None,
        time_range: Optional[str] = None,
        limit: int = 100,
    ) -> LogSearchResult:
        """Search logs matching a query string.

        Args:
            query: Search query (e.g., "service:payment AND level:ERROR")
            base_url: OpenSearch instance URL (for per-project routing)
            time_range: Time range (e.g., "15m", "1h", "24h")
            limit: Maximum number of entries to return
        """
        ...

    @abstractmethod
    async def get_recent_logs(
        self,
        service_name: str,
        base_url: Optional[str] = None,
        minutes: int = 15,
        limit: int = 50,
    ) -> list[LogEntry]:
        """Get recent log entries for a specific service."""
        ...
