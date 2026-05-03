import asyncio
import uuid
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import engine
from app.features.auth.models import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

async def test_insert():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        user = User(
            id=str(uuid.uuid4()),
            email=f'test_db_error_{uuid.uuid4()}@gmail.com',
            provider="google",
            provider_id='123456',
            accepted_tc=True
        )
        session.add(user)
        try:
            await session.commit()
            print("SUCCESS")
        except Exception as e:
            print(f"ERROR: {type(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_insert())
