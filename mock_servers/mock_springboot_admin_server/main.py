import logging
from typing import Optional, List, Dict
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_sba")

app = FastAPI(title="Mock SpringBoot Admin Server")

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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Spring Boot Admin</title>
    <style>
        body { font-family: sans-serif; margin: 0; padding: 20px; }
        .service-card { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
        .status-UP { color: green; font-weight: bold; }
        .status-DOWN { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Spring Boot Admin (Mock)</h2>
    <div id="services-list">
        {content}
    </div>
</body>
</html>
"""

@app.on_event("startup")
async def load_seed_data():
    # TODO: Load from seed_data/sba.yaml
    pass

@app.get("/applications", response_class=HTMLResponse)
async def applications_ui():
    logger.info("GET /applications")
    content = ""
    for name, data in SERVICES.items():
        status = data["status"]
        r2db = data["details"]["r2db_status"]
        content += f'''
        <div class="service-card" id="service-{name}">
            <h3>{name}</h3>
            <p>Overall Status: <span class="status-{status}">{status}</span></p>
            <p>R2DB Status: <span class="status-{r2db}">{r2db}</span></p>
        </div>
        '''
    return HTML_TEMPLATE.replace("{content}", content)

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
