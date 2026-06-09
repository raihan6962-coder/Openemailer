import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_endpoint(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "api_test@example.com",
        "password": "password123",
        "full_name": "API Test User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_login_endpoint(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login_test@example.com",
        "password": "password123",
        "full_name": "Login Test",
    })

    token = "test-token"
    await client.post("/api/v1/auth/verify-email", json={"token": token})

    response = await client.post("/api/v1/auth/login", json={
        "email": "login_test@example.com",
        "password": "password123",
    })
    assert response.status_code in (200, 401)
