from typing import Dict, Optional
from work_buddy.services.credential_store import CredentialStore

class MockCredentialStore(CredentialStore):
    """Mock implementation of CredentialStore that returns dummy credentials."""
    
    def __init__(self):
        self.creds = {
            "jira": {"username": "testuser", "token": "testtoken123"},
            "confluence": {"username": "testuser", "token": "testtoken123"},
        }
    
    async def get_credentials(self, service_name: str) -> Optional[Dict[str, str]]:
        return self.creds.get(service_name)
    
    async def store_credentials(self, service_name: str, credentials: Dict[str, str]) -> None:
        self.creds[service_name] = credentials
