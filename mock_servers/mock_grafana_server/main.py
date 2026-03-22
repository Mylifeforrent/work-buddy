import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_grafana")

app = FastAPI(title="Mock Grafana Server")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Grafana Dashboards</title>
    <style>
        body { background: #181b1f; color: #d8d9da; font-family: sans-serif; padding: 20px; }
        .panel { background: #22252b; border: 1px solid #303133; padding: 15px; margin-bottom: 20px; }
        .chart-placeholder { height: 200px; background: #2c3235; display: flex; align-items: center; justify-content: center; }
    </style>
</head>
<body>
    <h2>Mock Grafana - {dashboard_id}</h2>
    <div class="panel">
        <h3>CPU Usage</h3>
        <div class="chart-placeholder">[ Chart rendering mock for CPU: 45% ]</div>
    </div>
    <div class="panel">
        <h3>Memory Usage</h3>
        <div class="chart-placeholder">[ Chart rendering mock for Memory: 1.2 GB ]</div>
    </div>
</body>
</html>
"""

@app.on_event("startup")
async def load_seed_data():
    pass

@app.get("/d/{dashboard_id}", response_class=HTMLResponse)
async def dashboard_ui(dashboard_id: str):
    logger.info(f"GET /d/{dashboard_id}")
    return HTML_TEMPLATE.replace("{dashboard_id}", dashboard_id)

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
