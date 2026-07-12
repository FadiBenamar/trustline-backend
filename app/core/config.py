import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Rate Limiting configuration
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
    
    # Cost limit protection
    TOTAL_COST_CAP_USD: float = float(os.getenv("TOTAL_COST_CAP_USD", "10.00"))
    
    # App running mode
    APP_ENV: str = os.getenv("APP_ENV", "development")

settings = Settings()
