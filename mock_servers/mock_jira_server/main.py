import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_jira")

app = FastAPI(title="Mock Jira Server")

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
    return get_ui_html("jira")

# In-memory storage seeded with data soon
TICKETS: Dict[str, dict] = {}
PROJECT_COUNTERS: Dict[str, int] = {}

class CreateIssueRequest(BaseModel):
    fields: dict

class CommentRequest(BaseModel):
    body: str

@app.on_event("startup")
async def load_seed_data():
    # TODO: Load from seed_data/jira.yaml
    logger.info("Jira Mock Server started.")
    pass

@app.get("/rest/api/3/issue/{issue_id_or_key}")
async def get_issue(issue_id_or_key: str):
    logger.info(f"GET /rest/api/3/issue/{issue_id_or_key}")
    if issue_id_or_key not in TICKETS:
        raise HTTPException(status_code=404, detail="Issue not found")
    return TICKETS[issue_id_or_key]

@app.post("/rest/api/3/issue")
async def create_issue(request: CreateIssueRequest):
    project_key = request.fields.get("project", {}).get("key", "TEST")
    count = PROJECT_COUNTERS.get(project_key, 0) + 1
    PROJECT_COUNTERS[project_key] = count
    
    key = f"{project_key}-{count}"
    
    new_ticket = {
        "id": "100" + str(count),
        "key": key,
        "fields": request.fields,
    }
    TICKETS[key] = new_ticket
    
    logger.info(f"POST /rest/api/3/issue created {key}")
    return {"id": new_ticket["id"], "key": key, "self": f"http://localhost:8081/rest/api/3/issue/{key}"}

@app.post("/rest/api/3/issue/{issue_id_or_key}/comment")
async def add_comment(issue_id_or_key: str, request: CommentRequest):
    logger.info(f"POST /rest/api/3/issue/{issue_id_or_key}/comment")
    if issue_id_or_key not in TICKETS:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    if "comment" not in TICKETS[issue_id_or_key]["fields"]:
        TICKETS[issue_id_or_key]["fields"]["comment"] = {"comments": []}
        
    comment_id = str(len(TICKETS[issue_id_or_key]["fields"]["comment"]["comments"]) + 1)
    comment = {
        "id": comment_id,
        "body": request.body,
        "author": {"displayName": "workbuddy"},
        "created": "2023-01-01T12:00:00.000+0000"
    }
    TICKETS[issue_id_or_key]["fields"]["comment"]["comments"].append(comment)
    return comment

@app.put("/rest/api/3/issue/{issue_id_or_key}")
async def update_issue(issue_id_or_key: str, request: Request):
    logger.info(f"PUT /rest/api/3/issue/{issue_id_or_key}")
    if issue_id_or_key not in TICKETS:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    body = await request.json()
    fields = body.get("fields", {})
    TICKETS[issue_id_or_key]["fields"].update(fields)
    
    return "", 204

@app.get("/rest/api/3/search")
async def search_issues(jql: str = "", startAt: int = 0, maxResults: int = 50):
    logger.info(f"GET /rest/api/3/search jql={jql}")
    # Simple mock search returning all tickets
    issues = list(TICKETS.values())
    return {
        "startAt": startAt,
        "maxResults": maxResults,
        "total": len(issues),
        "issues": issues[startAt:startAt+maxResults]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("jira_server:app", host="0.0.0.0", port=8081, reload=True)

@app.get("/health")
async def health():
    return {"status": "ok"}
