from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analysis import router as analysis_router
from app.routes.webhook_mock import router as webhook_router
from app.routes.admin import router as admin_router

app = FastAPI(
    title="TrustLine Backend Engine",
    description="Decoupled FastAPI backend for processing Media Information Literacy (MIL) evaluations, synthetic signals, and facts.",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(analysis_router)
app.include_router(webhook_router)
app.include_router(admin_router)

@app.get("/health", tags=["System Health"])
def health():
    """
    Simple system health probe.
    """
    return {"status": "healthy", "service": "TrustLine Backend"}
