from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.scraper import ScraperService
from app.services.ai_service import AIService
from app.core.rate_limiter import rate_limit_dependency
import logging

logger = logging.getLogger("trustline")

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/", response_model=AnalyzeResponse, dependencies=[Depends(rate_limit_dependency)])
async def analyze_content(data: AnalyzeRequest):
    """
    Ingest text or a direct URL and process it through the structured Media Nutrition Label Engine.
    Tracks content type and applies rate limiting checks.
    """
    content = data.content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content field cannot be empty."
        )

    # Step 1: Detect and handle URL inputs
    is_url_input = ScraperService.is_url(content)
    content_type = "url" if is_url_input else "text"
    
    extracted_text = None
    if is_url_input:
        logger.info(f"URL detected: {content}. Triggering scraping engine.")
        try:
            extracted_text = await ScraperService.scrape_url(content)
            analysis_text = extracted_text
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to extract content from URL: {str(e)}"
            )
    else:
        analysis_text = content

    # Step 2: Run the AI/ML text parsing engine
    logger.info("Executing text analysis engine.")
    try:
        response = await AIService.analyze_text(
            content=analysis_text,
            content_type=content_type,
            lite_mode=data.lite_mode
        )
        
        # If we scraped a URL, populate the raw text in response
        if is_url_input:
            response.extracted_text = extracted_text
            
        return response
    except Exception as e:
        logger.error(f"Analysis engine failure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
