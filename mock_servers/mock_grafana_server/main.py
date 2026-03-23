import logging
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_grafana")

app = FastAPI(title="Mock Grafana Server")

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
    return get_ui_html("grafana")

@app.on_event("startup")
async def load_seed_data():
    pass

@app.get("/d/{dashboard_id}", response_class=HTMLResponse)
async def dashboard_ui(dashboard_id: str):
    logger.info(f"GET /d/{dashboard_id}")
    return get_ui_html("grafana")

@app.get("/api/dashboards/uid/{dashboard_id}")
async def api_get_dashboard(dashboard_id: str):
    logger.info(f"GET /api/dashboards/uid/{dashboard_id}")
    return {"dashboard": {"uid": dashboard_id, "title": f"Dashboard {dashboard_id}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("grafana_server:app", host="0.0.0.0", port=8084, reload=True)

@app.get("/health")
async def health():
    return {"status": "ok"}
