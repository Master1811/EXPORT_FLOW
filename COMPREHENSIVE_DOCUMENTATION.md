# ExportFlow Platform - Comprehensive Documentation

## Version 2.0 - Security & Scalability Overhaul
**Last Updated:** February 2026

---

## Executive Summary

This document details the complete architectural overhaul of ExportFlow, addressing critical security vulnerabilities, scalability issues, and implementing three major revenue-recovery features for export finance compliance.

---

## Table of Contents

1. [Critical Fixes Implemented](#critical-fixes-implemented)
2. [New Features](#new-features)
3. [Security Architecture](#security-architecture)
4. [Scalability Improvements](#scalability-improvements)
5. [API Reference](#api-reference)
6. [Testing & Quality Assurance](#testing--quality-assurance)
7. [Deployment Notes](#deployment-notes)

---

## Critical Fixes Implemented

### 1. Storage Architecture - Eliminated /tmp Usage

**Previous Issue:** Local `/tmp` file storage causing guaranteed data loss in container restarts.

**Solution:** Implemented `SecureStorageService` (`/app/backend/app/services/secure_storage_service.py`)
- **S3-Compatible Object Storage** with tenant-scoped paths: `tenant/{company_id}/{doc_type}/{year}/{month}/{filename}`
- **Fallback to MongoDB** when S3 credentials not available
- **Magic-byte validation** for all file uploads
- **No /tmp usage** - all file operations use `io.BytesIO()` in memory

```python
# Tenant-scoped path generation
def get_tenant_path(company_id, doc_type, filename):
    return f"tenant/{company_id}/{doc_type}/{year}/{month}/{filename}"
```

### 2. Tenant Authorization - Zero Cross-Tenant Leakage

**Previous Issue:** Missing tenant authorization checks enabling cross-tenant data exposure.

**Solution:** Implemented `TenantAuthService` (`/app/backend/app/services/tenant_auth_service.py`)
- **Strict ownership verification** for all resources: shipments, documents, payments, buyers, companies
- **Automatic company_id filtering** on all queries
- **Access attempt logging** for security auditing
- **IDOR protection** on every data access

```python
# Every data access goes through ownership verification
resource = await TenantAuthService.verify_ownership(
    resource_type="shipment", 
    resource_id=shipment_id, 
    user=current_user
)
```

### 3. Authentication - All Endpoints Protected

**Previous Issue:** Unauthenticated file and audit endpoints.

**Solution:** 
- All routes in `/app/backend/app/services/router.py` require `Depends(get_current_user)`
- JWT token validation on every request
- User context extracted for tenant isolation

### 4. Scoring System - Real Aggregation Pipelines

**Previous Issue:** Hardcoded mock scoring values in live APIs.

**Solution:** Implemented `CreditScoringService` (`/app/backend/app/services/credit_scoring_service.py`)
- **MongoDB aggregation pipelines** for buyer scoring:
  - Payment timeliness (40%)
  - Order volume consistency (20%)
  - Payment amount reliability (20%)
  - Relationship length (10%)
  - Recent behavior trend (10%)
- **Company scoring** with export volume, collection rate, compliance history
- **Full audit trail** for every score lookup

```python
# Real aggregation-based scoring
pipeline = [
    {"$match": {"buyer_id": buyer_id, "company_id": company_id}},
    {"$group": {
        "_id": "$buyer_id",
        "total_payments": {"$sum": 1},
        "on_time_count": {"$sum": {"$cond": [...]}}
    }}
]
```

### 5. PDF Handling - Proper Text Extraction

**Previous Issue:** Broken PDF handling sending empty payloads to Gemini.

**Solution:** `EnhancedDocumentService` (`/app/backend/app/services/document_service.py`)
- **PyPDF2 text extraction** before AI processing
- **Content validation** - rejects empty/insufficient text
- **Proper error handling** with meaningful messages

```python
def extract_pdf_text(content: bytes) -> str:
    pdf_file = io.BytesIO(content)
    reader = PyPDF2.PdfReader(pdf_file)
    text_parts = [page.extract_text() for page in reader.pages]
    return "\n".join(text_parts)
```

### 6. Startup Handlers - Unified Initialization

**Previous Issue:** Duplicate startup handlers preventing index creation.

**Solution:** Single unified startup event in `/app/backend/app/main.py`:
```python
@app.on_event("startup")
async def startup():
    configure_logging()
    await ensure_indexes()  # Creates all DB indexes
    # Initialize metrics with actual counts
    total_users = await db.users.count_documents({})
    users_registered.set(total_users)
```

### 7. Health Check - Accurate Dependency Status

**Previous Issue:** Health check always returning healthy regardless of database state.

**Solution:** Real dependency checking:
```python
@app.get("/api/health")
async def health_check():
    try:
        await db.command("ping")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "checks": {"database": db_status}
    }
```

### 8. Dashboard Queries - Aggregation Pipelines

**Previous Issue:** Dashboard collection scans that will fail at scale.

**Solution:** All dashboard data fetched via optimized aggregation pipelines in scoring and risk services.

### 9. DocumentService - Full Implementation

**Previous Issue:** Stubbed DocumentService methods causing silent processing failures.

**Solution:** Complete implementation with:
- `upload_document()` - Full validation and storage
- `fetch_document()` - Tenant-verified retrieval
- `list_documents()` - Filtered listing
- `delete_document()` - Secure deletion with audit
- `ai_process_document()` - Gemini integration with proper PDF handling
- `validate_document()` - Business rule validation

### 10. OFAC Screening - Export Compliance

**Previous Issue:** Missing OFAC/sanctions screening required for export compliance.

**Solution:** `OFACScreeningService` (`/app/backend/app/services/ofac_screening_service.py`)
- Name matching against SDN list
- Country-based risk assessment
- Fuzzy matching for name variations
- Full audit trail for all screenings

```python
result = await OFACScreeningService.screen_entity(
    entity_name="Buyer Corp",
    entity_type="buyer",
    country_code="DE",
    company_id=company_id
)
# Returns: is_clear, risk_score, matches, screening_id
```

### 11. Audit Logging - Comprehensive Trails

**Previous Issue:** Lack of audit logging for score access.

**Solution:** Every sensitive operation logged:
- Credit score lookups
- Document uploads/downloads
- Payment realizations
- OFAC screenings
- RBI letter generation

---

## New Features

### Feature 1: DGFT-Ready Excel Generator

**File:** `/app/backend/app/services/dgft_service.py`

**Endpoint:** `GET /api/dgft/export`

**Capabilities:**
- Generates validated .xlsx matching official DGFT bulk eBRC upload template
- Async join between shipments and connectors collections
- Maps: Shipping Bill, IEC, AD Code, Invoice, IRM Reference, Bank AD Code
- **Red highlighting** for missing required fields
- **Yellow highlighting** for missing optional fields
- Data Quality Summary sheet

### Feature 2: Digital Audit Vault

**File:** `/app/backend/app/services/audit_vault_service.py`

**Endpoints:**
- `POST /api/audit-vault/generate/{shipment_id}` - Start package generation
- `GET /api/audit-vault/status/{job_id}` - Check progress
- `GET /api/audit-vault/download/{package_id}` - Download ZIP

**Capabilities:**
- PDF cover sheet with WeasyPrint (HTML/CSS to PDF)
- FEMA 270-day compliance check
- Background task processing
- Time-limited signed URLs (24 hours)
- Actual document bundling from storage

### Feature 3: RBI 9-Month Risk Clock

**File:** `/app/backend/app/services/risk_clock_service.py`

**Endpoints:**
- `GET /api/risk-clock` - Full dashboard data
- `GET /api/risk-clock/aging-summary` - Chart data
- `POST /api/risk-clock/realize/{shipment_id}` - Record payment
- `POST /api/risk-clock/draft-letter/{shipment_id}` - AI letter generation

**Capabilities:**
- MongoDB aggregation pipeline for age calculation
- Risk categorization: CRITICAL (>240d), WARNING (>210d), MONITOR (>180d)
- Gemini 3 Flash AI for RBI extension letter drafting
- One-click payment realization

---

## Security Architecture

### Multi-Tenant Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                      API Request                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              JWT Authentication Middleware                   │
│         (Validates token, extracts user context)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              TenantAuthService.verify_ownership()           │
│         (Checks company_id matches resource owner)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Access Layer                         │
│              (All queries include company_id)               │
└─────────────────────────────────────────────────────────────┘
```

### File Security

1. **Magic-byte validation** - Prevents file type spoofing
2. **Size limits** - Per content type (PDF: 50MB, Images: 10MB)
3. **Tenant-scoped paths** - Files isolated by company
4. **Presigned URLs** - Time-limited access

---

## API Reference

### Export Features Router

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dgft/export` | GET | Download DGFT eBRC Excel |
| `/api/dgft/validate` | GET | Validate DGFT data |
| `/api/audit-vault/generate/{shipment_id}` | POST | Generate audit package |
| `/api/audit-vault/status/{job_id}` | GET | Check job status |
| `/api/audit-vault/download/{package_id}` | GET | Download package |
| `/api/risk-clock` | GET | Risk clock dashboard |
| `/api/risk-clock/aging-summary` | GET | Aging distribution |
| `/api/risk-clock/realize/{shipment_id}` | POST | Record payment |
| `/api/risk-clock/draft-letter/{shipment_id}` | POST | AI letter draft |
| `/api/compliance/ofac-screen` | POST | OFAC screening |
| `/api/credit/buyer-score/{buyer_id}` | GET | Buyer credit score |
| `/api/credit/company-score` | GET | Company credit score |
| `/api/files/secure-upload` | POST | Secure file upload |
| `/api/documents/upload` | POST | Document upload |
| `/api/documents/{id}/ai-process` | POST | AI extraction |

---

## Testing & Quality Assurance

### Locust Stress Tests

**File:** `/app/locust/locustfile.py`

Simulates 1,000 concurrent users:
- Risk clock queries
- Document bundling
- DGFT exports
- Credit score lookups

### Unit Tests

**File:** `/app/backend/tests/test_dgft_excel.py`

- Date format validation (ISO to DD/MM/YYYY)
- Numeric type validation (floats for amounts)
- Magic-byte validation
- FEMA compliance checks

---

## Deployment Notes

### Environment Variables

```bash
MONGO_URL="mongodb://..."
DB_NAME="exportflow_db"
JWT_SECRET_KEY="..."
EMERGENT_LLM_KEY="sk-emergent-..."
AWS_ACCESS_KEY_ID="..."  # Optional - falls back to MongoDB
AWS_SECRET_ACCESS_KEY="..."
AWS_S3_BUCKET="exportflow-documents"
```

### Database Indexes

Created automatically on startup:
- `shipments.company_id`
- `documents.company_id`
- `payments.company_id`
- `audit_logs.company_id`
- `credit_scores.company_id`

---

## Summary of Guarantees

✅ **Zero cross-tenant leakage** - All data access verified against company_id
✅ **Compliance-grade auditability** - Every sensitive operation logged
✅ **Reliable document persistence** - S3 with MongoDB fallback
✅ **Scalable risk scoring** - Aggregation pipelines, not collection scans
✅ **Production-ready health checks** - Real dependency status
✅ **OFAC compliance** - Sanctions screening for export workflows
