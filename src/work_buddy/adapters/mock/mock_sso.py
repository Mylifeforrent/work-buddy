from typing import Optional, Dict
import httpx

from work_buddy.services.sso_auth_service import SSOAuthService

class MockSSOAuthAdapter(SSOAuthService):
    """Mock implementation of SSOAuthService calling the local mock SSO server."""
    
    def __init__(self, sso_url: str = "http://localhost:8090"):
        self.sso_url = sso_url
        self.session_cookie: Optional[str] = None
        
    async def authenticate(self, username: str, password: str = "dummy") -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.sso_url}/login",
                data={"username": username, "password": password, "redirect_url": "/"},
                follow_redirects=False # Just capture the cookie from the 303 response
            )
            cookies = resp.cookies
            if "sso_session" in cookies:
                self.session_cookie = cookies.get("sso_session")
                return True
            return False

    async def is_authenticated(self) -> bool:
        if not self.session_cookie:
            return False
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.sso_url}/user",
                cookies={"sso_session": self.session_cookie}
            )
            if resp.status_code == 200:
                return resp.json().get("authenticated", False)
        return False

    async def get_session(self) -> Optional[Dict[str, str]]:
        if not self.session_cookie:
            return None
        return {"Cookie": f"sso_session={self.session_cookie}"}
