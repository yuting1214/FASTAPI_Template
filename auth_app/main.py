from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from typing import Callable
from datetime import timedelta
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory="auth_app/templates")
app.mount("/static", StaticFiles(directory="auth_app/static"), name="static")

@app.middleware("http")
async def add_doc_protect(request: Request, call_next):
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        if not request.session.get('authenticated'):
            return RedirectResponse(url="/")
    response = await call_next(request)
    return response
# Add session middleware with a custom expiration time (e.g., 30 minutes)
app.add_middleware(SessionMiddleware, 
                   secret_key="your_secret_key", 
                   max_age=1800)  # 1800 seconds = 30 minutes

# Custom middleware to protect specific paths
# class AuthMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app: ASGIApp, dispatch: Callable):
#         super().__init__(app)
#         self.dispatch = dispatch

#     async def dispatch(self, request: Request, call_next):
#         if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
#             if not request.session.get('authenticated'):
#                 return RedirectResponse(url="/")
#         response = await call_next(request)
#         return response


@app.get("/", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "user" and password == "pass":
        request.session['authenticated'] = True
        return RedirectResponse(url="/docs", status_code=303)
    else:
        message = "Invalid credentials"
        return templates.TemplateResponse("login.html", {"request": request, "message": message})

@app.get("/target", response_class=HTMLResponse)
async def read_target(request: Request):
    if not request.session.get('authenticated'):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("target.html", {"request": request})

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

if __name__ == "__main__":
    # mounting at the root path
    uvicorn.run(
        app="auth_app.main:app"
    )