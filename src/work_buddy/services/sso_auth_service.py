"""SSO Authentication Service Interface (Port).

Defines the abstract interface for Corporate SSO authentication.
Each monitoring tool requires separate SSO login (no session sharing).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SSOSession:
    """Represents an authenticated SSO session."""
    session_id: str
    staff_id: str
    is_valid: bool = True
    cookies: dict = None

    def __post_init__(self):
        if self.cookies is None:
            self.cookies = {}


@dataclass
class SSOCredentials:
    """Corporate SSO login credentials."""
    staff_id: str
    password: str


class SSOAuthService(ABC):
    """Abstract interface for SSO authentication.

    In the real environment, each tool (OpenSearch, Grafana, SpringBoot Admin)
    requires a separate SSO login — sessions are NOT shared between tools.

    Implementations:
    - MockSSOAuthAdapter: Accepts any credentials, issues mock session
    - RealSSOAuthAdapter: Handles real corporate SSO flow (stub)
    """

    @abstractmethod
    async def authenticate(self, credentials: SSOCredentials, tool_url: str) -> SSOSession:
        """Authenticate with SSO for a specific tool.

        Args:
            credentials: Staff ID and password
            tool_url: URL of the tool to authenticate for (since sessions aren't shared)

        Returns:
            SSOSession with cookies for the authenticated tool
        """
        ...

    @abstractmethod
    async def is_authenticated(self, tool_url: str) -> bool:
        """Check if there's a valid session for a specific tool."""
        ...

    @abstractmethod
    async def get_session(self, tool_url: str) -> Optional[SSOSession]:
        """Get the current session for a tool, if authenticated."""
        ...

    @abstractmethod
    async def logout(self, tool_url: str) -> None:
        """Invalidate the session for a specific tool."""
        ...
