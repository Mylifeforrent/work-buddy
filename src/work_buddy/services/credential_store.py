"""Credential Store Interface (Port).

Defines the abstract interface for securely storing and retrieving credentials.
No credentials should ever be hardcoded.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Credentials:
    """Generic credentials."""
    identifier: str  # e.g., "sso", "jira-api", "openai"
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    token: Optional[str] = None


class CredentialStore(ABC):
    """Abstract interface for credential storage.

    Implementations:
    - MockCredentialStore: Returns test credentials from config
    - RealCredentialStore: Uses system keyring or environment variables (stub)
    """

    @abstractmethod
    async def get_credentials(self, identifier: str) -> Optional[Credentials]:
        """Retrieve credentials by identifier.

        Args:
            identifier: Key for the credentials (e.g., "sso", "jira-api")

        Returns:
            Credentials if found, None otherwise
        """
        ...

    @abstractmethod
    async def store_credentials(self, credentials: Credentials) -> None:
        """Store credentials securely.

        Args:
            credentials: Credentials to store
        """
        ...

    @abstractmethod
    async def delete_credentials(self, identifier: str) -> bool:
        """Delete stored credentials.

        Returns:
            True if credentials were found and deleted
        """
        ...

    @abstractmethod
    async def list_identifiers(self) -> list[str]:
        """List all stored credential identifiers."""
        ...
