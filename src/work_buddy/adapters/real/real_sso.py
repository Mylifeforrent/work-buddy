from typing import Optional, Dict
from work_buddy.services.sso_auth_service import SSOAuthService

class RealSSOAuthAdapter(SSOAuthService):
    """Real implementation of SSOAuthService."""
    
    async def authenticate(self, *args, **kwargs) -> bool:
        raise NotImplementedError("TODO")

    async def is_authenticated(self) -> bool:
        raise NotImplementedError("TODO")

    async def get_session(self) -> Optional[Dict[str, str]]:
        raise NotImplementedError("TODO")
