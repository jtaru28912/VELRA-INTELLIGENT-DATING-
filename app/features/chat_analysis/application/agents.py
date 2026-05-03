from app.features.chat_analysis.domain.models import ExtractedFeatures
from app.features.chat_analysis.schemas import AnalyzeChatResponse, DateStrategy
from app.core.openai_client import OpenAIClient
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class AIStrategyGeneration(BaseModel):
    seriousness_score: int
    interest_level: str
    behavioral_pattern: list[str]
    emotional_investment: str
    risk_level: str
    evidence: list[str] = Field(..., description="Extract 3-5 specific behavioral evidences from the chat history")
    reasoning: str = Field(..., description="Specific psychological reasoning for this chat")
    date_budget: str
    date_type: str
    date_justification: str
    impression_strategy: list[str]
    suggestions: list[str]
    replies: list[str] = []
    effort_level: str = "balanced"
    should_go_on_date: bool = True
    date_decision_reason: str = "The vibe is consistent and interest is verified."
    boredom_level: str = "low"
    psychological_insight: str = ""

class StrategyGeneratorAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    async def execute(self, features: dict, prediction_interest: str, seriousness_score: int, history: str = "") -> tuple[AnalyzeChatResponse, dict]:
        # Improved, more diverse fallback content
        fallback_response = AnalyzeChatResponse(
            seriousness_score=seriousness_score,
            interest_level=prediction_interest,
            behavioral_pattern=["Complex Interaction Vibe"],
            emotional_investment= "moderate" if seriousness_score > 30 else "low",
            risk_level="Safe",
            date_strategy=DateStrategy(
                budget="$$", 
                type="Coffee or Drinks", 
                justification="Keep it casual to verify the digital chemistry in person."
            ),
            impression_strategy=[
                "Match their reply length: It signals subconscious synchronization.",
                "Use their specific emojis: It creates a mirror effect in their mind.",
                "The 3-hour delay: Use this on your next reply to re-establish value."
            ],
            suggestions=["Maintain the mystery by not over-explaining your day."],
            replies=["I like your energy, maybe we should bring that to real life?", "You're surprisingly easy to decode."],
            evidence=["Consistent reply timing", "Use of enthusiastic emojis"],
            reasoning="The interaction shows healthy engagement with no immediate red flags.",
            effort_level="balanced",
            boredom_level="Low",
            psychological_insight="They are testing your consistency before dropping their guard."
        )

        if not self.openai_client.enabled:
            return fallback_response, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        system_prompt = (
            "You are a Senior Human Psychology & Behavioral Intelligence Engine.\n"
            f"The ML subsystem already predicted their interest level as '{prediction_interest}'.\n"
            "Build the final engagement strategy for the user.\n"
            "STRICT RULES:\n"
            "- EVIDENCE ENGINE: You MUST extract 3-5 specific 'behavioral evidences' from the chat (e.g., 'Replied in 2 mins to a complex question', 'Used high-investment emojis', 'Specific future mention of seeing you').\n"
            "- REASONING: Provide a paragraph of 'psychological reasoning' explaining the 'why' behind the scores.\n"
            "- DEEP PSYCHOLOGY: Identify triggers like 'Seeking Validation', 'Avoidant Attachment', 'Breadcrumbing'.\n"
            "- BOREDOM DETECTION: Provide 'boredom_level' (Low, Medium, High).\n"
            "- PERSONALIZATION: 3 UNIQUE psychological power moves (impression_strategy).\n"
            "- TONE: Flirty, poetic, direct Gen-Z vibe.\n"
            "- RESPONSE LANGUAGE: Use the EXACT dialect/language of the input chat.\n"
        )
        
        payload = {
            "features": features,
            "prediction_interest": prediction_interest,
            "score": seriousness_score,
            "chat_history": history
        }

        try:
            res = await self.openai_client.generate_structured(
                system_prompt=system_prompt,
                user_payload=payload,
                response_model=AIStrategyGeneration,
            )
            data: AIStrategyGeneration = AIStrategyGeneration.model_validate(res.payload)
            usage = res.usage
        except Exception as e:
            logger.error(f"Strategy generation failed: {e}")
            return fallback_response, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        response = AnalyzeChatResponse(
            seriousness_score=data.seriousness_score,
            interest_level=data.interest_level,
            behavioral_pattern=data.behavioral_pattern,
            emotional_investment=data.emotional_investment,
            risk_level=data.risk_level,
            evidence=data.evidence,
            reasoning=data.reasoning,
            date_strategy=DateStrategy(
                budget=data.date_budget,
                type=data.date_type,
                justification=data.date_justification
            ),
            impression_strategy=data.impression_strategy,
            suggestions=data.suggestions,
            replies=data.replies,
            effort_level=data.effort_level,
            should_go_on_date=data.should_go_on_date,
            date_decision_reason=data.date_decision_reason,
            boredom_level=data.boredom_level,
            psychological_insight=data.psychological_insight
        )
        return response, usage
