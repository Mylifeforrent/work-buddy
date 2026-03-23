from fastapi import APIRouter, FastAPI, Form, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_sso")

app = FastAPI(title="Mock Corporate SSO")

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

router = APIRouter()
SESSIONS = set()

@router.get("/login", response_class=HTMLResponse)
async def login_page(redirect_url: str = "/"):
    """Show the SSO login page (React UI)."""
    logger.info(f"GET /login with redirect_url: {redirect_url}")
    return get_ui_html("sso")

@app.get("/", response_class=HTMLResponse)
async def root():
    return get_ui_html("sso")

@router.post("/login")
async def login_post(
    username: str = Form(...),
    password: str = Form(...),
    redirect_url: str = Form("/"),
):
    """Process login and set session cookie."""
    logger.info(f"POST /login user={username}")
    
    # Accept any username/password for mock purposes
    session_token = f"session_{username}_12345"
    SESSIONS.add(session_token)
    
    response = RedirectResponse(url=redirect_url, status_code=303)
    # Set a session cookie
    response.set_cookie(key="sso_session", value=session_token, httponly=True)
    return response

@router.get("/user")
async def get_current_user(request: Request):
    """Get the current authenticated user."""
    session_token = request.cookies.get("sso_session")
    if not session_token or session_token not in SESSIONS:
        return {"authenticated": False}
    
    # Extract username from mock token
    username = session_token.split("_")[1]
    return {"authenticated": True, "username": username}

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sso_server:app", host="0.0.0.0", port=8090, reload=True)

@app.get("/health")
async def health():
    return {"status": "ok"}
