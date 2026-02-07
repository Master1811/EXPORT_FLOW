from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from starlette.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

from .core.config import settings
from .core.database import db, close_db
from .core.dependencies import get_current_user
from .common.utils import generate_id, now_iso

# Import routers
from .auth.router import router as auth_router
from .companies.router import router as companies_router
from .shipments.router import router as shipments_router
from .documents.router import router as documents_router
from .payments.router import router as payments_router
from .forex.router import router as forex_router
from .gst.router import router as gst_router
from .incentives.router import router as incentives_router
from .ai.router import router as ai_router
from .connectors.router import router as connectors_router
from .credit.router import router as credit_router
from .jobs.router import router as jobs_router
from .notifications.router import router as notifications_router
from .exports.router import router as exports_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Exporter Finance & Compliance Platform",
        description="API for managing export shipments, payments, compliance, and incentives",
        version="1.0.0"
    )

    # Include routers with /api prefix
    app.include_router(auth_router, prefix="/api")
    app.include_router(companies_router, prefix="/api")
    app.include_router(shipments_router, prefix="/api")
    app.include_router(documents_router, prefix="/api")
    app.include_router(payments_router, prefix="/api")
    app.include_router(forex_router, prefix="/api")
    app.include_router(gst_router, prefix="/api")
    app.include_router(incentives_router, prefix="/api")
    app.include_router(ai_router, prefix="/api")
    app.include_router(connectors_router, prefix="/api")
    app.include_router(credit_router, prefix="/api")
    app.include_router(jobs_router, prefix="/api")
    app.include_router(notifications_router, prefix="/api")
    app.include_router(exports_router, prefix="/api")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=settings.CORS_ORIGINS.split(','),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown():
        await close_db()

    # Root endpoints
    @app.get("/api/")
    async def root():
        return {"message": "Exporter Finance & Compliance Platform API", "version": "1.0.0"}

    @app.get("/api/health")
    async def health_check():
        return {"status": "healthy", "timestamp": now_iso()}

    @app.get("/api/metrics")
    async def get_metrics():
        return {"uptime": "99.9%", "requests_today": 1250, "avg_response_time": "45ms"}

    @app.get("/api/audit/logs")
    async def get_audit_logs(limit: int = 100):
        logs = await db.audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
        return logs

    # Dashboard endpoints
    @app.get("/api/dashboard/stats")
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

    @app.get("/api/dashboard/charts/export-trend")
    async def get_export_trend():
        return {
            "labels": ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "data": [450000, 520000, 480000, 610000, 580000, 720000]
        }

    @app.get("/api/dashboard/charts/payment-status")
    async def get_payment_status_chart():
        return {
            "labels": ["Received", "Pending", "Overdue"],
            "data": [65, 25, 10]
        }

    # File endpoints
    @app.post("/api/files/upload")
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

    @app.get("/api/files/{file_id}")
    async def get_file(file_id: str):
        file_doc = await db.files.find_one({"id": file_id}, {"_id": 0})
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        return file_doc

    @app.delete("/api/files/{file_id}")
    async def delete_file(file_id: str):
        result = await db.files.delete_one({"id": file_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "File deleted"}

    # Webhook endpoints
    @app.post("/api/webhooks/whatsapp")
    async def whatsapp_webhook(data: Dict[str, Any]):
        logger.info(f"WhatsApp webhook received: {data}")
        return {"status": "received"}

    @app.post("/api/webhooks/bank")
    async def bank_webhook(data: Dict[str, Any]):
        logger.info(f"Bank webhook received: {data}")
        return {"status": "received"}

    return app

app = create_app()
