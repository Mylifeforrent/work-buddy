import logging
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_opensearch")

app = FastAPI(title="Mock OpenSearch Server")

LOGS = []

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenSearch Dashboards</title>
    <style>
        body { font-family: sans-serif; margin: 0; padding: 20px; }
        .search-bar { width: 100%; padding: 10px; font-size: 16px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Mock OpenSearch Dashboards</h2>
    <input type="text" class="search-bar" placeholder="Search logs..." value="{query}">
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Level</th>
            <th>Service</th>
            <th>Message</th>
        </tr>
        <tr>
            <td>2023-01-01 12:00:00</td>
            <td>ERROR</td>
            <td>PaymentService</td>
            <td>Failed to connect to DB</td>
        </tr>
    </table>
</body>
</html>
"""

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
