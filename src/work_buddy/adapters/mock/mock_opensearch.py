from typing import List, Dict, Any
import httpx

from work_buddy.services.opensearch_service import OpenSearchService

class MockOpenSearchAdapter(OpenSearchService):
    """Mock implementation of OpenSearchService calling the local mock server."""
    
    def __init__(self, base_url: str = "http://localhost:9200"):
        self.base_url = base_url
        
    async def search_logs(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/_search", json={"query": query})
            resp.raise_for_status()
            data = resp.json()
            
            return [hit["_source"] for hit in data.get("hits", {}).get("hits", [])]

    async def get_log_entries(self, service_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        return await self.search_logs(f"service: {service_name}", limit)
