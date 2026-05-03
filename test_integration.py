"""
Integration test: Tests the full auth + SSO sync flow against the live backend.
"""
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def test_health():
    print("\n--- Test 1: Health Check ---")
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        print(f"✅ Health: {r.json()}")

async def test_signup():
    print("\n--- Test 2: Email Signup ---")
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/auth/signup", json={
            "email": "integration_test_007@velra.ai",
            "password": "SecureTest123!"
        })
        if r.status_code == 201:
            data = r.json()
            print(f"✅ Signup SUCCESS. Token starts with: {data['access_token'][:20]}...")
            print(f"   accepted_tc: {data['accepted_tc']}")
            return data['access_token']
        elif r.status_code == 400 and "already registered" in r.text:
            print(f"⚠️  User already registered (expected on re-run). Logging in instead...")
            return await test_login()
        else:
            print(f"❌ Signup FAILED: {r.status_code} - {r.text}")
            return None

async def test_login():
    print("\n--- Test 2b: Email Login ---")
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "integration_test_007@velra.ai",
            "password": "SecureTest123!"
        })
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Login SUCCESS. accepted_tc: {data['accepted_tc']}")
            return data['access_token']
        else:
            print(f"❌ Login FAILED: {r.status_code} - {r.text}")
            return None

async def test_google_sso_sync():
    print("\n--- Test 3: Google SSO Sync ---")
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/auth/google/sync", json={
            "email": "sso_test_user@gmail.com",
            "provider_id": "google-uid-test-12345",
            "access_token": "mock_supabase_token_for_test"
        })
        if r.status_code == 200:
            data = r.json()
            print(f"✅ SSO Sync SUCCESS. Token starts with: {data['access_token'][:20]}...")
            print(f"   accepted_tc: {data['accepted_tc']}")
            return data['access_token']
        else:
            print(f"❌ SSO Sync FAILED: {r.status_code} - {r.text}")
            return None

async def test_protected_route(token: str):
    print("\n--- Test 4: Protected Route (Analyze Chat) ---")
    if not token:
        print("⚠️  Skipped: No token available.")
        return
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/analyze-chat",
            json={"messages": ["Hey, how are you?", "I'm fine, you?"], "context": "talking_stage"},
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 200:
            print(f"✅ Protected route SUCCESS. Got analysis response.")
        elif r.status_code == 401:
            print(f"❌ Auth FAILED (401). Token rejected.")
        else:
            print(f"⚠️  Got {r.status_code}: {r.text[:200]}")

async def test_db_users():
    print("\n--- Test 5: Verify Users in Supabase DB ---")
    import sys, os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app.core.database import SessionLocal, init_database
    from app.features.auth.models import User
    from sqlalchemy import select, func

    await init_database()
    async with SessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(User))
        count = result.scalar()
        print(f"✅ Supabase DB users table count: {count}")
        
        result2 = await session.execute(select(User).order_by(User.created_at.desc()).limit(3))
        users = result2.scalars().all()
        for u in users:
            print(f"   User: {u.email} | Provider: {u.provider} | accepted_tc: {u.accepted_tc}")

async def main():
    print("=" * 50)
    print("VELRA INTEGRATION TEST SUITE")
    print("=" * 50)
    try:
        await test_health()
        token = await test_signup()
        sso_token = await test_google_sso_sync()
        await test_protected_route(token)
        await test_db_users()
        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETE ✅")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
