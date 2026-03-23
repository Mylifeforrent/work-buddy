import logging
import os
from typing import Optional, List, Dict
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_sba")

app = FastAPI(title="Mock SpringBoot Admin Server")

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
    return get_ui_html("springboot_admin")

@app.get("/applications", response_class=HTMLResponse)
async def applications_ui():
    logger.info("GET /applications")
    return get_ui_html("springboot_admin")

SERVICES = {
    "payment-service": {
        "status": "UP",
        "details": {
            "r2db_status": "UP",
            "db_connections": 10
        }
    },
    "user-portal": {
        "status": "UP",
        "details": {
            "r2db_status": "UP",
            "db_connections": 5
        }
    }
}

@app.on_event("startup")
async def load_seed_data():
    # TODO: Load from seed_data/sba.yaml
    pass

@app.get("/api/applications")
async def api_applications():
    logger.info("GET /api/applications")
    return [{"name": k, "statusInfo": {"status": v["status"]}} for k, v in SERVICES.items()]

@app.get("/api/applications/{name}/health")
async def api_health(name: str):
    logger.info(f"GET /api/applications/{name}/health")
    if name not in SERVICES:
        return {"status": "UNKNOWN"}
    return SERVICES[name]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("springboot_admin_server:app", host="0.0.0.0", port=8083, reload=True)

@app.get("/health")
async def health():
    return {"status": "ok"}
