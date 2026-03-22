import logging
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_confluence")

app = FastAPI(title="Mock Confluence Server")

PAGES: Dict[str, dict] = {}

@app.on_event("startup")
async def load_seed_data():
    # TODO: Load from seed_data/confluence.yaml
    logger.info("Confluence Mock Server started.")
    pass

@app.get("/wiki/rest/api/content/{page_id}")
async def get_page(page_id: str, expand: str = ""):
    logger.info(f"GET /wiki/rest/api/content/{page_id}")
    if page_id not in PAGES:
        # Mock finding
        return {
            "id": page_id,
            "type": "page",
            "title": f"Mock Page {page_id}",
            "space": {"key": "SYS"},
            "body": {
                "storage": {"value": "<p>This is mock content.</p>"}
            },
            "_links": {"webui": f"/spaces/SYS/pages/{page_id}"}
        }
    return PAGES[page_id]

@app.get("/wiki/rest/api/content")
async def search_by_title(spaceKey: str = "", title: str = "", expand: str = ""):
    logger.info(f"GET /wiki/rest/api/content title={title}")
    # Mock searching
    results = [p for p in PAGES.values() if p.get("title") == title and p.get("space", {}).get("key") == spaceKey]
    return {"results": results}

@app.get("/wiki/rest/api/content/search")
async def search_pages(cql: str = "", limit: int = 10, expand: str = ""):
    logger.info(f"GET /wiki/rest/api/content/search cql={cql}")
    # Return everything or mock results
    return {
        "results": list(PAGES.values())[:limit]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("confluence_server:app", host="0.0.0.0", port=8082, reload=True)

@app.get("/health")
async def health():
    return {"status": "ok"}
