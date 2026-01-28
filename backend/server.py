from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Query, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'default-secret-key')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRE_MINUTES = int(os.environ.get('JWT_EXPIRE_MINUTES', 1440))

# Create the main app
app = FastAPI(title="Exporter Finance & Compliance Platform")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ PYDANTIC MODELS ============

# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    company_id: Optional[str] = None
    role: str = "user"
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Company Models
class CompanyCreate(BaseModel):
    name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    iec_code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    bank_account: Optional[str] = None
    bank_ifsc: Optional[str] = None

class CompanyResponse(BaseModel):
    id: str
    name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    iec_code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    created_at: str

# Shipment Models
class ShipmentCreate(BaseModel):
    shipment_number: str
    buyer_name: str
    buyer_country: str
    destination_port: str
    origin_port: str
    incoterm: str = "FOB"
    currency: str = "USD"
    total_value: float
    status: str = "draft"
    expected_ship_date: Optional[str] = None
    product_description: Optional[str] = None
    hs_codes: Optional[List[str]] = []

class ShipmentResponse(BaseModel):
    id: str
    shipment_number: str
    buyer_name: str
    buyer_country: str
    destination_port: str
    origin_port: str
    incoterm: str
    currency: str
    total_value: float
    status: str
    expected_ship_date: Optional[str]
    product_description: Optional[str]
    hs_codes: List[str]
    company_id: str
    created_at: str
    updated_at: str

class ShipmentUpdate(BaseModel):
    buyer_name: Optional[str] = None
    buyer_country: Optional[str] = None
    destination_port: Optional[str] = None
    origin_port: Optional[str] = None
    incoterm: Optional[str] = None
    currency: Optional[str] = None
    total_value: Optional[float] = None
    status: Optional[str] = None
    expected_ship_date: Optional[str] = None
    product_description: Optional[str] = None
    hs_codes: Optional[List[str]] = None

# Trade Document Models
class InvoiceCreate(BaseModel):
    invoice_number: str
    invoice_date: str
    items: List[Dict[str, Any]]
    subtotal: float
    tax_amount: float = 0
    total_amount: float
    payment_terms: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    document_type: str
    shipment_id: str
    document_number: str
    created_at: str
    data: Dict[str, Any]

# Payment Models
class PaymentCreate(BaseModel):
    shipment_id: str
    amount: float
    currency: str
    payment_date: str
    payment_mode: str
    bank_reference: Optional[str] = None
    exchange_rate: Optional[float] = None
    inr_amount: Optional[float] = None

class PaymentResponse(BaseModel):
    id: str
    shipment_id: str
    amount: float
    currency: str
    payment_date: str
    payment_mode: str
    bank_reference: Optional[str]
    exchange_rate: Optional[float]
    inr_amount: Optional[float]
    status: str
    created_at: str

# Forex Models
class ForexRateCreate(BaseModel):
    currency: str
    rate: float
    source: str = "manual"

class ForexRateResponse(BaseModel):
    id: str
    currency: str
    rate: float
    source: str
    timestamp: str

# GST Models
class GSTInputCreditCreate(BaseModel):
    invoice_number: str
    supplier_gstin: str
    invoice_date: str
    taxable_value: float
    igst: float = 0
    cgst: float = 0
    sgst: float = 0
    total_tax: float

class GSTSummaryResponse(BaseModel):
    month: str
    total_export_value: float
    total_igst_paid: float
    refund_eligible: float
    refund_claimed: float
    refund_pending: float

# Incentive Models
class IncentiveCalculateRequest(BaseModel):
    shipment_id: str
    hs_codes: List[str]
    fob_value: float
    currency: str = "INR"

class IncentiveResponse(BaseModel):
    id: str
    shipment_id: str
    scheme: str
    hs_code: str
    fob_value: float
    rate_percent: float
    incentive_amount: float
    status: str
    created_at: str

# AI Models
class AIQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None

class AIQueryResponse(BaseModel):
    query: str
    response: str
    timestamp: str

# Credit Models
class BuyerScoreResponse(BaseModel):
    buyer_id: str
    buyer_name: str
    credit_score: int
    risk_level: str
    payment_history: Dict[str, Any]
    recommendation: str

# Connector Models
class ConnectorInitRequest(BaseModel):
    connector_type: str
    credentials: Dict[str, str]

class ConnectorStatusResponse(BaseModel):
    connector_type: str
    status: str
    last_sync: Optional[str]
    message: str

# Job Models
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]]
    created_at: str

