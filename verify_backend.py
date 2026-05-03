import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from app.core.config import get_settings
from app.core.database import SessionLocal, init_database
from app.core.cache import RedisCache
from app.features.auth.models import User
from app.features.auth.service import AuthService
from sqlalchemy import select

async def verify():
    print("Starting Backend Verification...")
    settings = get_settings()
    
    # 1. DB Verification
    print("\n--- Phase 1: Database Test ---")
    await init_database()
    auth_service = AuthService(settings)
    
    test_email = "verify_db_v4@velra.ai"
    hashed_pw = auth_service.get_password_hash("VerificationPass123!")
    
    async with SessionLocal() as session:
        # Check if user exists
        query = select(User).where(User.email == test_email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            print(f"Found existing verification user: {test_email}")
        else:
            print(f"Creating new verification user: {test_email}")
            user = User(email=test_email, password_hash=hashed_pw)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"User created successfully in DB. ID: {user.id}")

    # 2. Unified Redis Verification
    print("\n--- Phase 2: Unified Cache Test ---")
    cache = RedisCache(settings)
    try:
        await cache.connect()
        if cache._mode:
            print(f"Unified Cache mode: {cache._mode}")
            test_key = "velra_unified_ping"
            test_data = {"status": "operational", "provider": cache._mode}
            
            print(f"Setting key: {test_key}")
            await cache.set_json(test_key, test_data, ttl_seconds=60)
            
            print("Retrieving key...")
            retrieved = await cache.get_json(test_key)
            
            if retrieved == test_data:
                print(f"Cache verification SUCCESS: {retrieved}")
            else:
                print(f"Cache verification FAILED. Got: {retrieved}")
        else:
            print("Cache not connected (No Upstash credentials and Local Redis down).")
    finally:
        await cache.close()
    
    print("\nVerification Complete!")

if __name__ == "__main__":
    asyncio.run(verify())
