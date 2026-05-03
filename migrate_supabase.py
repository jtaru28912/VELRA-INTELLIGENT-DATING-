import asyncio
from app.core.database import engine
from sqlalchemy import text

async def add_cols():
    print("Connecting to Supabase to update schema...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS provider TEXT DEFAULT 'email'"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS provider_id TEXT"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS accepted_tc BOOLEAN DEFAULT FALSE"))
            await conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL"))
            print("Successfully added columns (or they already exist).")
    except Exception as e:
        print(f"Schema update failed: {e}")

if __name__ == "__main__":
    asyncio.run(add_cols())
