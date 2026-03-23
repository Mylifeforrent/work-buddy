import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_confluence")

app = FastAPI(title="Mock Confluence Server")

# Load the built React UI
UI_DIST = os.path.join(os.path.dirname(__file__), "..", "ui", "dist")

def get_ui_html(tool_id: str):
    index_path = os.path.join(UI_DIST, "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("UI not built. Run 'npm run build' in mock_servers/ui", status_code=500)
    with open(index_path, "r") as f:
        content = f.read()
    return HTMLResponse(content.replace("<!-- TOOL_ID -->", tool_id))

app.mount("/assets", StaticFiles(directory=os.path.join(UI_DIST, "assets")), name="assets")

@app.get("/", response_class=HTMLResponse)
async def root():
    return get_ui_html("confluence")

@app.get("/wiki/spaces/{space_key}/pages/{page_id}", response_class=HTMLResponse)
async def confluence_page_ui(space_key: str, page_id: str):
    return get_ui_html("confluence")

# PAGES seeded data

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
