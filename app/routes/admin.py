from fastapi import APIRouter
from app.core.rate_limiter import limiter

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/stats")
def get_admin_stats():
    """
    Retrieve real-time API request analytics, estimated costs,
    and rate limit thresholds.
    """
    return limiter.get_stats()

@router.post("/reset-stats")
def reset_admin_stats():
    """
    Reset usage tracking statistics. Helpful for testing iteration cycles.
    """
    limiter.total_cost_usd = 0.0
    limiter.total_requests = 0
    limiter.total_fallback_requests = 0
    limiter.total_scraped_urls = 0
    limiter.requests.clear()
    return {"message": "Admin tracking statistics have been reset successfully."}
