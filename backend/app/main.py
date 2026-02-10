from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta

from .core.config import settings
from .core.database import db, close_db, ensure_indexes, get_pool_stats
from .core.dependencies import get_current_user
from .core.rate_limiting import setup_rate_limiting, limiter, dashboard_limit
from .core.resilient_client import get_circuit_breaker_status
from .core.structured_logging import configure_logging, logger as struct_logger
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
from .audit.router import router as audit_router
from .security.router import router as security_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_month_date_range(months_ago: int = 0) -> Tuple[str, str]:
    """Get the first and last day of a month (ISO format).
    
    Args:
        months_ago: 0 for current month, 1 for last month, etc.
    
    Returns:
        Tuple of (start_date, end_date) in ISO format
    """
    today = datetime.utcnow()
    # Calculate the date months_ago
    month = today.month - months_ago
    year = today.year
    while month <= 0:
        month += 12
        year -= 1
    
    # First day of the month
    start_date = datetime(year, month, 1)
    # Last day of the month
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    return start_date.isoformat() + "Z", end_date.isoformat() + "Z"

def calculate_metric_change(current_value: float, previous_value: float) -> Optional[Dict[str, Any]]:
    """Calculate percentage change between two values.
    
    Returns None if previous_value is 0 (no baseline for comparison).
    Returns dict with 'change' percentage and 'trend' (up/down).
    """
    if previous_value == 0:
        return None
    
    change = ((current_value - previous_value) / previous_value) * 100
    return {
        "change": abs(change),
        "trend": "up" if change >= 0 else "down"
    }

