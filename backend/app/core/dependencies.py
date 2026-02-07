from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timezone
from .database import db
from .config import settings

security = HTTPBearer()

async def check_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    blacklisted = await db.token_blacklist.find_one({"token": token})
    return blacklisted is not None

async def blacklist_token(token: str, reason: str = "logout"):
    """Add token to blacklist"""
    await db.token_blacklist.insert_one({
        "token": token,
        "reason": reason,
        "blacklisted_at": datetime.now(timezone.utc).isoformat()
    })

async def blacklist_user_tokens(user_id: str, reason: str = "password_change"):
    """Blacklist all tokens for a user (by marking user's token_version)"""
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"token_version": datetime.now(timezone.utc).isoformat()}}
    )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        
        # Check if token is blacklisted
        if await check_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        token_issued_at = payload.get("iat")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Check if token was issued before password change
        token_version = user.get("token_version")
        if token_version and token_issued_at:
            version_ts = datetime.fromisoformat(token_version.replace("Z", "+00:00")).timestamp()
            if token_issued_at < version_ts:
                raise HTTPException(status_code=401, detail="Token invalidated due to security update")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
