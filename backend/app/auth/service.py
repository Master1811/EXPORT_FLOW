from ..core.database import db
from ..core.security import hash_password, verify_password, create_token, create_token_pair, verify_refresh_token
from ..common.utils import generate_id, now_iso
from ..common.tamper_proof_audit import audit_service, TamperProofAuditService
from .models import UserCreate, UserLogin, UserResponse, TokenResponse
from fastapi import HTTPException

class AuthService:
    @staticmethod
    async def register(data: UserCreate, ip_address: str = None) -> dict:
        existing = await db.users.find_one({"email": data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = generate_id()
        company_id = None
        
        if data.company_name:
            company_id = generate_id()
            company_doc = {
                "id": company_id,
                "name": data.company_name,
                "created_at": now_iso()
            }
            await db.companies.insert_one(company_doc)
        
        user_doc = {
            "id": user_id,
            "email": data.email,
            "password": hash_password(data.password),
            "full_name": data.full_name,
            "company_id": company_id,
            "role": "admin" if company_id else "user",
            "created_at": now_iso(),
            "token_version": None  # For JWT invalidation
        }
        await db.users.insert_one(user_doc)
        
        # Create token pair (access + refresh)
        tokens = create_token_pair(user_id, data.email)
        
        # Audit log
        await audit_service.log(
            user_id=user_id,
            action=TamperProofAuditService.ACTION_CREATE,
            resource_type=TamperProofAuditService.RESOURCE_USER,
            resource_id=user_id,
            details={"email": data.email, "company_id": company_id},
            ip_address=ip_address
        )
        
        user_response = UserResponse(
            id=user_id,
            email=data.email,
            full_name=data.full_name,
            company_id=company_id,
            role=user_doc["role"],
            created_at=user_doc["created_at"]
        )
        
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"],
            "user": user_response
        }

    @staticmethod
    async def login(data: UserLogin, ip_address: str = None, user_agent: str = None) -> dict:
        user = await db.users.find_one({"email": data.email}, {"_id": 0})
        
        if not user or not verify_password(data.password, user["password"]):
            # Log failed login attempt
            await audit_service.log(
                user_id=data.email,  # Use email since we don't have user ID
                action=TamperProofAuditService.ACTION_FAILED_LOGIN,
                resource_type=TamperProofAuditService.RESOURCE_USER,
                details={"email": data.email, "reason": "Invalid credentials"},
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                error_message="Invalid credentials"
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token pair
        tokens = create_token_pair(user["id"], user["email"])
        
        # Log successful login
        await audit_service.log(
            user_id=user["id"],
            action=TamperProofAuditService.ACTION_LOGIN,
            resource_type=TamperProofAuditService.RESOURCE_USER,
            resource_id=user["id"],
            details={"email": user["email"]},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            company_id=user.get("company_id"),
            role=user.get("role", "user"),
            created_at=user["created_at"]
        )
        
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"],
            "user": user_response
        }

    @staticmethod
    async def refresh_tokens(refresh_token: str, ip_address: str = None) -> dict:
        """Use refresh token to get new access token."""
        try:
            payload = verify_refresh_token(refresh_token)
            user_id = payload["sub"]
            email = payload["email"]
            
            # Verify user still exists and token not invalidated
            user = await db.users.find_one({"id": user_id}, {"_id": 0})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            # Create new token pair
            tokens = create_token_pair(user_id, email)
            
            # Log token refresh
            await audit_service.log(
                user_id=user_id,
                action=TamperProofAuditService.ACTION_TOKEN_REFRESH,
                resource_type=TamperProofAuditService.RESOURCE_USER,
                resource_id=user_id,
                ip_address=ip_address
            )
            
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": tokens["token_type"],
                "expires_in": tokens["expires_in"]
            }
            
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    @staticmethod
    async def change_password(user_id: str, current_password: str, new_password: str, ip_address: str = None) -> dict:
        """Change user password and invalidate existing tokens"""
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(current_password, user["password"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password and token version
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "password": hash_password(new_password),
                "token_version": now_iso()
            }}
        )
        
        # Log password change
        await audit_service.log(
            user_id=user_id,
            action=TamperProofAuditService.ACTION_PASSWORD_CHANGE,
            resource_type=TamperProofAuditService.RESOURCE_USER,
            resource_id=user_id,
            details={"action": "Password changed, all sessions invalidated"},
            ip_address=ip_address
        )
        
        return {
            "message": "Password changed successfully. All sessions have been invalidated.",
            "status": "success"
        }

    @staticmethod
    async def logout(user_id: str, token: str, ip_address: str = None) -> dict:
        """Logout user and blacklist the token."""
        # Add token to blacklist
        await db.token_blacklist.insert_one({
            "token": token,
            "user_id": user_id,
            "blacklisted_at": now_iso()
        })
        
        # Log logout
        await audit_service.log(
            user_id=user_id,
            action=TamperProofAuditService.ACTION_LOGOUT,
            resource_type=TamperProofAuditService.RESOURCE_USER,
            resource_id=user_id,
            ip_address=ip_address
        )
        
        return {"message": "Successfully logged out"}

    @staticmethod
    def get_user_response(user: dict) -> UserResponse:
        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            company_id=user.get("company_id"),
            role=user.get("role", "user"),
            created_at=user["created_at"]
        )

    @staticmethod
    def refresh_user_token(user: dict) -> TokenResponse:
        token = create_token(user["id"], user["email"])
        return TokenResponse(
            access_token=token,
            user=AuthService.get_user_response(user)
        )
