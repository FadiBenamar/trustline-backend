import time
from collections import defaultdict
from fastapi import HTTPException, Request, status
from app.core.config import settings

class SlidingWindowRateLimiter:
    def __init__(self):
        # Maps IP to list of timestamps
        self.requests = defaultdict(list)
        # Tracking usage stats
        self.total_cost_usd = 0.0
        self.total_requests = 0
        self.total_fallback_requests = 0
        self.total_scraped_urls = 0

    def is_rate_limited(self, ip: str) -> bool:
        current_time = time.time()
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        limit = settings.RATE_LIMIT_REQUESTS
        
        # Filter out timestamps outside the sliding window
        self.requests[ip] = [t for t in self.requests[ip] if current_time - t < window]
        
        if len(self.requests[ip]) >= limit:
            return True
            
        self.requests[ip].append(current_time)
        return False

    def check_cost_cap(self) -> bool:
        return self.total_cost_usd >= settings.TOTAL_COST_CAP_USD

    def record_request(self, cost: float = 0.0, is_fallback: bool = False, is_scraped: bool = False):
        self.total_requests += 1
        self.total_cost_usd += cost
        if is_fallback:
            self.total_fallback_requests += 1
        if is_scraped:
            self.total_scraped_urls += 1

    def get_stats(self):
        return {
            "total_requests": self.total_requests,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "total_fallback_requests": self.total_fallback_requests,
            "total_scraped_urls": self.total_scraped_urls,
            "cost_cap_usd": settings.TOTAL_COST_CAP_USD,
            "cost_cap_reached": self.check_cost_cap(),
            "rate_limit_requests": settings.RATE_LIMIT_REQUESTS,
            "rate_limit_window_seconds": settings.RATE_LIMIT_WINDOW_SECONDS
        }

# Global instance of the rate limiter & tracker
limiter = SlidingWindowRateLimiter()

def rate_limit_dependency(request: Request):
    # Enforce cost cap protection first
    if limiter.check_cost_cap():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="API Usage cost cap has been reached. Please contact backend admin to increase limits."
        )
        
    client_ip = request.client.host if request.client else "unknown"
    if limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down to prevent API cost issues."
        )
