from typing import Dict, Any
import httpx

from work_buddy.services.grafana_service import GrafanaService

class MockGrafanaAdapter(GrafanaService):
    """Mock implementation of GrafanaService calling the local mock server."""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        
    async def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/dashboards/uid/{dashboard_id}")
            resp.raise_for_status()
            return resp.json()

    async def get_metrics(self, metric_query: str) -> Dict[str, Any]:
        # Mock metrics response
        return {"status": "success", "data": {"result": []}}
