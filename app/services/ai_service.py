import json
import logging
from typing import Dict, Any, Tuple
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.models.schemas import AnalyzeResponse, Flags, FlagDetail, CostEstimate

logger = logging.getLogger("trustline")

class AIService:
    @classmethod
    def get_openai_client(cls) -> Tuple[AsyncOpenAI, bool]:
        """
        Check if a valid OpenAI API key is set, and return client.
        Returns (client, is_valid).
        """
        key = settings.OPENAI_API_KEY
        if not key or key == "your_api_key_here" or key.strip() == "":
            return None, False
        return AsyncOpenAI(api_key=key), True

    @classmethod
    def get_fallback_payload(cls, content: str, content_type: str, lite_mode: bool) -> AnalyzeResponse:
        """
        Returns a high-fidelity mock analysis response based on heuristics when OpenAI API is disabled or not set.
        This allows testing the app's full workflow and schema matching out-of-the-box.
        """
        content_stripped = content.strip()
        
        # 1. Check if the text is too short / ambiguous (Low confidence fallback)
        if len(content_stripped) < 15:
            fallback_flag = FlagDetail(
                flagged=False,
                severity="not_enough_info",
                explanation="Not enough information to verify (input text is too short or ambiguous)."
            )
            return AnalyzeResponse(
                content_type=content_type,
                extracted_text=content if content_type == "url" else None,
                traffic_light="yellow",
                overall_risk_score=50,
                lite_mode=lite_mode,
                flags=Flags(
                    emotional_manipulation=fallback_flag,
                    missing_sources_context=fallback_flag,
                    synthetic_text_signals=fallback_flag,
                    logical_fallacies=fallback_flag
                ),
                correction_snippet="I'm not sure if this is accurate, but the text is too short to verify. Let's make sure to cross-check sources before forwarding!",
                cost_estimate=CostEstimate(tokens_prompt=0, tokens_completion=0, cost_usd=0.0)
            )

        # 2. Heuristic check for common sensationalist text
        content_lower = content_stripped.lower()
        
        # Flag indicators
        emotional_manip = False
        missing_sources = False
        synthetic_signals = False
        logical_fallacy = False
        
        emotional_reason = "No signs of loaded language or sensationalism detected."
        missing_sources_reason = "The text does not present major unverified claims needing external citations."
        synthetic_reason = "Writing style exhibits natural variability, human rhythm, and context."
        fallacy_reason = "No systemic logical fallacies (e.g., ad hominem, fake authority) were identified."
        
        # High Risk Patterns (Scams, panic forwarding, extreme claims)
        if any(w in content_lower for w in ["congratulations", "won a prize", "click here", "forward to", "whatsapp group", "secret recipe", "miracle cure"]):
            emotional_manip = True
            emotional_reason = "Flagged for loaded language, urgency triggers ('forward to'), and sensationalized promises."
            
            missing_sources = True
            missing_sources_reason = "Flagged for making sensational claims ('miracle cure', 'won a prize') with zero external citations, links, or verifiable sources."
            
            synthetic_signals = True
            synthetic_reason = "Signals commonly associated with synthetic text: repetitive phrasing and generic structures typical of automated spam templates."
            
            logical_fallacy = True
            fallacy_reason = "Flagged for Appeal to Emotion and False Authority fallacies."
            
            traffic_light = "red"
            risk_score = 90
            correction_snippet = "Hey, this message looks like it might contain misleading information (it uses urgent language and doesn't back up its claims). Let's avoid forwarding it until we can verify it from a trusted news source."

        # Moderate Risk Patterns (Conspiracies, weak citations, general claims)
        elif any(w in content_lower for w in ["they say", "scientists found", "government hiding", "shocking truth", "is artificial", "breaking:"]):
            emotional_manip = True
            emotional_reason = "Flagged for conspiracy-leaning framing ('government hiding') and sensational headlines ('breaking')."
            
            missing_sources = True
            missing_sources_reason = "Flagged for using vague source citations ('they say', 'scientists found') without providing specific verifiable references."
            
            logical_fallacy = True
            fallacy_reason = "Flagged for Appeal to Anonymous Authority ('they say') and Strawman argumentation."
            
            traffic_light = "yellow"
            risk_score = 65
            correction_snippet = "Hey, this claim about scientists/sources is a bit vague. It doesn't cite specific studies or publications. Let's make sure to verify it from an official source before sharing it further."

        # Low Risk (Normal readable news, typical text)
        else:
            traffic_light = "green"
            risk_score = 15
            correction_snippet = "This text appears to be low risk. However, it's always good practice to double-check sources if you plan on sharing it."

        # Package the flags
        flags = Flags(
            emotional_manipulation=FlagDetail(
                flagged=emotional_manip,
                severity="high" if emotional_manip else "low",
                explanation=emotional_reason
            ),
            missing_sources_context=FlagDetail(
                flagged=missing_sources,
                severity="high" if missing_sources else "low",
                explanation=missing_sources_reason
            ),
            synthetic_text_signals=FlagDetail(
                flagged=synthetic_signals,
                severity="medium" if synthetic_signals else "low",
                explanation=synthetic_reason
            ),
            logical_fallacies=FlagDetail(
                flagged=logical_fallacy,
                severity="medium" if logical_fallacy else "low",
                explanation=fallacy_reason
            )
        )
        
        return AnalyzeResponse(
            content_type=content_type,
            extracted_text=content if content_type == "url" else None,
            traffic_light=traffic_light,
            overall_risk_score=risk_score,
            lite_mode=lite_mode,
            flags=flags,
            correction_snippet=correction_snippet,
            cost_estimate=CostEstimate(tokens_prompt=0, tokens_completion=0, cost_usd=0.0)
        )

    @classmethod
    async def analyze_text(cls, content: str, content_type: str, lite_mode: bool) -> AnalyzeResponse:
        """
        Analyze a text string or scraped website content.
        Uses OpenAI if the key is available, else falls back to local high-fidelity heuristics.
        """
        content_stripped = content.strip()
        
        # Immediate fallback for extremely short inputs (saves token costs and avoids incorrect guesses)
        if len(content_stripped) < 15:
            response = cls.get_fallback_payload(content, content_type, lite_mode)
            limiter.record_request(cost=0.0, is_fallback=True, is_scraped=(content_type == "url"))
            return response

        client, is_api_available = cls.get_openai_client()
        
        if not is_api_available:
            logger.info("OpenAI API key not configured. Using local fallback simulation engine.")
            response = cls.get_fallback_payload(content, content_type, lite_mode)
            limiter.record_request(cost=0.0, is_fallback=True, is_scraped=(content_type == "url"))
            return response

        # If API is available, construct the prompt
        system_prompt = (
            "You are an expert Media and Information Literacy (MIL) assistant analyzing text to verify its credibility. "
            "Your output must follow a strict JSON schema. Detect and output: \n"
            "1. 'emotional_manipulation': Sensationalism, loaded language, fear-mongering. "
            "Check if loaded words are used to drive panic/clicks.\n"
            "2. 'missing_sources_context': Claims lacking links, references, or specific details. "
            "Highlight if assertions are completely unverified.\n"
            "3. 'synthetic_text_signals': Patterns commonly associated with AI/synthetic text (e.g. extreme repetition, "
            "highly generic structure). DO NOT give a binary verdict ('this is AI'), rather describe signals/patterns.\n"
            "4. 'logical_fallacies': Systemic fallacies like ad hominem, false authority, strawman.\n\n"
            "For each flag, assign:\n"
            "- 'flagged': true or false\n"
            "- 'severity': 'low', 'medium', 'high', or 'not_enough_info'\n"
            "- 'explanation': educational explanation teaching the user what signals were found and why it is flagged.\n\n"
            "LOW-CONFIDENCE FALLBACK: If the text is ambiguous, too short, in a language you cannot parse, or you lack confidence, "
            "set 'severity' to 'not_enough_info' and 'explanation' to 'Not enough information to verify' for that flag.\n\n"
            "Also return:\n"
            "- 'traffic_light': 'green' (🟢 Low Risk), 'yellow' (🟡 Moderate Risk), or 'red' (🔴 High Risk).\n"
            "- 'overall_risk_score': an integer from 0 to 100 consolidated risk level.\n"
            "- 'correction_snippet': a concise, polite, fact-based correction snippet to copy-paste back into a group chat."
        )

        user_content = f"Analyze the following {content_type} content:\n\n{content}"

        # We will use OpenAI Structured Outputs
        try:
            # Pricing for gpt-4o-mini
            input_rate = 0.15 / 1_000_000  # $0.15 per 1M prompt tokens
            output_rate = 0.60 / 1_000_000  # $0.60 per 1M completion tokens
            
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "analysis_result",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "traffic_light": {"type": "string", "enum": ["green", "yellow", "red"]},
                            "overall_risk_score": {"type": "integer"},
                            "flags": {
                                "type": "object",
                                "properties": {
                                    "emotional_manipulation": {
                                        "type": "object",
                                        "properties": {
                                            "flagged": {"type": "boolean"},
                                            "severity": {"type": "string", "enum": ["low", "medium", "high", "not_enough_info"]},
                                            "explanation": {"type": "string"}
                                        },
                                        "required": ["flagged", "severity", "explanation"],
                                        "additionalProperties": False
                                    },
                                    "missing_sources_context": {
                                        "type": "object",
                                        "properties": {
                                            "flagged": {"type": "boolean"},
                                            "severity": {"type": "string", "enum": ["low", "medium", "high", "not_enough_info"]},
                                            "explanation": {"type": "string"}
                                        },
                                        "required": ["flagged", "severity", "explanation"],
                                        "additionalProperties": False
                                    },
                                    "synthetic_text_signals": {
                                        "type": "object",
                                        "properties": {
                                            "flagged": {"type": "boolean"},
                                            "severity": {"type": "string", "enum": ["low", "medium", "high", "not_enough_info"]},
                                            "explanation": {"type": "string"}
                                        },
                                        "required": ["flagged", "severity", "explanation"],
                                        "additionalProperties": False
                                    },
                                    "logical_fallacies": {
                                        "type": "object",
                                        "properties": {
                                            "flagged": {"type": "boolean"},
                                            "severity": {"type": "string", "enum": ["low", "medium", "high", "not_enough_info"]},
                                            "explanation": {"type": "string"}
                                        },
                                        "required": ["flagged", "severity", "explanation"],
                                        "additionalProperties": False
                                    }
                                },
                                "required": ["emotional_manipulation", "missing_sources_context", "synthetic_text_signals", "logical_fallacies"],
                                "additionalProperties": False
                            },
                            "correction_snippet": {"type": "string"}
                        },
                        "required": ["traffic_light", "overall_risk_score", "flags", "correction_snippet"],
                        "additionalProperties": False
                    }
                }
            }

            completion = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format=response_format,
                temperature=0.2
            )

            response_text = completion.choices[0].message.content
            parsed_json = json.loads(response_text)

            prompt_tokens = completion.usage.prompt_tokens if completion.usage else 0
            completion_tokens = completion.usage.completion_tokens if completion.usage else 0
            cost = (prompt_tokens * input_rate) + (completion_tokens * output_rate)

            # Record stats
            limiter.record_request(cost=cost, is_fallback=False, is_scraped=(content_type == "url"))

            # Build Flags objects
            f_data = parsed_json["flags"]
            flags = Flags(
                emotional_manipulation=FlagDetail(**f_data["emotional_manipulation"]),
                missing_sources_context=FlagDetail(**f_data["missing_sources_context"]),
                synthetic_text_signals=FlagDetail(**f_data["synthetic_text_signals"]),
                logical_fallacies=FlagDetail(**f_data["logical_fallacies"])
            )

            return AnalyzeResponse(
                content_type=content_type,
                extracted_text=content if content_type == "url" else None,
                traffic_light=parsed_json["traffic_light"],
                overall_risk_score=parsed_json["overall_risk_score"],
                lite_mode=lite_mode,
                flags=flags,
                correction_snippet=parsed_json["correction_snippet"],
                cost_estimate=CostEstimate(
                    tokens_prompt=prompt_tokens,
                    tokens_completion=completion_tokens,
                    cost_usd=cost
                )
            )

        except Exception as e:
            logger.error(f"Error invoking OpenAI API: {str(e)}. Falling back to local simulation.")
            response = cls.get_fallback_payload(content, content_type, lite_mode)
            limiter.record_request(cost=0.0, is_fallback=True, is_scraped=(content_type == "url"))
            return response
