import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_opensearch")

app = FastAPI(title="Mock OpenSearch Server")

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
    return get_ui_html("opensearch")

@app.get("/app/dashboards", response_class=HTMLResponse)
async def get_dashboard(query: str = ""):
    logger.info(f"GET /app/dashboards query={query}")
    return get_ui_html("opensearch")

LOGS = []

@app.get("/app/dashboards", response_class=HTMLResponse)
async def get_dashboard(query: str = ""):
    logger.info(f"GET /app/dashboards query={query}")
    return DASHBOARD_HTML.replace("{query}", query)

@app.post("/_search")
async def search_logs(request: Request):
    logger.info("POST /_search")
    body = await request.json()
    return {
        "hits": {
            "total": {"value": len(LOGS)},
            "hits": [
                {"_source": log} for log in LOGS
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("opensearch_server:app", host="0.0.0.0", port=9200, reload=True)

@app.get("/health")
async def health():
    return {"status": "ok"}
