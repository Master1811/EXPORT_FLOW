"""
Feature 2: Digital Audit Vault & Smart Cover Sheet
Automated Audit Package generator with PDF cover sheet and ZIP bundling.
Uses proper PDF handling and secure storage.
"""

import io
import zipfile
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import logging
from jinja2 import Environment, BaseLoader
from fastapi import HTTPException, BackgroundTasks

from ..core.database import db
from ..common.utils import generate_id, now_iso
from .tenant_auth_service import TenantAuthService
from .secure_storage_service import SecureStorageService

logger = logging.getLogger(__name__)

FEMA_REALIZATION_WINDOW_DAYS = 270

# HTML Template for Audit Cover Sheet
AUDIT_COVER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; font-size: 11pt; line-height: 1.5; color: #1a1a2e; padding: 40px; background: white; }
        .header { border-bottom: 3px solid #1f4e79; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { font-size: 24pt; color: #1f4e79; margin-bottom: 5px; }
        .header .subtitle { color: #666; font-size: 12pt; }
        .company-info { display: flex; justify-content: space-between; margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .company-info .label { font-size: 9pt; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
        .company-info .value { font-weight: 600; font-size: 12pt; margin-top: 4px; }
        .shipment-details { margin-bottom: 30px; }
        .shipment-details h2 { font-size: 14pt; color: #1f4e79; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #e0e0e0; }
        .details-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
        .detail-item { padding: 12px; background: #f8f9fa; border-radius: 6px; }
        .detail-item .label { font-size: 9pt; color: #666; text-transform: uppercase; }
        .detail-item .value { font-weight: 600; font-size: 11pt; margin-top: 4px; }
        .compliance-section { margin-bottom: 30px; padding: 20px; border-radius: 8px; }
        .compliance-section.pass { background: #d4edda; border: 1px solid #28a745; }
        .compliance-section.fail { background: #f8d7da; border: 1px solid #dc3545; }
        .compliance-section.warning { background: #fff3cd; border: 1px solid #ffc107; }
        .compliance-section h2 { font-size: 14pt; margin-bottom: 15px; }
        .compliance-section.pass h2 { color: #155724; }
        .compliance-section.fail h2 { color: #721c24; }
        .compliance-section.warning h2 { color: #856404; }
        .compliance-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(0,0,0,0.1); }
        .compliance-item:last-child { border-bottom: none; }
        .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 9pt; font-weight: 600; text-transform: uppercase; }
        .status-badge.compliant { background: #28a745; color: white; }
        .status-badge.non-compliant { background: #dc3545; color: white; }
        .status-badge.pending { background: #ffc107; color: #1a1a2e; }
        .documents-section { margin-bottom: 30px; }
        .documents-section h2 { font-size: 14pt; color: #1f4e79; margin-bottom: 15px; }
        .document-list { border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; }
        .document-row { display: flex; justify-content: space-between; padding: 12px 15px; border-bottom: 1px solid #e0e0e0; }
        .document-row:last-child { border-bottom: none; }
        .document-row:nth-child(even) { background: #f8f9fa; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 9pt; color: #666; text-align: center; }
        .signature-section { margin-top: 50px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 40px; }
        .signature-box { padding-top: 60px; border-top: 1px solid #333; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AUDIT COVER SHEET</h1>
        <div class="subtitle">Export Shipment Compliance Package</div>
    </div>
    <div class="company-info">
        <div><div class="label">Exporter</div><div class="value">{{ company_name }}</div></div>
        <div><div class="label">IEC Code</div><div class="value">{{ iec_code }}</div></div>
        <div><div class="label">Report Generated</div><div class="value">{{ generation_date }}</div></div>
    </div>
    <div class="shipment-details">
        <h2>Shipment Information</h2>
        <div class="details-grid">
            <div class="detail-item"><div class="label">Shipment Number</div><div class="value">{{ shipment_number }}</div></div>
            <div class="detail-item"><div class="label">Shipping Bill No.</div><div class="value">{{ shipping_bill_no or 'N/A' }}</div></div>
            <div class="detail-item"><div class="label">Shipping Bill Date</div><div class="value">{{ shipping_bill_date or 'N/A' }}</div></div>
            <div class="detail-item"><div class="label">Buyer</div><div class="value">{{ buyer_name }}</div></div>
            <div class="detail-item"><div class="label">Destination</div><div class="value">{{ buyer_country }}</div></div>
            <div class="detail-item"><div class="label">Port</div><div class="value">{{ origin_port }} - {{ destination_port }}</div></div>
            <div class="detail-item"><div class="label">Invoice Value</div><div class="value">{{ currency }} {{ total_value }}</div></div>
            <div class="detail-item"><div class="label">FOB Value (INR)</div><div class="value">Rs {{ fob_value_inr }}</div></div>
            <div class="detail-item"><div class="label">e-BRC Status</div><div class="value">{{ ebrc_status }}</div></div>
        </div>
    </div>
    <div class="compliance-section {{ compliance_class }}">
        <h2>Compliance Health Summary</h2>
        <div class="compliance-item"><span>FEMA Compliance (270-day Realization)</span><span class="status-badge {{ fema_status_class }}">{{ fema_status }}</span></div>
        <div class="compliance-item"><span>Realization Days</span><span>{{ realization_days }} / 270 days</span></div>
        <div class="compliance-item"><span>Realized Amount</span><span>{{ currency }} {{ realized_amount }} ({{ realization_percentage }}%)</span></div>
        <div class="compliance-item"><span>e-BRC Filing</span><span class="status-badge {{ ebrc_status_class }}">{{ ebrc_filing_status }}</span></div>
        <div class="compliance-item"><span>Document Completeness</span><span>{{ doc_complete_count }}/{{ doc_total_count }} documents</span></div>
    </div>
    <div class="documents-section">
        <h2>Included Documents</h2>
        <div class="document-list">
            {% for doc in documents %}
            <div class="document-row"><span>{{ doc.name }}</span><span>{{ doc.type }}</span></div>
            {% endfor %}
        </div>
    </div>
    <div class="signature-section">
        <div class="signature-box"><div>Authorized Signatory</div></div>
        <div class="signature-box"><div>Date & Seal</div></div>
    </div>
    <div class="footer">
        <p>This document is auto-generated by ExportFlow Platform. Package ID: {{ package_id }}</p>
        <p>Generated on {{ generation_datetime }} | Checksum: {{ checksum }}</p>
    </div>
</body>
</html>
"""


class AuditVaultService:
    """Service for generating audit packages with PDF cover sheets."""
    
    @staticmethod
    def check_fema_compliance(shipment: Dict, payments: List[Dict]) -> Dict[str, Any]:
        """Check FEMA compliance - realization within 270-day RBI window."""
        ship_date_str = shipment.get("actual_ship_date") or shipment.get("expected_ship_date")
        if not ship_date_str:
            return {
                "compliant": False, "status": "PENDING", "days_elapsed": 0,
                "days_remaining": FEMA_REALIZATION_WINDOW_DAYS,
                "message": "Shipping date not recorded"
            }
        
        try:
            ship_date = datetime.fromisoformat(str(ship_date_str).replace("Z", "+00:00"))
        except:
            ship_date = datetime.now(timezone.utc)
        
        now = datetime.now(timezone.utc)
        days_elapsed = (now - ship_date).days
        days_remaining = FEMA_REALIZATION_WINDOW_DAYS - days_elapsed
        
        total_value = shipment.get("total_value", 0)
        realized = sum(p.get("amount", 0) for p in payments if p.get("status") in ["completed", "received", "paid"])
        realization_pct = (realized / total_value * 100) if total_value > 0 else 0
        
        if realization_pct >= 100 and days_elapsed <= FEMA_REALIZATION_WINDOW_DAYS:
            return {
                "compliant": True, "status": "COMPLIANT", "days_elapsed": days_elapsed,
                "days_remaining": days_remaining, "realized_amount": realized,
                "realization_percentage": round(realization_pct, 2),
                "message": "Full realization within FEMA window"
            }
        elif days_elapsed > FEMA_REALIZATION_WINDOW_DAYS and realization_pct < 100:
            return {
                "compliant": False, "status": "NON-COMPLIANT", "days_elapsed": days_elapsed,
                "days_remaining": days_remaining, "realized_amount": realized,
                "realization_percentage": round(realization_pct, 2),
                "message": f"FEMA window exceeded with only {realization_pct:.1f}% realization"
            }
        else:
            return {
                "compliant": True, "status": "PENDING", "days_elapsed": days_elapsed,
                "days_remaining": days_remaining, "realized_amount": realized,
                "realization_percentage": round(realization_pct, 2),
                "message": f"{days_remaining} days remaining for realization"
            }
    
    @staticmethod
    async def generate_cover_sheet_pdf(
        shipment: Dict, company: Dict, documents: List[Dict],
        fema_check: Dict, package_id: str
    ) -> bytes:
        """Generate PDF cover sheet using WeasyPrint."""
        try:
            from weasyprint import HTML
        except ImportError:
            logger.warning("WeasyPrint not available")
            return b""
        
        template_data = {
            "company_name": company.get("name") or company.get("company_name", "N/A"),
            "iec_code": company.get("iec_code") or company.get("iec", "N/A"),
            "generation_date": datetime.now(timezone.utc).strftime("%d %b %Y"),
            "generation_datetime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "shipment_number": shipment.get("shipment_number", "N/A"),
            "shipping_bill_no": None,
            "shipping_bill_date": None,
            "buyer_name": shipment.get("buyer_name", "N/A"),
            "buyer_country": shipment.get("buyer_country", "N/A"),
            "origin_port": shipment.get("origin_port", "N/A"),
            "destination_port": shipment.get("destination_port", "N/A"),
            "currency": shipment.get("currency", "USD"),
            "total_value": f"{shipment.get('total_value', 0):,.2f}",
            "fob_value_inr": f"{shipment.get('total_value', 0) * 83.5:,.2f}",
            "ebrc_status": shipment.get("ebrc_status", "Pending").upper(),
            "fema_status": fema_check["status"],
            "fema_status_class": "compliant" if fema_check["compliant"] else ("pending" if fema_check["status"] == "PENDING" else "non-compliant"),
            "compliance_class": "pass" if fema_check["compliant"] else ("warning" if fema_check["status"] == "PENDING" else "fail"),
            "realization_days": fema_check["days_elapsed"],
            "realized_amount": f"{fema_check.get('realized_amount', 0):,.2f}",
            "realization_percentage": f"{fema_check.get('realization_percentage', 0):.1f}",
            "ebrc_filing_status": shipment.get("ebrc_status", "PENDING").upper(),
            "ebrc_status_class": "compliant" if shipment.get("ebrc_status") == "approved" else "pending",
            "doc_complete_count": len([d for d in documents if d.get("document_type") in ["shipping_bill", "invoice", "packing_list"]]),
            "doc_total_count": 4,
            "documents": [{"name": d.get("document_number", f"DOC-{d.get('id', 'unknown')[:8]}"), "type": d.get("document_type", "document").replace("_", " ").title()} for d in documents],
            "package_id": package_id,
            "checksum": package_id[:16]
        }
        
        for doc in documents:
            if doc.get("document_type") == "shipping_bill":
                template_data["shipping_bill_no"] = doc.get("document_number")
                break
        
        env = Environment(loader=BaseLoader())
        template = env.from_string(AUDIT_COVER_TEMPLATE)
        html_content = template.render(**template_data)
        
        try:
            return HTML(string=html_content).write_pdf()
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return html_content.encode('utf-8')
    
    @staticmethod
    async def create_audit_package(
        shipment_id: str, company_id: str, user_id: str,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Create audit package as background task."""
        # Verify ownership
        await TenantAuthService.verify_ownership(
            "shipment", shipment_id, {"company_id": company_id}
        )
        
        job_id = generate_id()
        job_doc = {
            "id": job_id, "type": "audit_package", "shipment_id": shipment_id,
            "company_id": company_id, "user_id": user_id,
            "status": "processing", "progress": 0, "created_at": now_iso()
        }
        await db.jobs.insert_one(job_doc)
        
        background_tasks.add_task(
            AuditVaultService._process_audit_package, job_id, shipment_id, company_id, user_id
        )
        
        return {"job_id": job_id, "status": "processing", "message": "Audit package generation started"}
    
    @staticmethod
    async def _process_audit_package(job_id: str, shipment_id: str, company_id: str, user_id: str):
        """Background task to process audit package."""
        try:
            shipment = await db.shipments.find_one({"id": shipment_id, "company_id": company_id}, {"_id": 0})
            company = await db.companies.find_one({"id": company_id}, {"_id": 0}) or {}
            documents = await db.documents.find({"shipment_id": shipment_id, "company_id": company_id}, {"_id": 0}).to_list(100)
            payments = await db.payments.find({"shipment_id": shipment_id, "company_id": company_id}, {"_id": 0}).to_list(100)
            
            await db.jobs.update_one({"id": job_id}, {"$set": {"progress": 20, "status": "fetching_documents"}})
            
            fema_check = AuditVaultService.check_fema_compliance(shipment, payments)
            
            await db.jobs.update_one({"id": job_id}, {"$set": {"progress": 40, "status": "generating_cover_sheet"}})
            
            package_id = generate_id()
            cover_pdf = await AuditVaultService.generate_cover_sheet_pdf(shipment, company, documents, fema_check, package_id)
            
            await db.jobs.update_one({"id": job_id}, {"$set": {"progress": 60, "status": "bundling_documents"}})
            
            # Create ZIP in memory (no /tmp usage)
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("00_Audit_Cover_Sheet.pdf", cover_pdf)
                
                import json
                manifest = {
                    "package_id": package_id, "shipment_id": shipment_id,
                    "generated_at": now_iso(), "fema_compliance": fema_check,
                    "documents": [{"id": d.get("id"), "type": d.get("document_type")} for d in documents]
                }
                zf.writestr("manifest.json", json.dumps(manifest, indent=2))
                
                # Fetch actual document files from storage
                for idx, doc in enumerate(documents, 1):
                    file_id = doc.get("file_id")
                    if file_id:
                        try:
                            content, _ = await SecureStorageService.get_file(file_id, company_id)
                            ext = doc.get("content_type", "").split("/")[-1] or "pdf"
                            zf.writestr(f"{idx:02d}_{doc.get('document_type', 'doc')}.{ext}", content)
                        except:
                            zf.writestr(f"{idx:02d}_{doc.get('document_type', 'doc')}_placeholder.txt", f"Document: {doc.get('document_type')}")
                    else:
                        zf.writestr(f"{idx:02d}_{doc.get('document_type', 'doc')}_placeholder.txt", f"Document: {doc.get('document_type')}")
            
            zip_buffer.seek(0)
            zip_data = zip_buffer.getvalue()
            checksum = hashlib.sha256(zip_data).hexdigest()[:16]
            
            await db.jobs.update_one({"id": job_id}, {"$set": {"progress": 80, "status": "saving_package"}})
            
            # Store package
            package_doc = {
                "id": package_id, "job_id": job_id, "shipment_id": shipment_id,
                "company_id": company_id, "user_id": user_id,
                "filename": f"AuditPackage_{shipment.get('shipment_number', shipment_id)}.zip",
                "size": len(zip_data), "checksum": checksum, "fema_compliance": fema_check,
                "document_count": len(documents),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
                "created_at": now_iso()
            }
            await db.audit_packages.insert_one(package_doc)
            await db.audit_package_data.insert_one({"package_id": package_id, "data": zip_data, "created_at": now_iso()})
            
            await db.jobs.update_one(
                {"id": job_id},
                {"$set": {
                    "progress": 100, "status": "completed",
                    "result": {
                        "package_id": package_id,
                        "download_url": f"/api/audit-vault/download/{package_id}",
                        "expires_at": package_doc["expires_at"],
                        "checksum": checksum, "size": len(zip_data)
                    },
                    "completed_at": now_iso()
                }}
            )
            
            # Audit log
            await db.audit_logs.insert_one({
                "id": generate_id(), "action_type": "audit_package_created",
                "resource_type": "audit_package", "resource_id": package_id,
                "company_id": company_id, "user_id": user_id,
                "details": {"shipment_id": shipment_id, "document_count": len(documents), "fema_compliant": fema_check["compliant"]},
                "timestamp": now_iso()
            })
            
        except Exception as e:
            logger.error(f"Audit package generation failed: {e}")
            await db.jobs.update_one({"id": job_id}, {"$set": {"status": "failed", "error": str(e), "completed_at": now_iso()}})
    
    @staticmethod
    async def download_package(package_id: str, company_id: str):
        """Download audit package with tenant verification."""
        package = await db.audit_packages.find_one({"id": package_id, "company_id": company_id}, {"_id": 0})
        if not package:
            raise HTTPException(status_code=404, detail="Package not found or access denied")
        
        expires_at = datetime.fromisoformat(package["expires_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=410, detail="Download link has expired")
        
        package_data = await db.audit_package_data.find_one({"package_id": package_id})
        if not package_data:
            raise HTTPException(status_code=404, detail="Package data not found")
        
        return package_data["data"], package["filename"]
