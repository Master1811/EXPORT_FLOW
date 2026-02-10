from fastapi import APIRouter, Depends, Request, Body, Response, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..core.dependencies import get_current_user, blacklist_token, blacklist_user_tokens
from ..core.rate_limiting import auth_login_limit, auth_register_limit, limiter
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
@auth_register_limit
async def register(request: Request, response: Response, data: UserCreate):
    """
    Register a new user. Returns access and refresh tokens.
    Email verification token is generated (in production, send via email).
    Rate limited: 3/minute per IP.
    """
    return await AuthService.register(data, ip_address=get_client_ip(request))

@router.post("/login")
@auth_login_limit
async def login(request: Request, response: Response, data: UserLogin):
    """
    Login user. Returns access token (15 min) and refresh token (7 days).
    
    Security features:
    - Account locks after 5 failed attempts for 15 minutes
    - IP blocks after 10 failed attempts
    - Returns remaining attempts on failure
    
    Rate limited: 5/minute per IP.
    """
    return await AuthService.login(
        data, 
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

@router.post("/refresh")
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: str = Body(..., embed=True)
):
    """
    Use refresh token to get new access token.
    
    SECURITY: Old refresh token is INVALIDATED after use (token rotation).
    Call this when access token expires. Provides new access and refresh tokens.
    Rate limited: 30/minute.
    """
    return await AuthService.refresh_tokens(
        refresh_token,
        ip_address=get_client_ip(request)
    )

@router.post("/verify-email")
async def verify_email(token: str = Query(...)):
    """
    Verify email address using the token sent during registration.
    """
    return await AuthService.verify_email(token)

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return AuthService.get_user_response(user)

@router.get("/sessions")
async def get_sessions(user: dict = Depends(get_current_user)):
    """
    Get all active sessions for current user.
    Shows devices/IPs where user is logged in.
    """
    sessions = await AuthService.get_active_sessions(user["id"])
    return {"sessions": sessions, "count": len(sessions)}

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    request: Request,
    user: dict = Depends(get_current_user)
):
    """
    Revoke a specific session (logout from a specific device).
    """
    success = await AuthService.revoke_session(user["id"], session_id)
    if success:
        return {"message": "Session revoked successfully"}
    else:
        return {"message": "Session not found or already revoked"}

@router.post("/logout")
async def logout(
    request: Request,
    session_id: str = Body(None, embed=True),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user)
):
    """Logout user by revoking current session. All actions logged to audit trail."""
    await AuthService.logout(
        user["id"], 
        credentials.credentials,
        session_id=session_id,
        ip_address=get_client_ip(request)
    )
    return {"message": "Successfully logged out", "status": "success"}

@router.post("/logout-all-devices")
async def logout_all_devices(
    request: Request,
    current_session_id: str = Body(None, embed=True),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user)
):
    """
    Logout from all devices except the current one.
    Useful when user suspects their account is compromised.
    """
    return await AuthService.logout_all_devices(
        user["id"],
        current_session_id=current_session_id,
        ip_address=get_client_ip(request)
    )

@router.post("/change-password")
@limiter.limit("3/hour")
async def change_password(
    request: Request,
    response: Response,
    data: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user)
):
    """
    Change password and invalidate ALL existing sessions.
    User must re-login after password change.
    Rate limited: 3/hour.
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
