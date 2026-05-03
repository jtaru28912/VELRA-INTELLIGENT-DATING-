from typing import Annotated
from pydantic import BaseModel, EmailStr, StringConstraints

class UserCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    accepted_tc: bool = False

class GoogleSSORequest(BaseModel):
    email: EmailStr
    provider_id: str
    access_token: str # Supabase session token

class UserUpdate(BaseModel):
    accepted_tc: bool
    sub: str | None = None
    exp: int | None = None
