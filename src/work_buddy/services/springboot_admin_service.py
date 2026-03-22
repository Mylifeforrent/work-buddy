"""SpringBoot Admin Service Interface (Port).

Defines the abstract interface for SpringBoot Admin health check operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ServiceHealth:
    """Health status of a registered service."""
    service_name: str
    status: str  # UP, DOWN, OUT_OF_SERVICE, UNKNOWN
    details: dict = field(default_factory=dict)


@dataclass
class R2DBStatus:
    """R2DB (Reactive Relational Database) connection status."""
    status: str  # UP, DOWN
    database: str = ""
    validation_query: str = ""


@dataclass
class RegisteredService:
    """A service registered with SpringBoot Admin."""
    id: str
    name: str
    status: str
    url: str = ""
    health: Optional[ServiceHealth] = None
    r2db: Optional[R2DBStatus] = None


class SpringBootAdminService(ABC):
    """Abstract interface for SpringBoot Admin operations.

    Implementations:
    - MockSpringBootAdminAdapter: Calls mock SpringBoot Admin server
    - RealSpringBootAdminAdapter: Calls real SpringBoot Admin API (stub)
    """

    @abstractmethod
    async def list_services(self, base_url: Optional[str] = None) -> list[RegisteredService]:
        """List all registered services."""
        ...

    @abstractmethod
    async def get_service_health(self, service_name: str, base_url: Optional[str] = None) -> ServiceHealth:
        """Get health status for a specific service."""
        ...

    @abstractmethod
    async def get_r2db_status(self, service_name: str, base_url: Optional[str] = None) -> R2DBStatus:
        """Get R2DB connection status for a specific service."""
        ...
