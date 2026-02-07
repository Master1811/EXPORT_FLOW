from fastapi import APIRouter, Depends, Request, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..core.dependencies import get_current_user, blacklist_token, blacklist_user_tokens
from .models import UserCreate, UserLogin, UserResponse, TokenResponse, ChangePasswordRequest
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None

def get_user_agent(request: Request) -> str:
    """Extract user agent from request."""
    return request.headers.get("User-Agent")

@router.post("/register")
async def register(data: UserCreate, request: Request):
    """Register a new user. Returns access and refresh tokens."""
    return await AuthService.register(data, ip_address=get_client_ip(request))

@router.post("/login")
async def login(data: UserLogin, request: Request):
    """Login user. Returns access token (15 min) and refresh token (7 days)."""
    return await AuthService.login(
        data, 
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

@router.post("/refresh")
async def refresh_token(
    request: Request,
    refresh_token: str = Body(..., embed=True)
):
    """
    Use refresh token to get new access token.
    
    Call this when access token expires. Provides new access and refresh tokens.
    """
    return await AuthService.refresh_tokens(
        refresh_token,
        ip_address=get_client_ip(request)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return AuthService.get_user_response(user)

@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user)
):
    """Logout user by blacklisting current token. All actions logged to audit trail."""
    await AuthService.logout(
        user["id"], 
        credentials.credentials,
        ip_address=get_client_ip(request)
    )
    return {"message": "Successfully logged out", "status": "success"}

@router.post("/change-password")
async def change_password(
    request: Request,
    data: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user)
):
    """
    Change password and invalidate all existing tokens.
    User must re-login after password change.
    """
    result = await AuthService.change_password(
        user["id"], 
        data.current_password, 
        data.new_password,
        ip_address=get_client_ip(request)
    )
    # Blacklist current token
    await blacklist_token(credentials.credentials, reason="password_change")
    # Invalidate all other tokens
    await blacklist_user_tokens(user["id"], reason="password_change")
    return result
