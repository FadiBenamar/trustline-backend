from pydantic import BaseModel, Field
from typing import Optional, Dict

class AnalyzeRequest(BaseModel):
    content: str = Field(..., description="The pasted raw text block or a direct URL to analyze.")
    lite_mode: bool = Field(False, description="Lite mode returns minimal styling data and avoids heavy payloads for low-bandwidth environments.")

class FlagDetail(BaseModel):
    flagged: bool = Field(..., description="True if this specific flag is raised based on severity.")
    severity: str = Field(..., description="Risk severity: 'low', 'medium', 'high', or 'not_enough_info'.")
    explanation: str = Field(..., description="Educational explanation of why the flag was raised, or fallback warning.")

class Flags(BaseModel):
    emotional_manipulation: FlagDetail = Field(..., description="Flags emotional manipulation like loaded language, sensationalism, or fear-mongering.")
    missing_sources_context: FlagDetail = Field(..., description="Flags claims that lack supporting evidence, sources, or proper context.")
    synthetic_text_signals: FlagDetail = Field(..., description="Detects signals/patterns commonly associated with synthetic (AI-generated) text.")
    logical_fallacies: FlagDetail = Field(..., description="Flags systemic cognitive flaws and fallacies (e.g. ad hominem, strawman).")

class CostEstimate(BaseModel):
    tokens_prompt: int = Field(0, description="Estimated input prompt tokens.")
    tokens_completion: int = Field(0, description="Estimated output completion tokens.")
    cost_usd: float = Field(0.0, description="Estimated cost of this request in USD.")

class AnalyzeResponse(BaseModel):
    content_type: str = Field(..., description="Determined content type: 'text' or 'url'.")
    extracted_text: Optional[str] = Field(None, description="The raw scraped text if a URL was provided.")
    traffic_light: str = Field(..., description="Overall Traffic-Light summary view: 'green' (🟢 Low Risk), 'yellow' (🟡 Moderate Risk), or 'red' (🔴 High Risk).")
    overall_risk_score: int = Field(..., description="Overall consolidated risk score (0 to 100).")
    lite_mode: bool = Field(False, description="Reflects if the request was processed in Lite Mode.")
    flags: Flags = Field(..., description="The four critical MIL flags with detailed diagnostics.")
    correction_snippet: str = Field(..., description="A concise, polite, fact-based correction snippet generated for copy/paste.")
    cost_estimate: CostEstimate = Field(..., description="API consumption and cost tracking statistics.")

class WebhookSimulateRequest(BaseModel):
    sender: str = Field("+123456789", description="Simulated phone number or username of the message sender.")
    message_body: str = Field(..., description="The contents of the message sent to the WhatsApp or Telegram webhook.")
    platform: str = Field("whatsapp", description="The simulated messaging platform: 'whatsapp' or 'telegram'.")

class WebhookSimulateResponse(BaseModel):
    success: bool = Field(..., description="Whether the simulation succeeded.")
    message: str = Field(..., description="Status message describing the webhook result.")
    analysis_summary: str = Field(..., description="Consolidated analysis result summary.")
    correction_snippet: str = Field(..., description="The polite fact-based correction text generated.")
    simulated_reply: str = Field(..., description="Simulated automatic reply sent back to the group chat.")
