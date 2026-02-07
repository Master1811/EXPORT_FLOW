from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import secrets
from .config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str, token_type: str = "access") -> str:
    """
    Create JWT token with short TTL for security.
    
    Args:
        user_id: User's unique ID
        email: User's email
        token_type: 'access' (15 min) or 'refresh' (7 days)
    
    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)
    
    if token_type == "refresh":
        expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Generate unique token ID for tracking/revocation
    jti = secrets.token_hex(16)
    
    payload = {
        "sub": user_id,
        "email": email,
        "type": token_type,
        "jti": jti,  # JWT ID for revocation tracking
        "iat": now,
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_token_pair(user_id: str, email: str) -> dict:
    """
    Create both access and refresh tokens.
    
    Returns:
        Dict with access_token, refresh_token, and expiry info
    """
    access_token = create_token(user_id, email, "access")
    refresh_token = create_token(user_id, email, "refresh")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        "refresh_expires_in": settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # seconds
    }

def decode_token(token: str) -> dict:
    """Decode and verify JWT token."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def verify_refresh_token(token: str) -> dict:
    """Verify that a token is a valid refresh token."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token")
    return payload
