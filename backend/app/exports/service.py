"""
Export Service for generating CSV, Excel, and PDF files asynchronously
Supports large datasets (5000+ rows) with background processing
"""
import csv
import io
import os
import asyncio
import threading
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from ..core.database import get_database
from ..common.utils import generate_id, now_iso

# Export directory
EXPORT_DIR = "/tmp/exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

# Global db reference for background tasks
_db = None

async def get_db():
    global _db
    if _db is None:
        _db = await get_database()
    return _db

class ExportJob:
    """Track export job status"""
    def __init__(self, job_id: str, export_type: str, format: str, user_id: str):
        self.job_id = job_id
        self.export_type = export_type
        self.format = format
        self.user_id = user_id
        self.status = "pending"
        self.progress = 0
        self.total_rows = 0
        self.file_path = None
        self.error = None
        self.created_at = now_iso()
        self.completed_at = None


class ExportService:
    @staticmethod
    async def create_export_job(
        export_type: str,
        format: str,
        user: dict,
        filters: Optional[dict] = None
    ) -> dict:
        """Create a new export job and start background processing"""
        from ..core.database import db
        
        job_id = generate_id()
        company_id = user.get("company_id", user["id"])
        
        # Store job in database
        job_doc = {
            "id": job_id,
            "export_type": export_type,
            "format": format,
            "user_id": user["id"],
            "company_id": company_id,
            "filters": filters or {},
            "status": "pending",
            "progress": 0,
            "total_rows": 0,
            "file_path": None,
            "file_name": None,
            "error": None,
            "created_at": now_iso(),
            "completed_at": None
        }
        await db.export_jobs.insert_one(job_doc)
        
        # Process synchronously (simpler and more reliable than background tasks)
        # For true async, you'd use Celery or similar
        try:
            await ExportService._process_export(job_id, export_type, format, company_id, filters)
        except Exception as e:
            await ExportService._update_job(job_id, "failed", 0, 0, None, None, str(e))
        
        # Get final status
        job = await db.export_jobs.find_one({"id": job_id}, {"_id": 0})
        
        return {
            "job_id": job_id,
            "status": job.get("status", "processing"),
            "message": f"Export job {'completed' if job.get('status') == 'completed' else 'processing'}. Processing {export_type} data to {format.upper()}..."
        }

    @staticmethod
    async def get_job_status(job_id: str, user: dict) -> dict:
        """Get export job status"""
        from ..core.database import db
        
        job = await db.export_jobs.find_one({
            "id": job_id,
            "company_id": user.get("company_id", user["id"])
        }, {"_id": 0})
        
        if not job:
            return {"error": "Job not found"}
        
        return {
            "job_id": job["id"],
            "status": job["status"],
            "progress": job["progress"],
            "total_rows": job["total_rows"],
            "file_name": job.get("file_name"),
            "download_url": f"/api/exports/download/{job_id}" if job["status"] == "completed" else None,
            "error": job.get("error"),
            "created_at": job["created_at"],
            "completed_at": job.get("completed_at")
        }

    @staticmethod
    async def get_file_path(job_id: str, user: dict) -> Optional[str]:
        """Get file path for download"""
        from ..core.database import db
        
        job = await db.export_jobs.find_one({
            "id": job_id,
            "company_id": user.get("company_id", user["id"]),
            "status": "completed"
        }, {"_id": 0})
        
        if job and job.get("file_path"):
            return job["file_path"], job.get("file_name", f"export.{job['format']}")
        return None, None

    @staticmethod
    async def _process_export(job_id: str, export_type: str, format: str, company_id: str, filters: dict):
        """Process export"""
        from ..core.database import db
        
        try:
            # Fetch data based on export type
            data = await ExportService._fetch_data(export_type, company_id, filters, job_id)
            
            if not data:
                await ExportService._update_job(job_id, "completed", 100, 0, None, None)
                return
            
            # Generate file
            file_name = f"{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            file_path = os.path.join(EXPORT_DIR, f"{job_id}_{file_name}")
            
            if format == "csv":
                await ExportService._generate_csv(data, file_path, job_id)
            elif format == "xlsx":
                await ExportService._generate_excel(data, file_path, job_id)
            elif format == "pdf":
                await ExportService._generate_pdf(data, file_path, job_id, export_type)
            
            await ExportService._update_job(job_id, "completed", 100, len(data), file_path, file_name)
            
        except Exception as e:
            await ExportService._update_job(job_id, "failed", 0, 0, None, None, str(e))

    @staticmethod
    async def _fetch_data(export_type: str, company_id: str, filters: dict, job_id: str) -> List[dict]:
        """Fetch data from database"""
        from ..core.database import db
        
        await ExportService._update_job(job_id, "processing", 10)
        
        if export_type == "shipments":
            query = {"company_id": company_id}
            if filters and filters.get("status"):
                query["status"] = filters["status"]
            data = await db.shipments.find(query, {"_id": 0, "password": 0}).to_list(10000)
            
        elif export_type == "payments":
            query = {"company_id": company_id}
            data = await db.payments.find(query, {"_id": 0}).to_list(10000)
            
        elif export_type == "receivables":
            # Direct query instead of service call
            shipments = await db.shipments.find({"company_id": company_id, "status": {"$ne": "paid"}}, {"_id": 0}).to_list(500)
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            data = []
            for s in shipments:
                payments = await db.payments.find({"shipment_id": s["id"], "company_id": company_id}, {"_id": 0}).to_list(100)
                total_paid = sum(p.get("amount", 0) for p in payments)
                outstanding = s["total_value"] - total_paid
                if outstanding > 0:
                    created = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))
                    days_outstanding = (now - created).days
                    data.append({
                        "shipment_number": s.get("shipment_number"),
                        "buyer_name": s.get("buyer_name"),
                        "buyer_country": s.get("buyer_country", ""),
                        "total_value": s["total_value"],
                        "currency": s.get("currency", "INR"),
                        "paid": total_paid,
                        "outstanding": outstanding,
                        "status": s.get("status"),
                        "days_outstanding": days_outstanding
                    })
            
        elif export_type == "incentives":
            query = {"company_id": company_id}
            shipments = await db.shipments.find(query, {"_id": 0}).to_list(10000)
            from ..incentives.hs_database import get_hs_code_info
            data = []
            for s in shipments:
                incentive_data = {
                    "shipment_number": s.get("shipment_number"),
                    "buyer_name": s.get("buyer_name"),
                    "total_value": s.get("total_value"),
                    "currency": s.get("currency"),
                    "hs_codes": ", ".join(s.get("hs_codes", [])),
                    "status": s.get("status")
                }
                # Add potential incentive calculation
                hs_codes = s.get("hs_codes", [])
                if hs_codes:
                    total_rate = 0
                    for code in hs_codes:
                        info = get_hs_code_info(code)
                        total_rate += info.get("rodtep", 0) + info.get("drawback", 0)
                    avg_rate = total_rate / len(hs_codes) if hs_codes else 0
                    incentive_data["potential_incentive"] = s.get("total_value", 0) * avg_rate / 100
                else:
                    incentive_data["potential_incentive"] = 0
                data.append(incentive_data)
        else:
            data = []
        
        await ExportService._update_job(job_id, "processing", 30, len(data))
        return data

    @staticmethod
    async def _generate_csv(data: List[dict], file_path: str, job_id: str):
        """Generate CSV file"""
        if not data:
            return
        
        await ExportService._update_job(job_id, "processing", 50)
        
        headers = list(data[0].keys())
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            batch_size = 1000
            for i, row in enumerate(data):
                writer.writerow(row)
                if i % batch_size == 0:
                    progress = 50 + int((i / len(data)) * 45)
                    await ExportService._update_job(job_id, "processing", progress)

    @staticmethod
    async def _generate_excel(data: List[dict], file_path: str, job_id: str):
        """Generate Excel file with xlsxwriter for better performance"""
        import xlsxwriter
        
        if not data:
            return
        
        await ExportService._update_job(job_id, "processing", 50)
        
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet("Export")
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#3B82F6',
            'font_color': 'white',
            'border': 1
        })
        
        # Currency format
        currency_format = workbook.add_format({'num_format': '₹#,##0.00'})
        
        headers = list(data[0].keys())
        for col, header in enumerate(headers):
            worksheet.write(0, col, header.replace("_", " ").title(), header_format)
        
        # Data rows
        batch_size = 1000
        for row_num, row_data in enumerate(data, 1):
            for col, header in enumerate(headers):
                value = row_data.get(header, "")
                if isinstance(value, (int, float)) and header in ["total_value", "outstanding", "amount", "potential_incentive"]:
                    worksheet.write_number(row_num, col, value, currency_format)
                else:
                    worksheet.write(row_num, col, str(value) if value else "")
            
            if row_num % batch_size == 0:
                progress = 50 + int((row_num / len(data)) * 45)
                await ExportService._update_job(job_id, "processing", progress)
        
        # Auto-fit columns
        for col, header in enumerate(headers):
            max_len = max(len(str(header)), max(len(str(row.get(header, ""))) for row in data[:100]))
            worksheet.set_column(col, col, min(max_len + 2, 50))
        
        workbook.close()

    @staticmethod
    async def _generate_pdf(data: List[dict], file_path: str, job_id: str, export_type: str):
        """Generate PDF file with reportlab"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        
        if not data:
            return
        
        await ExportService._update_job(job_id, "processing", 50)
        
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4), topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20
        )
        title = Paragraph(f"{export_type.title()} Export Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Prepare table data
        headers = list(data[0].keys())[:8]  # Limit columns for PDF
        table_data = [[h.replace("_", " ").title() for h in headers]]
        
        for row in data[:500]:  # Limit rows for PDF (pagination would be needed for more)
            row_values = []
            for h in headers:
                val = row.get(h, "")
                if isinstance(val, float):
                    val = f"₹{val:,.2f}" if h in ["total_value", "outstanding", "amount", "potential_incentive"] else f"{val:.2f}"
                row_values.append(str(val)[:30] if val else "")  # Truncate long values
            table_data.append(row_values)
        
        await ExportService._update_job(job_id, "processing", 70)
        
        # Create table
        col_widths = [1.2*inch] * len(headers)
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
        ]))
        
        elements.append(table)
        
        # Summary
        elements.append(Spacer(1, 20))
        summary = Paragraph(f"Total Records: {len(data)}", styles['Normal'])
        elements.append(summary)
        
        doc.build(elements)

    @staticmethod
    async def _update_job(job_id: str, status: str, progress: int, total_rows: int = None, file_path: str = None, file_name: str = None, error: str = None):
        """Update job status in database"""
        from ..core.database import db
        
        update = {
            "status": status,
            "progress": progress
        }
        if total_rows is not None:
            update["total_rows"] = total_rows
        if file_path:
            update["file_path"] = file_path
        if file_name:
            update["file_name"] = file_name
        if error:
            update["error"] = error
        if status in ["completed", "failed"]:
            update["completed_at"] = now_iso()
        
        await db.export_jobs.update_one({"id": job_id}, {"$set": update})

    @staticmethod
    async def list_jobs(user: dict, limit: int = 10) -> List[dict]:
        """List recent export jobs for user"""
        from ..core.database import db
        
        jobs = await db.export_jobs.find(
            {"company_id": user.get("company_id", user["id"])},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return [{
            "job_id": j["id"],
            "export_type": j["export_type"],
            "format": j["format"],
            "status": j["status"],
            "progress": j["progress"],
            "total_rows": j["total_rows"],
            "file_name": j.get("file_name"),
            "created_at": j["created_at"],
            "completed_at": j.get("completed_at"),
            "download_url": f"/api/exports/download/{j['id']}" if j["status"] == "completed" else None
        } for j in jobs]

    @staticmethod
    async def cleanup_old_exports(days: int = 7):
        """Cleanup export files older than specified days"""
        from ..core.database import db
        import os
        from datetime import timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        old_jobs = await db.export_jobs.find({
            "created_at": {"$lt": cutoff.isoformat()}
        }).to_list(1000)
        
        for job in old_jobs:
            if job.get("file_path") and os.path.exists(job["file_path"]):
                os.remove(job["file_path"])
        
        await db.export_jobs.delete_many({"created_at": {"$lt": cutoff.isoformat()}})
