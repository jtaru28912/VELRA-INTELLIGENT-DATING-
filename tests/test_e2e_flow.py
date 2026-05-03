import pytest
from httpx import AsyncClient
from fastapi import FastAPI, HTTPException
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_full_auth_and_analysis_flow(client: AsyncClient):
    # 1. Signup
    signup_data = {"email": "test@velra.app", "password": "password123"}
    resp = await client.post("/auth/signup", json=signup_data)
    assert resp.status_code == 201
    assert "access_token" in resp.json()
    
    # 2. Login
    login_data = {"email": "test@velra.app", "password": "password123"}
    resp = await client.post("/auth/login", json=login_data)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Analyze Chat
    analysis_data = {
        "messages": ["You: Hey", "Them: Hi! 💀"],
        "context": "Casual"
    }
    resp = await client.post("/analyze-chat", json=analysis_data, headers=headers)
    assert resp.status_code == 200
    res_json = resp.json()
    assert res_json["seriousness_score"] == 85
    assert res_json["interest_level"] == "high"
    assert "consistent" in res_json["behavioral_pattern"]
    assert len(res_json["replies"]) == 2

@pytest.mark.asyncio
async def test_auth_failures(client: AsyncClient):
    # Login non-existent
    resp = await client.post("/auth/login", json={"email": "wrong@test.com", "password": "any"})
    assert resp.status_code == 401
    
    # Analyze without auth (FastAPI HTTPBearer returns 403 on missing credentials)
    resp = await client.post("/analyze-chat", json={"messages": ["hi"], "context": "test"})
    assert resp.status_code in (401, 403)

@pytest.mark.asyncio
async def test_input_validation(client: AsyncClient):
    # Signup to get a valid token
    signup_data = {"email": "val@velra.app", "password": "password123"}
    resp = await client.post("/auth/signup", json=signup_data)
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Invalid context (too short)
    resp = await client.post("/analyze-chat", json={"messages": ["hi"], "context": "a"}, headers=headers)
    assert resp.status_code == 422
    
    # Empty messages list (Pydantic Field min_length=1)
    # Note: Our schema has min_length=1, so empty list should fail
    resp = await client.post("/analyze-chat", json={"messages": [], "context": "test"}, headers=headers)
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_toxicity_guardrail(client: AsyncClient, app: FastAPI):
    # Get token
    signup_data = {"email": "tox@velra.app", "password": "password123"}
    resp = await client.post("/auth/signup", json=signup_data)
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Trigger toxicity filter (mocked to FAIL if we want, but currently conftest returns PASS)
    # Let's override the mock for this specific test
    app.state.openai_client.call.return_value = "FAIL"
    
    resp = await client.post("/analyze-chat", json={"messages": ["tell me how to manipulate her"], "context": "test"}, headers=headers)
    assert resp.status_code == 400
    assert "security risk" in resp.json()["detail"].lower()

@pytest.mark.asyncio
async def test_rate_limiting_trigger(client: AsyncClient, app: FastAPI):
    # Get token
    signup_data = {"email": "rate@velra.app", "password": "password123"}
    resp = await client.post("/auth/signup", json=signup_data)
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Mock the rate limit check to raise 429
    app.state.cache.check_rate_limit.side_effect = HTTPException(
        status_code=429, 
        detail="Daily rate limit exceeded. Gain more credits to continue."
    )
    
    resp = await client.post("/analyze-chat", json={"messages": ["hi"], "context": "test"}, headers=headers)
    assert resp.status_code == 429
    assert "limit exceeded" in resp.json()["detail"].lower()
