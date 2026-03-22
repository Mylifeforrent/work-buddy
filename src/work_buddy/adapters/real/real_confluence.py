from typing import Optional, List
from work_buddy.services.confluence_service import ConfluenceService, ConfluencePage, SearchResult

class RealConfluenceAdapter(ConfluenceService):
    """Real implementation of ConfluenceService."""
    
    async def search_pages(self, *args, **kwargs) -> List[SearchResult]:
        raise NotImplementedError("TODO")

    async def get_page_content(self, *args, **kwargs) -> ConfluencePage:
        raise NotImplementedError("TODO")

    async def get_page_by_title(self, *args, **kwargs) -> Optional[ConfluencePage]:
        raise NotImplementedError("TODO")

    async def list_pages(self, *args, **kwargs) -> List[ConfluencePage]:
        raise NotImplementedError("TODO")
