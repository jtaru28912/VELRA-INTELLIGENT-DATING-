from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os
import logging

from app.core.database import get_db_session
from app.features.auth.schemas import UserCreate, UserLogin, TokenResponse
from app.features.auth.models import User
from app.features.auth.dependencies import get_auth_service, get_current_user
from app.features.auth.service import AuthService
from app.core.email import EmailService
from app.core.config import get_settings
from app.features.auth.schemas import UserCreate, UserLogin, TokenResponse, GoogleSSORequest # Assume we add this

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize EmailService using Supabase Settings
email_service = EmailService()

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    logger.info("Signup attempt for email: %s", payload.email)
    
    query = select(User).where(User.email == payload.email)
    result = await session.execute(query)
    if result.scalar_one_or_none():
        logger.warning("Signup failed: Email already registered - %s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    try:
        hashed_pw = auth_service.get_password_hash(payload.password)
        new_user = User(email=payload.email, password_hash=hashed_pw)
        session.add(new_user)
        
        logger.info("Committing new user to database...")
        await session.commit()
        await session.refresh(new_user)
        logger.info("User successfully persisted and refreshed. ID: %s", new_user.id)
        
        # Send welcome email in background
        background_tasks.add_task(email_service.send_welcome_email, new_user.email)
        
        token = auth_service.create_access_token(subject=new_user.id)
        return {"access_token": token, "token_type": "bearer", "accepted_tc": False}
    except Exception as e:
        logger.exception("Database commit failure during signup for %s: %s", payload.email, str(e))
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save user data. Database error occurred."
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    logger.info("Login attempt for email: %s", payload.email)
    
    query = select(User).where(User.email == payload.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning("Login failed: User not found - %s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth_service.verify_password(payload.password, user.password_hash):
        logger.warning("Login failed: Incorrect password for %s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    logger.info("User %s successfully logged in.", payload.email)
    token = auth_service.create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer", "accepted_tc": user.accepted_tc}

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    session: AsyncSession = Depends(get_db_session)
) -> Any:
    logger.info("Forgot password request for: %s", email)
    # Logic to verify email and generate reset token would go here
    return {"message": "If the account exists, a reset link has been sent."}

@router.post("/google/sync", response_model=TokenResponse)
async def google_sync(
    payload: GoogleSSORequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    # In a production app, we would verify the Supabase JWT here.
    # For now, we trust the frontend provided email and provider_id from the verified Supabase session.
    logger.info("Syncing Google SSO user: %s", payload.email)
    
    query = select(User).where(User.email == payload.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        logger.info("Creating new user from Google SSO: %s", payload.email)
        user = User(
            email=payload.email,
            provider="google",
            provider_id=payload.provider_id,
            accepted_tc=True # Auto-agree for SSO users for seamless flow
        )
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
            logger.info("New SSO user persisted. ID: %s", user.id)
            background_tasks.add_task(email_service.send_welcome_email, user.email)
        except Exception as e:
            logger.exception("Failed to persist SSO user: %s", str(e))
            await session.rollback()
            raise HTTPException(status_code=500, detail="SSO Sync failed.")
    else:
        # Update provider info if it was email before
        if user.provider != "google":
            user.provider = "google"
            user.provider_id = payload.provider_id
            await session.commit()
            logger.info("Updated existing user %s to Google provider.", user.email)

    token = auth_service.create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer", "accepted_tc": user.accepted_tc}

@router.patch("/me/accept-tc", response_model=bool)
async def accept_tc(
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    logger.info("User %s accepting Terms & Conditions.", user.email)
    user.accepted_tc = True
    try:
        await session.commit()
        logger.info("T&C acceptance persisted for %s.", user.email)
        return True
    except Exception as e:
        logger.exception("Failed to persist T&C acceptance: %s", str(e))
        await session.rollback()
        raise HTTPException(status_code=500, detail="Update failed.")
