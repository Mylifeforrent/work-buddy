from typing import Optional, List
import httpx

from work_buddy.services.confluence_service import ConfluenceService, ConfluencePage, SearchResult

class MockConfluenceAdapter(ConfluenceService):
    """Mock implementation of ConfluenceService calling the local mock server."""
    
    def __init__(self, base_url: str = "http://localhost:8082"):
        self.base_url = base_url
    
    async def search_pages(self, query: str, space_key: Optional[str] = None, limit: int = 10) -> List[SearchResult]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/wiki/rest/api/content/search", params={"cql": query, "limit": limit})
            resp.raise_for_status()
            data = resp.json()
            
            results = []
            for item in data.get("results", []):
                page = ConfluencePage(
                    id=item["id"],
                    title=item.get("title", ""),
                    space_key=item.get("space", {}).get("key", ""),
                    body=item.get("body", {}).get("storage", {}).get("value", "")
                )
                results.append(SearchResult(page=page))
            return results

    async def get_page_content(self, page_id: str) -> ConfluencePage:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/wiki/rest/api/content/{page_id}")
            resp.raise_for_status()
            data = resp.json()
            
            return ConfluencePage(
                id=data["id"],
                title=data.get("title", ""),
                space_key=data.get("space", {}).get("key", ""),
                body=data.get("body", {}).get("storage", {}).get("value", "")
            )

    async def get_page_by_title(self, title: str, space_key: str) -> Optional[ConfluencePage]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/wiki/rest/api/content", params={"title": title, "spaceKey": space_key})
            resp.raise_for_status()
            data = resp.json()
            
            results = data.get("results", [])
            if not results:
                return None
            item = results[0]
            return ConfluencePage(
                id=item["id"],
                title=item.get("title", ""),
                space_key=item.get("space", {}).get("key", ""),
                body=item.get("body", {}).get("storage", {}).get("value", "")
            )

    async def list_pages(self, space_key: str, limit: int = 50) -> List[ConfluencePage]:
        return await self.search_pages(f"space={space_key}", space_key=space_key, limit=limit)
