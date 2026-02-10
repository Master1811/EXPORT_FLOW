"""
Enhanced Authentication Service with Security Features:
- Email verification on registration
- Failed login tracking with account lockout
- Session management (active sessions, logout all devices)
- Refresh token rotation (invalidate old tokens)
- CSRF token generation
"""
from ..core.database import db
from ..core.security import hash_password, verify_password, create_token, create_token_pair, verify_refresh_token
from ..common.utils import generate_id, now_iso
from ..common.tamper_proof_audit import audit_service, TamperProofAuditService
from .models import UserCreate, UserLogin, UserResponse, TokenResponse
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import secrets
import hashlib


# Security configuration
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
EMAIL_VERIFICATION_EXPIRY_HOURS = 24
SESSION_EXPIRY_DAYS = 7


class AuthService:
    
    # ==================== LOGIN ATTEMPT TRACKING ====================
    
    @staticmethod
    async def get_failed_attempts(email: str, ip_address: str) -> dict:
        """Get failed login attempts for an email/IP combination"""
        # Check by email (account-level lockout)
        email_attempts = await db.login_attempts.find_one({
            "identifier": email.lower(),
            "type": "email"
        }, {"_id": 0})
        
        # Check by IP (IP-level lockout)
        ip_attempts = await db.login_attempts.find_one({
            "identifier": ip_address,
            "type": "ip"
        }, {"_id": 0}) if ip_address else None
        
        return {
            "email_attempts": email_attempts,
            "ip_attempts": ip_attempts
        }
    
    @staticmethod
    async def is_locked_out(email: str, ip_address: str) -> tuple:
        """Check if account or IP is locked out. Returns (is_locked, reason, unlock_time)"""
        attempts_data = await AuthService.get_failed_attempts(email, ip_address)
        
        now = datetime.now(timezone.utc)
        
        # Check email lockout
        email_attempts = attempts_data.get("email_attempts")
        if email_attempts:
            if email_attempts.get("failed_count", 0) >= MAX_FAILED_LOGIN_ATTEMPTS:
                lockout_until = email_attempts.get("lockout_until")
                if lockout_until:
                    lockout_time = datetime.fromisoformat(lockout_until.replace('Z', '+00:00'))
                    if now < lockout_time:
                        remaining_minutes = int((lockout_time - now).total_seconds() / 60)
                        return (True, f"Account locked due to too many failed attempts. Try again in {remaining_minutes} minutes.", lockout_time.isoformat())
        
        # Check IP lockout
        ip_attempts = attempts_data.get("ip_attempts")
        if ip_attempts:
            if ip_attempts.get("failed_count", 0) >= MAX_FAILED_LOGIN_ATTEMPTS * 2:  # Higher threshold for IP
                lockout_until = ip_attempts.get("lockout_until")
                if lockout_until:
                    lockout_time = datetime.fromisoformat(lockout_until.replace('Z', '+00:00'))
                    if now < lockout_time:
                        remaining_minutes = int((lockout_time - now).total_seconds() / 60)
                        return (True, f"IP temporarily blocked. Try again in {remaining_minutes} minutes.", lockout_time.isoformat())
        
        return (False, None, None)
    
    @staticmethod
    async def record_failed_attempt(email: str, ip_address: str):
        """Record a failed login attempt"""
        now = datetime.now(timezone.utc)
        lockout_time = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        
        # Update email-based tracking
        email_result = await db.login_attempts.find_one_and_update(
            {"identifier": email.lower(), "type": "email"},
            {
                "$inc": {"failed_count": 1},
                "$set": {"last_attempt": now_iso()},
                "$setOnInsert": {"created_at": now_iso()}
            },
            upsert=True,
            return_document=True
        )
        
        # Set lockout if threshold reached
        if email_result and email_result.get("failed_count", 0) >= MAX_FAILED_LOGIN_ATTEMPTS:
            await db.login_attempts.update_one(
                {"identifier": email.lower(), "type": "email"},
                {"$set": {"lockout_until": lockout_time.isoformat()}}
            )
        
        # Update IP-based tracking
        if ip_address:
            ip_result = await db.login_attempts.find_one_and_update(
                {"identifier": ip_address, "type": "ip"},
                {
                    "$inc": {"failed_count": 1},
                    "$set": {"last_attempt": now_iso()},
                    "$setOnInsert": {"created_at": now_iso()}
                },
                upsert=True,
                return_document=True
            )
            
            if ip_result and ip_result.get("failed_count", 0) >= MAX_FAILED_LOGIN_ATTEMPTS * 2:
                await db.login_attempts.update_one(
                    {"identifier": ip_address, "type": "ip"},
                    {"$set": {"lockout_until": lockout_time.isoformat()}}
                )
    
    @staticmethod
    async def reset_failed_attempts(email: str, ip_address: str):
        """Reset failed login attempts after successful login"""
        await db.login_attempts.delete_one({"identifier": email.lower(), "type": "email"})
        if ip_address:
            # Only reset IP if it was this email's failures
            await db.login_attempts.update_one(
                {"identifier": ip_address, "type": "ip"},
                {"$inc": {"failed_count": -1}}
            )
    
    # ==================== SESSION MANAGEMENT ====================
    
    @staticmethod
    async def create_session(user_id: str, refresh_token: str, ip_address: str = None, user_agent: str = None) -> str:
        """Create a new session record"""
        session_id = generate_id()
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        session_doc = {
            "id": session_id,
            "user_id": user_id,
            "token_hash": token_hash,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": now_iso(),
            "last_active": now_iso(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat(),
            "is_active": True
        }
        
        await db.user_sessions.insert_one(session_doc)
        return session_id
    
    @staticmethod
    async def get_active_sessions(user_id: str) -> list:
        """Get all active sessions for a user"""
        sessions = await db.user_sessions.find({
            "user_id": user_id,
            "is_active": True
        }, {"_id": 0, "token_hash": 0}).to_list(100)
        
        return sessions
    
    @staticmethod
    async def revoke_session(user_id: str, session_id: str) -> bool:
        """Revoke a specific session"""
        result = await db.user_sessions.update_one(
            {"id": session_id, "user_id": user_id},
            {"$set": {"is_active": False, "revoked_at": now_iso()}}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def revoke_all_sessions(user_id: str, except_session_id: str = None) -> int:
        """Revoke all sessions for a user (logout from all devices)"""
        query = {"user_id": user_id, "is_active": True}
        if except_session_id:
            query["id"] = {"$ne": except_session_id}
        
        result = await db.user_sessions.update_many(
            query,
            {"$set": {"is_active": False, "revoked_at": now_iso()}}
        )
        return result.modified_count
    
    @staticmethod
    async def validate_session(user_id: str, refresh_token: str) -> bool:
        """
        Validate that a session is still active.
        Returns True if:
        - Session exists and is active, OR
        - Session doesn't exist (backward compatibility for tokens created before session tracking)
        """
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Check if session exists
        session = await db.user_sessions.find_one({
            "user_id": user_id,
            "token_hash": token_hash
        })
        
        # If no session found, allow for backward compatibility
        # (tokens issued before session tracking was implemented)
        if session is None:
            return True
        
        # If session found, check if it's active
        return session.get("is_active", False)
    
    @staticmethod
    async def invalidate_refresh_token(refresh_token: str):
        """Invalidate a specific refresh token (token rotation)"""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        await db.user_sessions.update_one(
            {"token_hash": token_hash},
            {"$set": {"is_active": False, "rotated_at": now_iso()}}
        )
        # Also add to blacklist for extra safety
        await db.blacklisted_tokens.insert_one({
            "token_hash": token_hash,
            "type": "refresh",
            "blacklisted_at": now_iso()
        })
    
    # ==================== EMAIL VERIFICATION ====================
    
    @staticmethod
    async def generate_verification_token(user_id: str, email: str) -> str:
        """Generate email verification token"""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        await db.email_verifications.insert_one({
            "user_id": user_id,
            "email": email.lower(),
            "token_hash": token_hash,
            "created_at": now_iso(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=EMAIL_VERIFICATION_EXPIRY_HOURS)).isoformat(),
            "used": False
        })
        
        return token
    
    @staticmethod
    async def verify_email(token: str) -> dict:
        """Verify email with token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        verification = await db.email_verifications.find_one({
            "token_hash": token_hash,
            "used": False
        })
        
        if not verification:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        # Check expiry
        expires_at = datetime.fromisoformat(verification["expires_at"].replace('Z', '+00:00'))
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="Verification token has expired")
        
        # Mark email as verified
        await db.users.update_one(
            {"id": verification["user_id"]},
            {"$set": {"email_verified": True, "email_verified_at": now_iso()}}
        )
        
        # Mark token as used
        await db.email_verifications.update_one(
            {"token_hash": token_hash},
            {"$set": {"used": True, "used_at": now_iso()}}
        )
        
        return {"message": "Email verified successfully"}
    
    # ==================== CSRF TOKEN ====================
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a CSRF token"""
        return secrets.token_urlsafe(32)
    
    # ==================== CORE AUTH METHODS ====================
    
    @staticmethod
    async def register(data: UserCreate, ip_address: str = None) -> dict:
        existing = await db.users.find_one({"email": data.email.lower()})
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
            "email": data.email.lower(),  # Normalize email
            "password": hash_password(data.password),
            "full_name": data.full_name,
            "company_id": company_id,
            "role": "admin" if company_id else "user",
            "created_at": now_iso(),
            "email_verified": False,  # NEW: Email not verified initially
            "token_version": None
        }
        await db.users.insert_one(user_doc)
        
        # Generate email verification token
        verification_token = await AuthService.generate_verification_token(user_id, data.email)
        
        # Create token pair (access + refresh)
        tokens = create_token_pair(user_id, data.email)
        
        # Create session
        session_id = await AuthService.create_session(
            user_id, tokens["refresh_token"], ip_address
        )
        
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
            "user": user_response,
            "session_id": session_id,
            "email_verification_required": True,
            "verification_token": verification_token  # In production, send via email
        }

    @staticmethod
    async def login(data: UserLogin, ip_address: str = None, user_agent: str = None) -> dict:
        email = data.email.lower()
        
        # Check for lockout FIRST
        is_locked, lock_reason, unlock_time = await AuthService.is_locked_out(email, ip_address)
        if is_locked:
            raise HTTPException(
                status_code=429, 
                detail=lock_reason,
                headers={"Retry-After": unlock_time}
            )
        
        user = await db.users.find_one({"email": email}, {"_id": 0})
        
        if not user or not verify_password(data.password, user["password"]):
            # Record failed attempt
            await AuthService.record_failed_attempt(email, ip_address)
            
            # Get current count for user feedback
            attempts_data = await AuthService.get_failed_attempts(email, ip_address)
            current_attempts = attempts_data.get("email_attempts", {}).get("failed_count", 1)
            remaining_attempts = MAX_FAILED_LOGIN_ATTEMPTS - current_attempts
            
            # Log failed login attempt
            await audit_service.log(
                user_id=email,
                action=TamperProofAuditService.ACTION_FAILED_LOGIN,
                resource_type=TamperProofAuditService.RESOURCE_USER,
                details={
                    "email": email, 
                    "reason": "Invalid credentials",
                    "attempt_number": current_attempts
                },
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                error_message="Invalid credentials"
            )
            
            if remaining_attempts > 0:
                raise HTTPException(
                    status_code=401, 
                    detail=f"Invalid credentials. {remaining_attempts} attempts remaining before lockout."
                )
            else:
                raise HTTPException(
                    status_code=429, 
                    detail=f"Account locked for {LOCKOUT_DURATION_MINUTES} minutes due to too many failed attempts."
                )
        
        # Reset failed attempts on successful login
        await AuthService.reset_failed_attempts(email, ip_address)
        
        # Create token pair
        tokens = create_token_pair(user["id"], user["email"])
        
        # Create session
        session_id = await AuthService.create_session(
            user["id"], tokens["refresh_token"], ip_address, user_agent
        )
        
        # Log successful login
        await audit_service.log(
            user_id=user["id"],
            action=TamperProofAuditService.ACTION_LOGIN,
            resource_type=TamperProofAuditService.RESOURCE_USER,
            resource_id=user["id"],
            details={"email": user["email"], "session_id": session_id},
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
        
        # Generate CSRF token
        csrf_token = AuthService.generate_csrf_token()
        
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"],
            "user": user_response,
            "session_id": session_id,
            "csrf_token": csrf_token,
            "email_verified": user.get("email_verified", False)
        }

    @staticmethod
    async def refresh_tokens(refresh_token: str, ip_address: str = None) -> dict:
        """Use refresh token to get new access token with token rotation."""
        try:
            payload = verify_refresh_token(refresh_token)
            user_id = payload["sub"]
            email = payload["email"]
            
            # Verify user still exists
            user = await db.users.find_one({"id": user_id}, {"_id": 0})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            # Validate session is still active
            session_valid = await AuthService.validate_session(user_id, refresh_token)
            if not session_valid:
                raise HTTPException(status_code=401, detail="Session has been revoked")
            
            # IMPORTANT: Invalidate old refresh token (token rotation)
            await AuthService.invalidate_refresh_token(refresh_token)
            
            # Create new token pair
            tokens = create_token_pair(user_id, email)
            
            # Create new session with new refresh token
            session_id = await AuthService.create_session(
                user_id, tokens["refresh_token"], ip_address
            )
            
            # Log token refresh
            await audit_service.log(
                user_id=user_id,
                action=TamperProofAuditService.ACTION_TOKEN_REFRESH,
                resource_type=TamperProofAuditService.RESOURCE_USER,
                resource_id=user_id,
                details={"new_session_id": session_id},
                ip_address=ip_address
            )
            
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": tokens["token_type"],
                "expires_in": tokens["expires_in"],
                "session_id": session_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    @staticmethod
    async def change_password(user_id: str, current_password: str, new_password: str, ip_address: str = None) -> dict:
        """Change user password and invalidate ALL existing sessions"""
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
                "token_version": now_iso(),
                "password_changed_at": now_iso()
            }}
        )
        
        # Revoke ALL sessions (logout from all devices)
        revoked_count = await AuthService.revoke_all_sessions(user_id)
        
        # Log password change
        await audit_service.log(
            user_id=user_id,
            action=TamperProofAuditService.ACTION_PASSWORD_CHANGE,
            resource_type=TamperProofAuditService.RESOURCE_USER,
            resource_id=user_id,
            details={"sessions_revoked": revoked_count},
            ip_address=ip_address
        )
        
        return {
            "message": "Password changed successfully. All sessions have been invalidated.",
            "sessions_revoked": revoked_count,
            "status": "success"
        }

    @staticmethod
    async def logout(user_id: str, token: str, session_id: str = None, ip_address: str = None) -> dict:
        """Logout user and revoke the session."""
        # Revoke current session
        if session_id:
            await AuthService.revoke_session(user_id, session_id)
        
        # Also blacklist the access token
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
    async def logout_all_devices(user_id: str, current_session_id: str = None, ip_address: str = None) -> dict:
        """Logout from all devices except current session"""
        revoked_count = await AuthService.revoke_all_sessions(user_id, except_session_id=current_session_id)
        
        # Log mass logout
        await audit_service.log(
            user_id=user_id,
            action="logout_all_devices",
            resource_type=TamperProofAuditService.RESOURCE_USER,
            resource_id=user_id,
            details={"sessions_revoked": revoked_count, "kept_session": current_session_id},
            ip_address=ip_address
        )
        
        return {
            "message": f"Logged out from {revoked_count} other device(s)",
            "sessions_revoked": revoked_count
        }

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