# Notification Models
class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    read: bool
    created_at: str

# ============ HELPER FUNCTIONS ============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_id() -> str:
    return str(uuid.uuid4())

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# ============ AUTH ENDPOINTS ============

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(data: UserCreate):
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

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
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

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        company_id=user.get("company_id"),
        role=user.get("role", "user"),
        created_at=user["created_at"]
    )

@api_router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(user: dict = Depends(get_current_user)):
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

# ============ COMPANY ENDPOINTS ============

@api_router.post("/company", response_model=CompanyResponse)
async def create_company(data: CompanyCreate, user: dict = Depends(get_current_user)):
    company_id = generate_id()
    company_doc = {
        "id": company_id,
        "name": data.name,
        "gstin": data.gstin,
        "pan": data.pan,
        "iec_code": data.iec_code,
        "address": data.address,
        "city": data.city,
        "state": data.state,
        "country": data.country,
        "bank_account": data.bank_account,
        "bank_ifsc": data.bank_ifsc,
        "owner_id": user["id"],
        "created_at": now_iso()
    }
    await db.companies.insert_one(company_doc)
    await db.users.update_one({"id": user["id"]}, {"$set": {"company_id": company_id}})
    
    return CompanyResponse(
        id=company_id, name=data.name, gstin=data.gstin, pan=data.pan,
        iec_code=data.iec_code, address=data.address, city=data.city,
        state=data.state, country=data.country, created_at=company_doc["created_at"]
    )

