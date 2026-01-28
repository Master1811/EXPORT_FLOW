from fastapi import APIRouter, Depends
from ..core.dependencies import get_current_user
from .models import UserCreate, UserLogin, UserResponse, TokenResponse
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

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
