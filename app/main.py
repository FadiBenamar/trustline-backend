from fastapi import FastAPI
from app.routes.analysis import router as analysis_router

app = FastAPI(title="TrustLine Backend")

app.include_router(analysis_router)

@app.get("/health")
def health():
    return {"status": "ok"}
