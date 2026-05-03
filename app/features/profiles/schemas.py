from typing import Literal
from pydantic import BaseModel, Field

class ProfileAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    source: Literal["instagram", "linkedin", "manual"]

class ProfileTraitsResponse(BaseModel):
    summary: str = Field(..., description="I have successfully evaluated [name] profile...")
    personality_type: str
    interests: list[str]
    lifestyle: str
    communication_style: str
    values: list[str]
    likely_preferences: list[str]

class ProfileDetailResponse(BaseModel):
    id: str
    source: str
    extracted_traits: ProfileTraitsResponse
