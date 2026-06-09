from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest,
    AuthResponse, MessageResponse,
)
from app.services.auth.auth_service import AuthService
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.register(request.email, request.password, request.full_name, request.workspace_name)
    return MessageResponse(
        message="Registration successful. Please verify your email.",
        reset_token=result.get("verification_token"),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, req: Request, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(
        request.email, request.password,
        ip_address=req.client.host,
        user_agent=req.headers.get("user-agent"),
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh_token(request.refresh_token)


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.verify_email(request.token)
    return {"message": "Email verified successfully"}


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.forgot_password(request.email)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.reset_password(request.token, request.new_password)
    return {"message": "Password reset successfully"}


@router.post("/logout")
async def logout(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(current_user.id)
    return {"message": "Logged out successfully"}
