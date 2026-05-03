from pydantic import BaseModel, Field

class FeedbackRequest(BaseModel):
    analysis_id: str
    is_helpful: bool

class LearningPatternStats(BaseModel):
    pattern: str
    success_rate: float
    occurrences: int
