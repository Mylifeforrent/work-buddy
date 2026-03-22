import logging
from typing import Optional

from fastapi import APIRouter, FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_sso")

app = FastAPI(title="Mock Corporate SSO")
router = APIRouter()

# Simple hardcoded session store
SESSIONS = set()

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Corporate SSO Login</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; }
        .login-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 300px; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; }
        input[type="text"], input[type="password"] { width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 0.75rem; background: #0052cc; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0047b3; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Corporate SSO</h2>
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Staff ID</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <input type="hidden" name="redirect_url" value="{redirect_url}">
            <button type="submit" id="submit">Sign In</button>
        </form>
    </div>
</body>
</html>
"""

@router.get("/login", response_class=HTMLResponse)
async def login_page(redirect_url: str = "/"):
    """Show the SSO login page."""
    logger.info(f"GET /login with redirect_url: {redirect_url}")
    return LOGIN_HTML.replace("{redirect_url}", redirect_url)

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
