import pytest
from app.services.auth.auth_service import AuthService
from app.repositories.user import UserRepository
from app.repositories.workspace import WorkspaceRepository


@pytest.mark.asyncio
async def test_register_user(test_session):
    service = AuthService(test_session)
    result = await service.register(
        email="test@example.com",
        password="password123",
        full_name="Test User",
        workspace_name="Test Workspace",
    )
    assert result["email"] == "test@example.com"
    assert result["workspace_id"] is not None
    assert result["verification_token"] is not None


@pytest.mark.asyncio
async def test_register_duplicate_email(test_session):
    service = AuthService(test_session)
    await service.register(
        email="duplicate@example.com",
        password="password123",
        full_name="Test User",
    )
    with pytest.raises(Exception) as exc_info:
        await service.register(
            email="duplicate@example.com",
            password="password456",
            full_name="Test User 2",
        )
    assert "already registered" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_login_unverified(test_session):
    service = AuthService(test_session)
    await service.register(
        email="unverified@example.com",
        password="password123",
        full_name="Test User",
    )
    with pytest.raises(Exception) as exc_info:
        await service.login("unverified@example.com", "password123")
    assert "not verified" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_verify_email(test_session):
    service = AuthService(test_session)
    result = await service.register(
        email="verify@example.com",
        password="password123",
        full_name="Test User",
    )
    success = await service.verify_email(result["verification_token"])
    assert success is True