@api_router.get("/company/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, user: dict = Depends(get_current_user)):
    company = await db.companies.find_one({"id": company_id}, {"_id": 0})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse(**{k: v for k, v in company.items() if k in CompanyResponse.model_fields})

@api_router.put("/company/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: str, data: CompanyCreate, user: dict = Depends(get_current_user)):
    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_at"] = now_iso()
    await db.companies.update_one({"id": company_id}, {"$set": update_data})
    company = await db.companies.find_one({"id": company_id}, {"_id": 0})
    return CompanyResponse(**{k: v for k, v in company.items() if k in CompanyResponse.model_fields})

# ============ SHIPMENT ENDPOINTS ============

@api_router.post("/shipments", response_model=ShipmentResponse)
async def create_shipment(data: ShipmentCreate, user: dict = Depends(get_current_user)):
    shipment_id = generate_id()
    shipment_doc = {
        "id": shipment_id,
        **data.model_dump(),
        "company_id": user.get("company_id", user["id"]),
        "created_by": user["id"],
        "created_at": now_iso(),
        "updated_at": now_iso()
    }
    await db.shipments.insert_one(shipment_doc)
    return ShipmentResponse(**{k: v for k, v in shipment_doc.items() if k in ShipmentResponse.model_fields})

@api_router.get("/shipments", response_model=List[ShipmentResponse])
async def get_shipments(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    query = {"company_id": user.get("company_id", user["id"])}
    if status:
        query["status"] = status
    
    shipments = await db.shipments.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return [ShipmentResponse(**{k: v for k, v in s.items() if k in ShipmentResponse.model_fields}) for s in shipments]

@api_router.get("/shipments/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(shipment_id: str, user: dict = Depends(get_current_user)):
    shipment = await db.shipments.find_one({"id": shipment_id}, {"_id": 0})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return ShipmentResponse(**{k: v for k, v in shipment.items() if k in ShipmentResponse.model_fields})

@api_router.put("/shipments/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(shipment_id: str, data: ShipmentUpdate, user: dict = Depends(get_current_user)):
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    update_data["updated_at"] = now_iso()
    await db.shipments.update_one({"id": shipment_id}, {"$set": update_data})
    shipment = await db.shipments.find_one({"id": shipment_id}, {"_id": 0})
    return ShipmentResponse(**{k: v for k, v in shipment.items() if k in ShipmentResponse.model_fields})

@api_router.delete("/shipments/{shipment_id}")
async def delete_shipment(shipment_id: str, user: dict = Depends(get_current_user)):
    result = await db.shipments.delete_one({"id": shipment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return {"message": "Shipment deleted"}

# ============ TRADE DOCUMENTS ENDPOINTS ============

@api_router.post("/shipments/{shipment_id}/invoice", response_model=DocumentResponse)
async def create_invoice(shipment_id: str, data: InvoiceCreate, user: dict = Depends(get_current_user)):
    doc_id = generate_id()
    doc = {
        "id": doc_id,
        "document_type": "invoice",
        "shipment_id": shipment_id,
        "document_number": data.invoice_number,
        "data": data.model_dump(),
        "company_id": user.get("company_id", user["id"]),
        "created_by": user["id"],
        "created_at": now_iso()
    }
    await db.documents.insert_one(doc)
    return DocumentResponse(**{k: v for k, v in doc.items() if k in DocumentResponse.model_fields})

@api_router.post("/shipments/{shipment_id}/packing-list", response_model=DocumentResponse)
async def create_packing_list(shipment_id: str, data: Dict[str, Any], user: dict = Depends(get_current_user)):
    doc_id = generate_id()
    doc = {
        "id": doc_id,
        "document_type": "packing_list",
        "shipment_id": shipment_id,
        "document_number": data.get("packing_list_number", f"PL-{shipment_id[:8]}"),
        "data": data,
        "company_id": user.get("company_id", user["id"]),
        "created_by": user["id"],
        "created_at": now_iso()
    }
    await db.documents.insert_one(doc)
    return DocumentResponse(**{k: v for k, v in doc.items() if k in DocumentResponse.model_fields})

@api_router.post("/shipments/{shipment_id}/shipping-bill", response_model=DocumentResponse)
async def create_shipping_bill(shipment_id: str, data: Dict[str, Any], user: dict = Depends(get_current_user)):
    doc_id = generate_id()
    doc = {
        "id": doc_id,
        "document_type": "shipping_bill",
        "shipment_id": shipment_id,
        "document_number": data.get("sb_number", f"SB-{shipment_id[:8]}"),
        "data": data,
        "company_id": user.get("company_id", user["id"]),
        "created_by": user["id"],
        "created_at": now_iso()
    }
    await db.documents.insert_one(doc)
    return DocumentResponse(**{k: v for k, v in doc.items() if k in DocumentResponse.model_fields})

@api_router.get("/shipments/{shipment_id}/documents", response_model=List[DocumentResponse])
async def get_shipment_documents(shipment_id: str, user: dict = Depends(get_current_user)):
    docs = await db.documents.find({"shipment_id": shipment_id}, {"_id": 0}).to_list(100)
    return [DocumentResponse(**{k: v for k, v in d.items() if k in DocumentResponse.model_fields}) for d in docs]

# ============ PAYMENT ENDPOINTS ============

@api_router.post("/payments", response_model=PaymentResponse)
async def create_payment(data: PaymentCreate, user: dict = Depends(get_current_user)):
    payment_id = generate_id()
    payment_doc = {
        "id": payment_id,
        **data.model_dump(),
        "status": "received",
        "company_id": user.get("company_id", user["id"]),
        "created_by": user["id"],
        "created_at": now_iso()
    }
    await db.payments.insert_one(payment_doc)
    return PaymentResponse(**{k: v for k, v in payment_doc.items() if k in PaymentResponse.model_fields})

@api_router.get("/payments/shipment/{shipment_id}", response_model=List[PaymentResponse])
async def get_shipment_payments(shipment_id: str, user: dict = Depends(get_current_user)):
    payments = await db.payments.find({"shipment_id": shipment_id}, {"_id": 0}).to_list(100)
    return [PaymentResponse(**{k: v for k, v in p.items() if k in PaymentResponse.model_fields}) for p in payments]

@api_router.get("/receivables")
async def get_receivables(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    shipments = await db.shipments.find({"company_id": company_id, "status": {"$ne": "paid"}}, {"_id": 0}).to_list(500)
    
    receivables = []
    for s in shipments:
        payments = await db.payments.find({"shipment_id": s["id"]}, {"_id": 0}).to_list(100)
        total_paid = sum(p.get("amount", 0) for p in payments)
        outstanding = s["total_value"] - total_paid
        if outstanding > 0:
            receivables.append({
                "shipment_id": s["id"],
                "shipment_number": s["shipment_number"],
                "buyer_name": s["buyer_name"],
                "total_value": s["total_value"],
                "currency": s["currency"],
                "paid": total_paid,
                "outstanding": outstanding,
                "status": s["status"]
            })
    return receivables

@api_router.get("/receivables/aging")
async def get_receivables_aging(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    
    aging = {"current": 0, "30_days": 0, "60_days": 0, "90_days": 0, "over_90": 0}
    now = datetime.now(timezone.utc)
    
    for s in shipments:
        payments = await db.payments.find({"shipment_id": s["id"]}, {"_id": 0}).to_list(100)
        total_paid = sum(p.get("amount", 0) for p in payments)
        outstanding = s["total_value"] - total_paid
        
        if outstanding > 0:
            created = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))
            days = (now - created).days
            
            if days <= 30:
                aging["current"] += outstanding
            elif days <= 60:
                aging["30_days"] += outstanding
            elif days <= 90:
                aging["60_days"] += outstanding
            elif days <= 120:
                aging["90_days"] += outstanding
            else:
                aging["over_90"] += outstanding
    
    return aging

# ============ FOREX ENDPOINTS ============

@api_router.post("/forex/rate", response_model=ForexRateResponse)
async def create_forex_rate(data: ForexRateCreate, user: dict = Depends(get_current_user)):
    rate_id = generate_id()
    rate_doc = {
        "id": rate_id,
        "currency": data.currency,
        "rate": data.rate,
        "source": data.source,
        "company_id": user.get("company_id", user["id"]),
        "timestamp": now_iso()
    }
    await db.forex_rates.insert_one(rate_doc)
    return ForexRateResponse(**{k: v for k, v in rate_doc.items() if k in ForexRateResponse.model_fields})

@api_router.get("/forex/latest")
async def get_latest_forex():
    currencies = ["USD", "EUR", "GBP", "AED", "JPY", "CNY", "SGD"]
    rates = {}
    for curr in currencies:
        rate = await db.forex_rates.find_one({"currency": curr}, {"_id": 0}, sort=[("timestamp", -1)])
        if rate:
            rates[curr] = rate["rate"]
        else:
            # Default rates for demo
            default_rates = {"USD": 83.50, "EUR": 91.20, "GBP": 106.50, "AED": 22.75, "JPY": 0.56, "CNY": 11.50, "SGD": 62.30}
            rates[curr] = default_rates.get(curr, 1.0)
    return {"rates": rates, "base": "INR", "timestamp": now_iso()}

@api_router.get("/forex/history/{currency}")
async def get_forex_history(currency: str, days: int = 30, user: dict = Depends(get_current_user)):
    rates = await db.forex_rates.find({"currency": currency}, {"_id": 0}).sort("timestamp", -1).limit(days).to_list(days)
    return {"currency": currency, "history": rates}

# ============ GST & COMPLIANCE ENDPOINTS ============

@api_router.post("/gst/input-credit")
async def add_gst_input_credit(data: GSTInputCreditCreate, user: dict = Depends(get_current_user)):
    credit_id = generate_id()
    credit_doc = {
        "id": credit_id,
        **data.model_dump(),
        "company_id": user.get("company_id", user["id"]),
        "status": "pending",
        "created_at": now_iso()
    }
    await db.gst_credits.insert_one(credit_doc)
    return {"id": credit_id, "message": "GST input credit added"}

@api_router.get("/gst/summary/monthly", response_model=List[GSTSummaryResponse])
async def get_gst_monthly_summary(year: int = None, user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    
    # Aggregate shipments by month
    months = []
    for m in range(1, 13):
        month_str = f"{year or 2024}-{m:02d}"
        shipments = await db.shipments.find({
            "company_id": company_id,
            "created_at": {"$regex": f"^{month_str}"}
        }, {"_id": 0}).to_list(500)
        
        total_value = sum(s.get("total_value", 0) for s in shipments)
        igst_paid = total_value * 0.18  # Simplified calculation
        
        months.append(GSTSummaryResponse(
            month=month_str,
            total_export_value=total_value,
            total_igst_paid=igst_paid,
            refund_eligible=igst_paid,
            refund_claimed=igst_paid * 0.6,
            refund_pending=igst_paid * 0.4
        ))
    
    return months

@api_router.get("/gst/refund/expected")
async def get_expected_refund(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    
    total_export_value = sum(s.get("total_value", 0) for s in shipments)
    expected_refund = total_export_value * 0.18 * 0.4  # Simplified
    
    return {
        "total_export_value": total_export_value,
        "igst_paid": total_export_value * 0.18,
        "refund_claimed": total_export_value * 0.18 * 0.6,
        "refund_expected": expected_refund,
        "estimated_date": (datetime.now(timezone.utc) + timedelta(days=45)).isoformat()
    }

@api_router.get("/gst/refund/status")
async def get_refund_status(user: dict = Depends(get_current_user)):
    # Return mock refund status for demo
    return {
        "pending_applications": 3,
        "total_pending_amount": 245000,
        "applications": [
            {"ref_number": "GST-REF-2024-001", "amount": 85000, "status": "processing", "filed_date": "2024-01-15"},
            {"ref_number": "GST-REF-2024-002", "amount": 92000, "status": "under_review", "filed_date": "2024-01-28"},
            {"ref_number": "GST-REF-2024-003", "amount": 68000, "status": "approved", "filed_date": "2024-02-10"}
        ]
    }

@api_router.get("/compliance/lut-status")
async def get_lut_status(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    lut = await db.compliance.find_one({"company_id": company_id, "type": "lut"}, {"_id": 0})
    
    if lut:
        return lut
    
    return {
        "status": "not_filed",
        "message": "LUT not filed for current financial year",
        "action_required": True
    }

@api_router.post("/compliance/lut-link")
async def link_lut(data: Dict[str, str], user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    lut_doc = {
        "id": generate_id(),
        "company_id": company_id,
        "type": "lut",
        "lut_number": data.get("lut_number"),
        "financial_year": data.get("financial_year", "2024-25"),
        "valid_from": data.get("valid_from"),
        "valid_until": data.get("valid_until"),
        "status": "active",
        "created_at": now_iso()
    }
    await db.compliance.insert_one(lut_doc)
    return {"message": "LUT linked successfully", "lut_number": data.get("lut_number")}

# ============ INCENTIVES ENDPOINTS ============

# RoDTEP rates by HS code (simplified)
RODTEP_RATES = {
    "61": 4.0, "62": 4.0, "63": 4.0,  # Textiles
    "84": 2.5, "85": 2.5,  # Machinery & Electronics
    "87": 3.0,  # Vehicles
    "90": 2.0,  # Instruments
    "94": 3.5,  # Furniture
}

@api_router.get("/incentives/rodtep-eligibility")
async def check_rodtep_eligibility(hs_code: str = Query(...)):
    chapter = hs_code[:2]
    rate = RODTEP_RATES.get(chapter, 0)
    
    return {
        "hs_code": hs_code,
        "chapter": chapter,
        "eligible": rate > 0,
        "rate_percent": rate,
        "scheme": "RoDTEP",
        "notes": f"Chapter {chapter} products eligible for {rate}% RoDTEP benefit" if rate > 0 else "Not eligible for RoDTEP"
    }

@api_router.post("/incentives/calculate", response_model=IncentiveResponse)
async def calculate_incentive(data: IncentiveCalculateRequest, user: dict = Depends(get_current_user)):
    total_incentive = 0
    primary_hs = data.hs_codes[0] if data.hs_codes else "00"
    chapter = primary_hs[:2]
    rate = RODTEP_RATES.get(chapter, 0)
    total_incentive = data.fob_value * (rate / 100)
    
    incentive_id = generate_id()
    incentive_doc = {
        "id": incentive_id,
        "shipment_id": data.shipment_id,
        "scheme": "RoDTEP",
        "hs_code": primary_hs,
        "fob_value": data.fob_value,
        "rate_percent": rate,
        "incentive_amount": total_incentive,
        "status": "calculated",
        "company_id": user.get("company_id", user["id"]),
        "created_at": now_iso()
    }
    await db.incentives.insert_one(incentive_doc)
    
    return IncentiveResponse(**{k: v for k, v in incentive_doc.items() if k in IncentiveResponse.model_fields})

@api_router.get("/incentives/lost-money")
async def get_lost_incentives(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    
    # Find shipments without incentive claims
    shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    claimed_shipments = await db.incentives.distinct("shipment_id", {"company_id": company_id})
    
    unclaimed = [s for s in shipments if s["id"] not in claimed_shipments]
    potential_loss = sum(s.get("total_value", 0) * 0.03 for s in unclaimed)  # Avg 3% rate
    
    return {
        "unclaimed_shipments": len(unclaimed),
        "potential_incentive_loss": potential_loss,
        "recommendation": f"Claim incentives for {len(unclaimed)} shipments to recover ₹{potential_loss:,.2f}"
    }

@api_router.get("/incentives/summary")
async def get_incentives_summary(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    incentives = await db.incentives.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    
    total = sum(i.get("incentive_amount", 0) for i in incentives)
    claimed = sum(i.get("incentive_amount", 0) for i in incentives if i.get("status") == "claimed")
    pending = sum(i.get("incentive_amount", 0) for i in incentives if i.get("status") in ["calculated", "submitted"])
    
    return {
        "total_incentives": total,
        "claimed": claimed,
        "pending": pending,
        "count": len(incentives),
        "by_scheme": {
            "RoDTEP": sum(i.get("incentive_amount", 0) for i in incentives if i.get("scheme") == "RoDTEP"),
            "RoSCTL": sum(i.get("incentive_amount", 0) for i in incentives if i.get("scheme") == "RoSCTL")
        }
    }

# ============ CONNECTOR ENGINE ENDPOINTS ============

@api_router.post("/connect/bank/initiate")
async def initiate_bank_connection(data: ConnectorInitRequest, user: dict = Depends(get_current_user)):
    job_id = generate_id()
    connector_doc = {
        "id": generate_id(),
        "job_id": job_id,
        "connector_type": "bank",
        "company_id": user.get("company_id", user["id"]),
        "status": "initiating",
        "created_at": now_iso()
    }
    await db.connectors.insert_one(connector_doc)
    
    return {"job_id": job_id, "status": "initiating", "message": "Bank connection initiated via Account Aggregator"}

@api_router.post("/connect/bank/consent")
async def bank_consent(data: Dict[str, str], user: dict = Depends(get_current_user)):
    return {"status": "consent_pending", "consent_url": "https://aa.example.com/consent", "expires_in": 300}

@api_router.get("/sync/bank")
async def sync_bank_data(user: dict = Depends(get_current_user)):
    return {
        "status": "synced",
        "last_sync": now_iso(),
        "accounts": [
            {"account_number": "****1234", "bank": "HDFC Bank", "balance": 1250000, "type": "current"},
            {"account_number": "****5678", "bank": "ICICI Bank", "balance": 850000, "type": "EEFC"}
        ]
    }

@api_router.post("/connect/gst/link")
async def link_gst(data: Dict[str, str], user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    gst_doc = {
        "id": generate_id(),
        "company_id": company_id,
        "gstin": data.get("gstin"),
        "connector_type": "gst",
        "status": "linked",
        "created_at": now_iso()
    }
    await db.connectors.insert_one(gst_doc)
    return {"status": "linked", "gstin": data.get("gstin")}

@api_router.get("/sync/gst")
async def sync_gst_data(user: dict = Depends(get_current_user)):
    return {
        "status": "synced",
        "last_sync": now_iso(),
        "data": {
            "gstr1_filed": True,
            "gstr3b_filed": True,
            "pending_returns": [],
            "input_credit_balance": 125000
        }
    }

@api_router.post("/connect/customs/link")
async def link_customs(data: Dict[str, str], user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    customs_doc = {
        "id": generate_id(),
        "company_id": company_id,
        "iec_code": data.get("iec_code"),
        "connector_type": "customs",
        "status": "linked",
        "created_at": now_iso()
    }
    await db.connectors.insert_one(customs_doc)
    return {"status": "linked", "iec_code": data.get("iec_code")}

@api_router.get("/sync/customs")
async def sync_customs_data(user: dict = Depends(get_current_user)):
    return {
        "status": "synced",
        "last_sync": now_iso(),
        "data": {
            "shipping_bills": 45,
            "pending_assessments": 2,
            "duty_drawback_pending": 75000
        }
    }

# ============ AI & FORECASTING ENDPOINTS ============

@api_router.post("/ai/query", response_model=AIQueryResponse)
async def ai_query(data: AIQueryRequest, user: dict = Depends(get_current_user)):
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=os.environ.get("EMERGENT_LLM_KEY"),
            session_id=f"export-ai-{user['id']}",
            system_message="""You are an expert AI assistant for export finance and compliance. 
            You help exporters understand GST regulations, RoDTEP/RoSCTL incentives, forex management, 
            customs procedures, and trade documentation. Provide accurate, concise, and actionable advice."""
        ).with_model("gemini", "gemini-2.5-flash")
        
        user_message = UserMessage(text=data.query)
        response = await chat.send_message(user_message)
        
        return AIQueryResponse(query=data.query, response=response, timestamp=now_iso())
    except Exception as e:
        logger.error(f"AI query error: {e}")
        return AIQueryResponse(
            query=data.query,
            response="I apologize, but I'm currently unable to process your query. Please try again later.",
            timestamp=now_iso()
        )

@api_router.get("/ai/refund-forecast")
async def get_refund_forecast(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    
    total_value = sum(s.get("total_value", 0) for s in shipments)
    
    return {
        "forecast": [
            {"month": "Jan 2025", "expected_refund": total_value * 0.02, "confidence": 0.85},
            {"month": "Feb 2025", "expected_refund": total_value * 0.025, "confidence": 0.80},
            {"month": "Mar 2025", "expected_refund": total_value * 0.03, "confidence": 0.75}
        ],
        "total_expected": total_value * 0.075,
        "notes": "Based on historical filing patterns and current pending applications"
    }

@api_router.get("/ai/cashflow-forecast")
async def get_cashflow_forecast(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    
    return {
        "forecast": [
            {"month": "Jan 2025", "inflow": 2500000, "outflow": 1800000, "net": 700000},
            {"month": "Feb 2025", "inflow": 2800000, "outflow": 2000000, "net": 800000},
            {"month": "Mar 2025", "inflow": 3200000, "outflow": 2200000, "net": 1000000}
        ],
        "alerts": [
            {"type": "warning", "message": "Large payment due in Feb from Buyer XYZ - monitor closely"}
        ]
    }

@api_router.get("/ai/incentive-optimizer")
async def get_incentive_optimizer(user: dict = Depends(get_current_user)):
    return {
        "recommendations": [
            {
                "action": "Apply for RoDTEP",
                "shipments_affected": 5,
                "potential_benefit": 125000,
                "priority": "high"
            },
            {
                "action": "Update HS codes for better rates",
                "shipments_affected": 3,
                "potential_benefit": 45000,
                "priority": "medium"
            }
        ],
        "total_opportunity": 170000
    }

@api_router.get("/ai/risk-alerts")
async def get_risk_alerts(user: dict = Depends(get_current_user)):
    return {
        "alerts": [
            {"severity": "high", "type": "payment_delay", "message": "Buyer ABC Corp - 3 invoices overdue by 45+ days", "action": "Follow up immediately"},
            {"severity": "medium", "type": "forex", "message": "USD weakening - consider hedging open positions", "action": "Review forex strategy"},
            {"severity": "low", "type": "compliance", "message": "LUT renewal due in 45 days", "action": "Plan renewal"}
        ]
    }

# ============ CREDIT INTELLIGENCE ENDPOINTS ============

@api_router.get("/credit/buyer-score/{buyer_id}", response_model=BuyerScoreResponse)
async def get_buyer_score(buyer_id: str, user: dict = Depends(get_current_user)):
    # Calculate score based on payment history
    payments = await db.payments.find({"buyer_id": buyer_id}, {"_id": 0}).to_list(100)
    
    on_time = len([p for p in payments if p.get("status") == "on_time"])
    delayed = len([p for p in payments if p.get("status") == "delayed"])
    total = len(payments)
    
    score = 750 if total == 0 else int(500 + (on_time / max(total, 1)) * 350)
    
    risk_level = "low" if score >= 700 else "medium" if score >= 500 else "high"
    
    return BuyerScoreResponse(
        buyer_id=buyer_id,
        buyer_name="Sample Buyer",
        credit_score=score,
        risk_level=risk_level,
        payment_history={"on_time": on_time, "delayed": delayed, "total": total},
        recommendation="Safe to extend credit" if risk_level == "low" else "Recommend advance payment terms"
    )

@api_router.get("/credit/company-score")
async def get_company_score(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    
    shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    payments = await db.payments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    
    total_export_value = sum(s.get("total_value", 0) for s in shipments)
    total_payments = sum(p.get("amount", 0) for p in payments)
    
    return {
        "company_score": 780,
        "factors": {
            "export_volume": {"score": 85, "trend": "up"},
            "payment_collection": {"score": 78, "trend": "stable"},
            "compliance_history": {"score": 90, "trend": "up"},
            "buyer_diversity": {"score": 70, "trend": "stable"}
        },
        "credit_limit_eligible": total_export_value * 0.5,
        "recommendations": ["Apply for export credit guarantee", "Consider ECGC coverage"]
    }

@api_router.get("/credit/payment-behavior")
async def get_payment_behavior(user: dict = Depends(get_current_user)):
    return {
        "average_collection_days": 45,
        "on_time_percentage": 78,
        "trend": "improving",
        "by_region": {
            "USA": {"avg_days": 38, "on_time": 85},
            "Europe": {"avg_days": 42, "on_time": 80},
            "Middle East": {"avg_days": 55, "on_time": 65}
        }
    }

# ============ DOCUMENT OCR ENDPOINTS ============

@api_router.post("/documents/ocr/extract")
async def extract_document(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    job_id = generate_id()
    
    # Save file and create job
    job_doc = {
        "id": job_id,
        "type": "ocr_extraction",
        "status": "processing",
        "company_id": user.get("company_id", user["id"]),
        "filename": file.filename,
        "created_at": now_iso()
    }
    await db.jobs.insert_one(job_doc)
    
    # For demo, return mock extracted data
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Document queued for OCR extraction"
    }

@api_router.post("/invoices/bulk-upload")
async def bulk_upload_invoices(files: List[UploadFile] = File(...), user: dict = Depends(get_current_user)):
    job_id = generate_id()
    
    job_doc = {
        "id": job_id,
        "type": "bulk_invoice_upload",
        "status": "processing",
        "company_id": user.get("company_id", user["id"]),
        "file_count": len(files),
        "created_at": now_iso()
    }
    await db.jobs.insert_one(job_doc)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "files_queued": len(files)
    }

# ============ FILE STORAGE ENDPOINTS ============

@api_router.post("/files/upload")
async def upload_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    file_id = generate_id()
    content = await file.read()
    
    file_doc = {
        "id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "company_id": user.get("company_id", user["id"]),
        "uploaded_by": user["id"],
        "created_at": now_iso()
    }
    await db.files.insert_one(file_doc)
    
    return {"id": file_id, "filename": file.filename, "size": len(content)}

@api_router.get("/files/{file_id}")
async def get_file(file_id: str, user: dict = Depends(get_current_user)):
    file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    return file_doc

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str, user: dict = Depends(get_current_user)):
    result = await db.files.delete_one({"id": file_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted"}

# ============ JOB STATUS ENDPOINTS ============

@api_router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    job = await db.jobs.find_one({"id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        progress=job.get("progress", 0),
        result=job.get("result"),
        created_at=job.get("created_at", now_iso())
    )

# ============ NOTIFICATION ENDPOINTS ============

@api_router.post("/notifications/send")
async def send_notification(data: NotificationCreate, user: dict = Depends(get_current_user)):
    notif_id = generate_id()
    notif_doc = {
        "id": notif_id,
        **data.model_dump(),
        "read": False,
        "created_at": now_iso()
    }
    await db.notifications.insert_one(notif_doc)
    return {"id": notif_id, "message": "Notification sent"}

@api_router.get("/notifications/history", response_model=List[NotificationResponse])
async def get_notifications(user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    return [NotificationResponse(**n) for n in notifications]

# ============ WEBHOOK ENDPOINTS ============

@api_router.post("/webhooks/whatsapp")
async def whatsapp_webhook(data: Dict[str, Any]):
    logger.info(f"WhatsApp webhook received: {data}")
    return {"status": "received"}

@api_router.post("/webhooks/bank")
async def bank_webhook(data: Dict[str, Any]):
    logger.info(f"Bank webhook received: {data}")
    return {"status": "received"}

# ============ DASHBOARD STATS ENDPOINTS ============

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    company_id = user.get("company_id", user["id"])
    
    shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    payments = await db.payments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    incentives = await db.incentives.find({"company_id": company_id}, {"_id": 0}).to_list(500)
    
    total_export_value = sum(s.get("total_value", 0) for s in shipments)
    total_payments = sum(p.get("amount", 0) for p in payments)
    total_incentives = sum(i.get("incentive_amount", 0) for i in incentives)
    
    active_shipments = len([s for s in shipments if s.get("status") not in ["completed", "cancelled"]])
    
    return {
        "total_export_value": total_export_value,
        "total_receivables": total_export_value - total_payments,
        "total_payments_received": total_payments,
        "total_incentives_earned": total_incentives,
        "active_shipments": active_shipments,
        "total_shipments": len(shipments),
        "pending_gst_refund": total_export_value * 0.18 * 0.4,
        "compliance_score": 85
    }

@api_router.get("/dashboard/charts/export-trend")
async def get_export_trend(user: dict = Depends(get_current_user)):
    # Return mock trend data
    return {
        "labels": ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "data": [450000, 520000, 480000, 610000, 580000, 720000]
    }

@api_router.get("/dashboard/charts/payment-status")
async def get_payment_status_chart(user: dict = Depends(get_current_user)):
    return {
        "labels": ["Received", "Pending", "Overdue"],
        "data": [65, 25, 10]
    }

# ============ SYSTEM ENDPOINTS ============

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": now_iso()}

@api_router.get("/metrics")
async def get_metrics():
    return {
        "uptime": "99.9%",
        "requests_today": 1250,
        "avg_response_time": "45ms"
    }

@api_router.get("/audit/logs")
async def get_audit_logs(user: dict = Depends(get_current_user), limit: int = 100):
    logs = await db.audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return logs

# ============ ROOT ENDPOINT ============

@api_router.get("/")
async def root():
    return {"message": "Exporter Finance & Compliance Platform API", "version": "1.0.0"}

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
