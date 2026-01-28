from ..core.database import db
from ..core.security import hash_password, verify_password, create_token
from ..common.utils import generate_id, now_iso
from .models import UserCreate, UserLogin, UserResponse, TokenResponse
from fastapi import HTTPException

class AuthService:
    @staticmethod
    async def register(data: UserCreate) -> TokenResponse:
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
            "created_at": now_iso()
        }
        await db.users.insert_one(user_doc)
        
        token = create_token(user_id, data.email)
        user_response = UserResponse(
            id=user_id,
            email=data.email,
            full_name=data.full_name,
            company_id=company_id,
            role=user_doc["role"],
            created_at=user_doc["created_at"]
        )
        return TokenResponse(access_token=token, user=user_response)

    @staticmethod
    async def login(data: UserLogin) -> TokenResponse:
        user = await db.users.find_one({"email": data.email}, {"_id": 0})
        if not user or not verify_password(data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_token(user["id"], user["email"])
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            company_id=user.get("company_id"),
            role=user.get("role", "user"),
            created_at=user["created_at"]
        )
        return TokenResponse(access_token=token, user=user_response)

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
