from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalyzeChatRequest(BaseModel):
    messages: list[str] = Field(default=[], max_length=200)
    images: list[str] = Field(default=[], max_length=10) # base64 or urls
    context: str = Field(..., min_length=2, max_length=64)
    persona: str | None = None
    profile_id: str | None = None

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, value: list[str]) -> list[str]:
        cleaned = [message.strip() for message in value if message.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty message is required")
        return cleaned

    @field_validator("context")
    @classmethod
    def validate_context(cls, value: str) -> str:
        return value.strip().lower()


class FeatureExtractionResponse(BaseModel):
    avg_reply_time: float
    initiations: float
    message_length_trend: Literal["increasing", "decreasing"]
    sentiment_score: float
    future_mentions: int


class ScoreResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    flags: list[str]


# 1. Expert Analyst schema
class AIExpertAnalysis(BaseModel):
    seriousness_score: int = Field(..., ge=0, le=100)
    interest_level: str
    behavioral_pattern: list[str] = Field(..., min_length=1, max_length=2)
    reasoning: list[str] = Field(..., min_length=1, max_length=5)
    red_flags: list[str] = Field(..., description="Empty list if none")
    suggested_action: str
    alignment_score: int | None = None
    mismatch_reasons: list[str] = []


# 2. Interest Classification schema
class AIInterestClassification(BaseModel):
    interest_level: str
    confidence: float = Field(..., ge=0.0, le=1.0)


# 3. Reply Generation schema
class AIReplyGeneration(BaseModel):
    replies: list[str] = Field(..., min_length=2, max_length=2)


class BeforeYouMeet(BaseModel):
    behave: str
    tone: str
    talk_listen_ratio: str
    what_not_to_do: str

class AIExtendedAnalysis(BaseModel):
    emotional_investment_level: Literal["low", "guarded", "moderate", "high"]
    risk_level: Literal["low", "medium", "high"]
    recommendation: str
    reason: str
    date_type: Literal["coffee", "activity", "premium dinner", "drinks"]
    budget_range: str
    impression_strategy: list[str]
    emotional_strategy: list[str]
    risk_note: str
    what_they_like: list[str]
    what_to_avoid: list[str]
    conversation_topics: list[str]
    best_approach: str
    effort_level: Literal["low", "balanced", "high"]
    spending_advice: str
    emotional_advice: str
    overall_strategy: str
    before_you_meet: BeforeYouMeet

# 4. Guardrail Validation schema
class AIValidation(BaseModel):
    valid: bool
    issues: list[str]


class DateStrategy(BaseModel):
    budget: str = "$$"
    type: str = "coffee"
    justification: str = "Standard fallback recommendation"

class AIStrategyGeneration(BaseModel):
    seriousness_score: int = Field(..., ge=0, le=100)
    interest_level: str
    behavioral_pattern: list[str]
    emotional_investment: str
    risk_level: str
    evidence: list[str]
    reasoning: str
    date_budget: str
    date_type: str
    date_justification: str
    impression_strategy: list[str]
    suggestions: list[str]
    replies: list[str]
    effort_level: str
    should_go_on_date: bool
    date_decision_reason: str
    boredom_level: str
    psychological_insight: str
    gift_ideas: list[str]
    chat_ideas: list[str]


class AnalyzeChatResponse(BaseModel):
    seriousness_score: int
    interest_level: str
    behavioral_pattern: list[str]
    emotional_investment: str = "moderate"
    risk_level: str = "medium"
    evidence: list[str] = Field(..., description="3-5 behavioral evidences from the chat")
    reasoning: str = Field(..., description="Psychological reasoning for the analysis")
    date_strategy: DateStrategy
    impression_strategy: list[str] = []
    suggestions: list[str] = []
    replies: list[str] = []
    effort_level: str = "balanced"
    should_go_on_date: bool = True
    date_decision_reason: str = "The vibe is consistent and interest is verified."
    boredom_level: str = "low"
    psychological_insight: str = ""
    gift_ideas: list[str] = []
    chat_ideas: list[str] = []
    messages: list[str] = []


# --- TIPS ENGINE ---

class TipItem(BaseModel):
    title: str
    content: str
    category: Literal["topic", "gift", "strategy", "behavior"]

class TipsResponse(BaseModel):
    summary: str
    tips: list[TipItem]
    vibe_check: str


# --- DATE CALCULATOR ---

class DateCalculatorRequest(BaseModel):
    budget: str  # e.g. "$", "$$", "$$$"
    intent: str  # e.g. "casual", "serious", "first meet"
    location_pref: str | None = None

class DateCalculatorResponse(BaseModel):
    date_type: str
    budget_range: str
    justification: str
    plan: list[str]
    pro_tip: str

