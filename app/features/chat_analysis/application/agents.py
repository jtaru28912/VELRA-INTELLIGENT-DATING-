from app.features.chat_analysis.schemas import AnalyzeChatResponse, DateStrategy, AIStrategyGeneration
from app.core.openai_client import OpenAIClient
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class StrategyGeneratorAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    async def execute(self, features: dict, prediction_interest: str, seriousness_score: int, history: str = "", persona: str = "") -> tuple[AnalyzeChatResponse, dict]:
        # Improved fallback with more context-aware defaults
        fallback_response = AnalyzeChatResponse(
            seriousness_score=seriousness_score,
            interest_level=prediction_interest,
            behavioral_pattern=["Engagement Analysis Pending"],
            emotional_investment= "moderate" if seriousness_score > 30 else "low",
            risk_level="Safe",
            date_strategy=DateStrategy(
                budget="$$", 
                type="Casual Meetup", 
                justification="Analysis failed to generate personalized strategy. Falling back to safety baseline."
            ),
            impression_strategy=[
                "Maintain your current energy level until deeper analysis is available.",
                "Focus on open-ended questions about their values.",
                "Let the conversation breathe."
            ],
            suggestions=["Wait for more behavioral signals before investing emotionally."],
            replies=["That's a nice compliment, thank you.", "I appreciate you saying that."],
            evidence=["Manual review required for linguistic subtext."],
            reasoning="The AI model encountered a parsing error during this specific analysis.",
            effort_level="balanced",
            boredom_level="Low",
            psychological_insight="This interaction requires human intuition for accurate decoding.",
            gift_ideas=["A thoughtful recommendation", "An experience mentioned in chat"],
            chat_ideas=["Ask about their favorite weekend activities", "Share a funny recent story"],
            messages=[]
        )

        if not self.openai_client.enabled:
            return fallback_response, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        system_prompt = f"""You are the Velra AI 'Psychological Profiler' – an elite expert in Gen-Z dating and human behavioral subtext.
Your mission is to perform a 'deep-tissue' analysis of the provided chat history.

EVALUATION GOAL & CONTEXT:
User's Context: "{persona or 'Not provided'}"
You MUST evaluate the chat history specifically against the user's goals. 

PSYCHOLOGICAL FRAMEWORK:
1. Phase Identification: Determine if they are in 'Attraction Phase' (focused on body/looks), 'Comfort Phase' (sharing stories), or 'Investment Phase' (future planning).
2. Intent Decoding: Distinguish between 'Physical Desire' and 'Emotional Serious Intent'. If they only compliment physical traits (body, hair) and use sexual language, they are likely in the Attraction/Casual phase.
3. Nature vs. Appearance: Call out if they have mentioned the user's personality or nature at all.
4. Tactical Timelines: Provide research-based timelines for when the user should invest or pull back.

CRITICAL RULES:
- BE BRUTALLY HONEST: If the guy just wants a hookup but the girl wants a relationship, say it.
- NO GENERIC PHRASES: Avoid "vibe is consistent". Use specific chat references.
- TONE: High-IQ, tactical, slightly edgy, and deeply human.

REQUIRED SCHEMA FIELDS:
- evidence: 3-5 specific linguistic proofs (e.g., 'Used body-focused compliments instead of personality-based ones').
- reasoning: 2-3 sentences of 'Why' they are acting this way.
- psychological_insight: One 'ego-shattering' realization about their intent.
- gift_ideas: 3 unique items based on their personality (not generic).
- chat_ideas: 3 hooks to test their commitment.
"""
        
        payload = {
            "features": features,
            "prediction_interest": prediction_interest,
            "score": seriousness_score,
            "chat_history": history,
            "user_goal": persona
        }

        try:
            res = await self.openai_client.generate_structured(
                system_prompt=system_prompt,
                user_payload=payload,
                response_model=AIStrategyGeneration,
            )
            data: AIStrategyGeneration = AIStrategyGeneration.model_validate(res.payload)
            usage = res.usage
            
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
                psychological_insight=data.psychological_insight,
                gift_ideas=data.gift_ideas,
                chat_ideas=data.chat_ideas
            )
            return response, usage
            
        except Exception as e:
            logger.error(f"Strategy generation failed: {e}", exc_info=True)
            return fallback_response, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
