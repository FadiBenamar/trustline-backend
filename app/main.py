import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.analysis import router as analysis_router
from app.routes.webhook_mock import router as webhook_router
from app.routes.admin import router as admin_router

app = FastAPI(
    title="TrustLine MIL Engine & Platform",
    description="FastAPI backend and interactive frontend for processing Media Information Literacy (MIL) evaluations, synthetic signals, and fact verification.",
    version="1.0.0"
)

# Enable CORS for cross-origin frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers FIRST
app.include_router(analysis_router)
app.include_router(webhook_router)
app.include_router(admin_router)

@app.get("/health", tags=["System Health"])
def health():
    """
    Simple system health probe.
    """
    return {"status": "healthy", "service": "TrustLine Engine & Platform"}

# Mount frontend static web application at root '/' LAST
frontend_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
frontend_path = os.path.join(frontend_root, "dist")
if not os.path.exists(frontend_path):
    frontend_path = frontend_root
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