async def get_stats_for_period(company_id: str, start_date: str, end_date: str) -> Dict[str, float]:
    """Get aggregated statistics for a given date range."""
    shipments = await db.shipments.find({
        "company_id": company_id,
        "created_at": {"$gte": start_date, "$lte": end_date}
    }, {"_id": 0}).to_list(500)
    
    payments = await db.payments.find({
        "company_id": company_id,
        "created_at": {"$gte": start_date, "$lte": end_date}
    }, {"_id": 0}).to_list(500)
    
    incentives = await db.incentives.find({
        "company_id": company_id,
        "created_at": {"$gte": start_date, "$lte": end_date}
    }, {"_id": 0}).to_list(500)
    
    return {
        "export_value": sum(s.get("total_value", 0) for s in shipments),
        "payments": sum(p.get("amount", 0) for p in payments),
        "incentives": sum(i.get("incentive_amount", 0) for i in incentives)
    }

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
    app.include_router(audit_router, prefix="/api")
    app.include_router(security_router, prefix="/api")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=settings.CORS_ORIGINS.split(','),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup rate limiting
    setup_rate_limiting(app)

    # Startup event - create indexes and configure logging
    @app.on_event("startup")
    async def startup():
        configure_logging()
        await ensure_indexes()
        struct_logger.info("Application startup complete", indexes="ensured", rate_limiting="enabled")

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

    @app.get("/api/metrics/database")
    async def get_database_metrics():
        """Get database connection pool statistics"""
        pool_stats = await get_pool_stats()
        return {
            "status": "healthy" if "error" not in pool_stats else "degraded",
            "pool": pool_stats,
            "timestamp": now_iso()
        }

    @app.get("/api/metrics/circuit-breakers")
    async def get_circuit_breakers():
        """Get circuit breaker status for external services"""
        return {
            "circuit_breakers": get_circuit_breaker_status(),
            "timestamp": now_iso()
        }

    @app.get("/api/audit/logs")
    async def get_audit_logs(limit: int = 100):
        logs = await db.audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
        return logs

    # Dashboard endpoints
    @app.get("/api/dashboard/stats")
    async def get_dashboard_stats(user: dict = Depends(get_current_user)):
        company_id = user.get("company_id", user["id"])
        
        # Get current month data
        current_start, current_end = get_month_date_range(0)
        current_stats = await get_stats_for_period(company_id, current_start, current_end)
        
        # Get previous month data
        previous_start, previous_end = get_month_date_range(1)
        previous_stats = await get_stats_for_period(company_id, previous_start, previous_end)
        
        # Get all-time data for total stats
        all_shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        all_payments = await db.payments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        all_incentives = await db.incentives.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        total_export_value = sum(s.get("total_value", 0) for s in all_shipments)
        total_payments = sum(p.get("amount", 0) for p in all_payments)
        total_incentives = sum(i.get("incentive_amount", 0) for i in all_incentives)
        active_shipments = len([s for s in all_shipments if s.get("status") not in ["completed", "cancelled"]])
        
        # Calculate month-over-month changes
        export_value_change = calculate_metric_change(current_stats["export_value"], previous_stats["export_value"])
        receivables_current = current_stats["export_value"] - current_stats["payments"]
        receivables_previous = previous_stats["export_value"] - previous_stats["payments"]
        receivables_change = calculate_metric_change(receivables_current, receivables_previous)
        incentives_change = calculate_metric_change(current_stats["incentives"], previous_stats["incentives"])
        
        return {
            "total_export_value": total_export_value,
            "total_receivables": total_export_value - total_payments,
            "total_payments_received": total_payments,
            "total_incentives_earned": total_incentives,
            "active_shipments": active_shipments,
            "total_shipments": len(all_shipments),
            "pending_gst_refund": total_export_value * 0.18 * 0.4,
            "compliance_score": 85,
            # Month-over-month comparison data
            "export_value_trend": export_value_change,
            "receivables_trend": receivables_change,
            "incentives_trend": incentives_change,
            "has_previous_month_data": previous_stats["export_value"] > 0
        }

    @app.get("/api/dashboard/charts/export-trend")
    async def get_export_trend(user: dict = Depends(get_current_user)):
        company_id = user.get("company_id", user["id"])
        
        # Get shipments from last 6 months
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        shipments = await db.shipments.find({
            "company_id": company_id,
            "created_at": {"$gte": six_months_ago.isoformat() + "Z"}
        }, {"_id": 0}).to_list(500)
        
        # Group by month
        monthly_data = {}
        for shipment in shipments:
            created_at = shipment.get("created_at", "")
            if created_at:
                # Parse ISO format date
                month_key = created_at[:7]  # YYYY-MM
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += shipment.get("total_value", 0)
        
        # Generate last 6 months in order
        labels = []
        data = []
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for i in range(5, -1, -1):  # Last 6 months in chronological order
            month_date = datetime.utcnow() - timedelta(days=i*30)
            month_key = month_date.strftime("%Y-%m")
            month_label = month_names[month_date.month - 1]
            labels.append(month_label)
            data.append(monthly_data.get(month_key, 0))
        
        return {
            "labels": labels,
            "data": data
        }

    @app.get("/api/dashboard/charts/payment-status")
    async def get_payment_status_chart(user: dict = Depends(get_current_user)):
        company_id = user.get("company_id", user["id"])
        # Per-shipment receivables approach:
        # - For each shipment, compute unpaid = total_value - sum(payments for that shipment)
        # - If unpaid == 0 -> shipment considered fully paid (paid portion counts toward Received)
        # - If unpaid > 0 and shipment due_date (if available) is past -> unpaid counts as Overdue
        # - Else unpaid counts as Pending
        # Also include payments not linked to shipments: paid -> Received, unpaid/unapplied -> Pending/Overdue by due_date if present

        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(2000)
        payments = await db.payments.find({"company_id": company_id}, {"_id": 0}).to_list(4000)

        # Build payments by shipment
        payments_by_shipment = {}
        unlinked_payments = []
        for p in payments:
            sid = p.get("shipment_id")
            if sid:
                payments_by_shipment.setdefault(sid, []).append(p)
            else:
                unlinked_payments.append(p)

        received_amount = 0.0
        pending_amount = 0.0
        overdue_amount = 0.0
        now = datetime.utcnow()
        paid_statuses = {"paid", "received", "completed"}

        # Process each shipment
        for s in shipments:
            sid = s.get("id") or s.get("shipment_number")
            total = float(s.get("total_value", 0) or 0)
            # Prefer payments' inr_amount if present
            payment_list = payments_by_shipment.get(sid, [])
            paid_sum = 0.0
            for pp in payment_list:
                paid_sum += float(pp.get("inr_amount") or pp.get("amount") or 0)

            paid_applied = min(paid_sum, total)
            unpaid = max(0.0, total - paid_sum)

            received_amount += paid_applied

            # Determine due date for shipment: try explicit `due_date`, then `ebrc_due_date`, then none
            due_date_str = s.get("due_date") or s.get("ebrc_due_date") or s.get("expected_ship_date")
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                except Exception:
                    due_date = None

            if unpaid > 0:
                if due_date and due_date < now:
                    overdue_amount += unpaid
                else:
                    pending_amount += unpaid

        # Process unlinked payments
        for p in unlinked_payments:
            amt = float(p.get("inr_amount") or p.get("amount") or 0)
            status = (p.get("status") or "").lower()
            if status in paid_statuses:
                received_amount += amt
            elif status == "overdue":
                overdue_amount += amt
            else:
                # try due_date on payment
                due_date_str = p.get("due_date")
                if due_date_str:
                    try:
                        d = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                        if d < now:
                            overdue_amount += amt
                        else:
                            pending_amount += amt
                    except Exception:
                        pending_amount += amt
                else:
                    pending_amount += amt

        # If no data, return zeros
        total_export = sum(float(s.get("total_value", 0) or 0) for s in shipments)
        total_payments = sum(float(p.get("inr_amount") or p.get("amount") or 0) for p in payments)
        if total_export == 0 and total_payments == 0:
            return {"labels": ["Received", "Pending", "Overdue"], "data": [0, 0, 0]}

        return {
            "labels": ["Received", "Pending", "Overdue"],
            "data": [
                round(received_amount, 2),
                round(pending_amount, 2),
                round(overdue_amount, 2)
            ]
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
        struct_logger.info("WhatsApp webhook received", event_type=data.get("type"))
        return {"status": "received"}

    @app.post("/api/webhooks/bank")
    async def bank_webhook(data: Dict[str, Any]):
        struct_logger.info("Bank webhook received", event_type=data.get("type"))
        return {"status": "received"}

    @app.post("/api/webhooks/account-aggregator")
    async def account_aggregator_webhook(data: Dict[str, Any]):
        """
        Webhook listener for Account Aggregator (AA) bank consent updates
        
        Expected payload:
        {
            "event_type": "consent_approved" | "consent_rejected" | "data_ready" | "consent_revoked",
            "consent_id": "string",
            "customer_id": "string",
            "fip_id": "string (Financial Information Provider ID)",
            "timestamp": "ISO datetime",
            "data": { ... }
        }
        """
        event_type = data.get("event_type")
        consent_id = data.get("consent_id")
        customer_id = data.get("customer_id")
        
        struct_logger.info(
            "Account Aggregator webhook received",
            event_type=event_type,
            consent_id=consent_id
        )
        
        # Store webhook event for processing
        webhook_doc = {
            "id": generate_id(),
            "webhook_type": "account_aggregator",
            "event_type": event_type,
            "consent_id": consent_id,
            "customer_id": customer_id,
            "payload": data,
            "status": "received",
            "created_at": now_iso()
        }
        await db.webhook_events.insert_one(webhook_doc)
        
        # Process based on event type
        if event_type == "consent_approved":
            # Update connector status
            await db.connectors.update_one(
                {"consent_id": consent_id},
                {"$set": {"status": "consent_approved", "updated_at": now_iso()}}
            )
        elif event_type == "data_ready":
            # Mark data as ready for fetch
            await db.connectors.update_one(
                {"consent_id": consent_id},
                {"$set": {"status": "data_ready", "data_available": True, "updated_at": now_iso()}}
            )
        elif event_type == "consent_rejected":
            await db.connectors.update_one(
                {"consent_id": consent_id},
                {"$set": {"status": "consent_rejected", "updated_at": now_iso()}}
            )
        elif event_type == "consent_revoked":
            await db.connectors.update_one(
                {"consent_id": consent_id},
                {"$set": {"status": "consent_revoked", "updated_at": now_iso()}}
            )
        
        return {
            "status": "received",
            "event_type": event_type,
            "processed": True
        }

    return app

app = create_app()
