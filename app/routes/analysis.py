from fastapi import APIRouter
from app.models.schemas import AnalyzeRequest

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/")
def analyze(data: AnalyzeRequest):
    return {
        "trust_score": 75,
        "risk_level": "medium",
        "message": "Demo response",
        "content": data.content
    }
