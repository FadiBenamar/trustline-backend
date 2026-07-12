from fastapi import APIRouter, HTTPException, status
from app.models.schemas import WebhookSimulateRequest, WebhookSimulateResponse
from app.services.ai_service import AIService
from app.services.scraper import ScraperService
import logging

logger = logging.getLogger("trustline")

router = APIRouter(prefix="/mock", tags=["Webhook Mocks"])

@router.post("/webhook", response_model=WebhookSimulateResponse)
async def simulate_webhook(data: WebhookSimulateRequest):
    """
    Simulate a webhook trigger from Telegram or WhatsApp.
    This demonstrates the out-of-app distribution loop ('Act' step) in hackathon demos.
    """
    body = data.message_body.strip()
    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message body cannot be empty."
        )

    platform_name = data.platform.lower()
    if platform_name not in ("whatsapp", "telegram"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform must be either 'whatsapp' or 'telegram'."
        )

    # Detect if content is URL
    is_url = ScraperService.is_url(body)
    content_type = "url" if is_url else "text"

    try:
        # If it's a URL, fetch content first
        if is_url:
            text_to_analyze = await ScraperService.scrape_url(body)
        else:
            text_to_analyze = body

        # Perform analysis (rate limiter bypassed for mocks or counts? Let's bypass to keep it friendly for demos)
        analysis = await AIService.analyze_text(
            content=text_to_analyze,
            content_type=content_type,
            lite_mode=False
        )

        traffic_light_mapping = {
            "green": "🟢 Low Risk",
            "yellow": "🟡 Moderate Risk",
            "red": "🔴 High Risk"
        }
        risk_label = traffic_light_mapping.get(analysis.traffic_light, "Unknown Risk")

        # Create simulated bot auto-response message
        simulated_reply = (
            f"🔍 *TrustLine Verification* on *{platform_name.capitalize()}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Analysis result: *{risk_label}*\n"
            f"Consolidated Risk Score: *{analysis.overall_risk_score}/100*\n\n"
            f"💡 *Polite Fact-Correction (Copy to clipboard/forward):*\n"
            f"\"{analysis.correction_snippet}\"\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🎓 *Media Literacy Tip:* Check sources before forwarding sensational information."
        )

        analysis_summary = f"Analyzed message from {data.sender}. Risk: {risk_label} ({analysis.overall_risk_score}/100)."

        return WebhookSimulateResponse(
            success=True,
            message=f"Successfully simulated webhook incoming message for {platform_name}.",
            analysis_summary=analysis_summary,
            correction_snippet=analysis.correction_snippet,
            simulated_reply=simulated_reply
        )

    except Exception as e:
        logger.error(f"Webhook simulation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook simulation failed: {str(e)}"
        )
