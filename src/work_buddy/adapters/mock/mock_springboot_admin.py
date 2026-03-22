from typing import Dict, Any, List
import httpx

from work_buddy.services.springboot_admin_service import SpringBootAdminService

class MockSpringBootAdminAdapter(SpringBootAdminService):
    """Mock implementation of SpringBootAdminService calling the local mock server."""
    
    def __init__(self, base_url: str = "http://localhost:9300"):
        self.base_url = base_url
        
    async def list_services(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/applications")
            resp.raise_for_status()
            return resp.json()

    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/applications/{service_name}/health")
            resp.raise_for_status()
            return resp.json()

    async def get_r2db_status(self, service_name: str) -> str:
        health_data = await self.get_service_health(service_name)
        return health_data.get("details", {}).get("r2db_status", "UNKNOWN")
