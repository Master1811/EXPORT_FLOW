from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..core.dependencies import get_current_user, blacklist_token, blacklist_user_tokens
from .models import UserCreate, UserLogin, UserResponse, TokenResponse, ChangePasswordRequest
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate):
    return await AuthService.register(data)

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    return await AuthService.login(data)

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return AuthService.get_user_response(user)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(user: dict = Depends(get_current_user)):
    return AuthService.refresh_user_token(user)

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user)
):
    """Logout user by blacklisting current token"""
    await blacklist_token(credentials.credentials, reason="logout")
    return {"message": "Successfully logged out", "status": "success"}

@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user)
):
    """Change password and invalidate all existing tokens"""
    result = await AuthService.change_password(user["id"], data.current_password, data.new_password)
    # Blacklist current token
    await blacklist_token(credentials.credentials, reason="password_change")
    # Invalidate all other tokens
    await blacklist_user_tokens(user["id"], reason="password_change")
    return result
