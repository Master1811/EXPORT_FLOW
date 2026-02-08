"""
Notification Service for ExportFlow
Handles email notifications for:
- e-BRC deadline alerts (15 days before)
- Overdue payment reminders (60+ days)
- Export job completion notifications
"""
import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from ..core.database import db
from ..common.utils import generate_id, now_iso

# Email templates
def get_ebrc_alert_template(shipment: dict, days_remaining: int) -> str:
    """Generate e-BRC deadline alert email HTML"""
    urgency = "URGENT" if days_remaining <= 7 else "REMINDER"
    color = "#EF4444" if days_remaining <= 7 else "#F59E0B"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 30px; text-align: center; }}
            .urgency {{ background: {color}; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; margin-bottom: 10px; }}
            .content {{ padding: 30px; }}
            .shipment-card {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid {color}; }}
            .label {{ color: #6b7280; font-size: 12px; text-transform: uppercase; margin-bottom: 5px; }}
            .value {{ font-size: 16px; font-weight: 600; color: #1f2937; }}
            .days-box {{ text-align: center; background: {color}; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .days-number {{ font-size: 48px; font-weight: bold; }}
            .cta-button {{ display: inline-block; background: #3B82F6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span class="urgency">{urgency}</span>
                <h1 style="margin: 10px 0;">e-BRC Filing Deadline Alert</h1>
            </div>
            <div class="content">
                <p>Your e-BRC filing deadline is approaching. Please take action to avoid compliance issues.</p>
                
                <div class="shipment-card">
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="margin-bottom: 15px;">
                            <div class="label">Shipment Number</div>
                            <div class="value">{shipment.get('shipment_number', 'N/A')}</div>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <div class="label">Buyer</div>
                            <div class="value">{shipment.get('buyer_name', 'N/A')}</div>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <div class="label">Invoice Value</div>
                            <div class="value">₹{shipment.get('total_value', 0):,.2f}</div>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <div class="label">Destination</div>
                            <div class="value">{shipment.get('buyer_country', 'N/A')}</div>
                        </div>
                    </div>
                </div>
                
                <div class="days-box">
                    <div class="days-number">{days_remaining}</div>
                    <div>days remaining</div>
                </div>
                
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Gather required documents (Shipping Bill, Invoice, Bank Realization Certificate)</li>
                    <li>Log into DGFT portal and file e-BRC</li>
                    <li>Update status in ExportFlow once filed</li>
                </ol>
                
                <center>
                    <a href="#" class="cta-button">View in ExportFlow</a>
                </center>
            </div>
            <div class="footer">
                <p>This is an automated alert from ExportFlow. Do not reply to this email.</p>
                <p>© 2025 ExportFlow - Exporter Finance & Compliance Platform</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_overdue_payment_template(receivable: dict) -> str:
    """Generate overdue payment reminder email HTML"""
    days_overdue = receivable.get('days_outstanding', 0)
    severity = "HIGH" if days_overdue > 90 else "MEDIUM"
    color = "#EF4444" if days_overdue > 90 else "#F59E0B"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #7c2d12 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; }}
            .severity {{ background: {color}; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; margin-bottom: 10px; }}
            .content {{ padding: 30px; }}
            .payment-card {{ background: #fef2f2; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid {color}; }}
            .label {{ color: #6b7280; font-size: 12px; text-transform: uppercase; margin-bottom: 5px; }}
            .value {{ font-size: 16px; font-weight: 600; color: #1f2937; }}
            .amount-box {{ text-align: center; background: {color}; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .amount {{ font-size: 36px; font-weight: bold; }}
            .cta-button {{ display: inline-block; background: #10B981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span class="severity">{severity} PRIORITY</span>
                <h1 style="margin: 10px 0;">Payment Overdue Alert</h1>
            </div>
            <div class="content">
                <p>The following payment is overdue and requires immediate attention.</p>
                
                <div class="payment-card">
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="margin-bottom: 15px;">
                            <div class="label">Shipment</div>
                            <div class="value">{receivable.get('shipment_number', 'N/A')}</div>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <div class="label">Buyer</div>
                            <div class="value">{receivable.get('buyer_name', 'N/A')}</div>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <div class="label">Days Overdue</div>
                            <div class="value" style="color: {color};">{days_overdue} days</div>
                        </div>
                    </div>
                </div>
                
                <div class="amount-box">
                    <div style="font-size: 14px; margin-bottom: 5px;">Outstanding Amount</div>
                    <div class="amount">₹{receivable.get('outstanding', 0):,.2f}</div>
                </div>
                
                <p><strong>Recommended Actions:</strong></p>
                <ul>
                    <li>Contact buyer to follow up on payment</li>
                    <li>Review payment terms and any disputes</li>
                    <li>Consider escalation if no response</li>
                </ul>
                
                <center>
                    <a href="#" class="cta-button">Record Payment</a>
                </center>
            </div>
            <div class="footer">
                <p>This is an automated alert from ExportFlow. Do not reply to this email.</p>
                <p>© 2025 ExportFlow - Exporter Finance & Compliance Platform</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_export_ready_template(job: dict) -> str:
    """Generate export ready notification email HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #065f46 0%, #10B981 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .export-card {{ background: #f0fdf4; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid #10B981; }}
            .label {{ color: #6b7280; font-size: 12px; text-transform: uppercase; margin-bottom: 5px; }}
            .value {{ font-size: 16px; font-weight: 600; color: #1f2937; }}
            .cta-button {{ display: inline-block; background: #3B82F6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 10px 0;">✓ Export Ready for Download</h1>
            </div>
            <div class="content">
                <p>Your export has been generated and is ready for download.</p>
                
                <div class="export-card">
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="margin-bottom: 15px;">
                            <div class="label">Export Type</div>
                            <div class="value">{job.get('export_type', 'N/A').title()}</div>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <div class="label">Format</div>
                            <div class="value">{job.get('format', 'N/A').upper()}</div>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <div class="label">Total Records</div>
                            <div class="value">{job.get('total_rows', 0)} rows</div>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <div class="label">File Name</div>
                            <div class="value">{job.get('file_name', 'N/A')}</div>
                        </div>
                    </div>
                </div>
                
                <center>
                    <a href="#" class="cta-button">Download Export</a>
                </center>
                
                <p style="color: #6b7280; font-size: 12px;">Note: This download link will expire in 7 days.</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from ExportFlow.</p>
                <p>© 2025 ExportFlow - Exporter Finance & Compliance Platform</p>
            </div>
        </div>
    </body>
    </html>
    """


class NotificationService:
    """Email notification service using SendGrid"""
    
    @staticmethod
    def _get_sendgrid_client():
        """Get SendGrid client"""
        api_key = os.environ.get("SENDGRID_API_KEY")
        if not api_key:
            raise ValueError("SENDGRID_API_KEY not configured")
        return SendGridAPIClient(api_key)
    
    @staticmethod
    def _get_sender_email():
        """Get sender email"""
        return os.environ.get("SENDER_EMAIL", "noreply@exportflow.com")
    
    @staticmethod
    async def send_email(to_email: str, subject: str, html_content: str) -> dict:
        """Send email via SendGrid"""
        try:
            message = Mail(
                from_email=NotificationService._get_sender_email(),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = NotificationService._get_sendgrid_client()
            response = sg.send(message)
            
            # Log notification
            await db.notification_logs.insert_one({
                "id": generate_id(),
                "to_email": to_email,
                "subject": subject,
                "status": "sent" if response.status_code == 202 else "failed",
                "status_code": response.status_code,
                "created_at": now_iso()
            })
            
            return {
                "success": response.status_code == 202,
                "status_code": response.status_code
            }
        except Exception as e:
            # Log failed notification
            await db.notification_logs.insert_one({
                "id": generate_id(),
                "to_email": to_email,
                "subject": subject,
                "status": "error",
                "error": str(e),
                "created_at": now_iso()
            })
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def send_ebrc_alert(user_email: str, shipment: dict, days_remaining: int) -> dict:
        """Send e-BRC deadline alert"""
        subject = f"[Action Required] e-BRC Filing Due in {days_remaining} Days - {shipment.get('shipment_number')}"
        html_content = get_ebrc_alert_template(shipment, days_remaining)
        return await NotificationService.send_email(user_email, subject, html_content)
    
    @staticmethod
    async def send_overdue_payment_alert(user_email: str, receivable: dict) -> dict:
        """Send overdue payment reminder"""
        days_overdue = receivable.get('days_outstanding', 60)
        subject = f"[Payment Overdue] {receivable.get('buyer_name')} - ₹{receivable.get('outstanding', 0):,.0f} ({days_overdue} days)"
        html_content = get_overdue_payment_template(receivable)
        return await NotificationService.send_email(user_email, subject, html_content)
    
    @staticmethod
    async def send_export_ready(user_email: str, job: dict) -> dict:
        """Send export ready notification"""
        subject = f"Your {job.get('export_type', 'data').title()} Export is Ready"
        html_content = get_export_ready_template(job)
        return await NotificationService.send_email(user_email, subject, html_content)
    
    @staticmethod
    async def check_and_send_alerts(company_id: str, user_email: str) -> dict:
        """Check for alerts and send notifications"""
        alerts_sent = {"ebrc": 0, "overdue": 0, "errors": []}
        now = datetime.now(timezone.utc)
        
        # Check e-BRC deadlines (alert if <= 15 days remaining)
        shipments = await db.shipments.find({
            "company_id": company_id,
            "ebrc_status": "pending",
            "status": {"$in": ["shipped", "delivered", "completed"]}
        }, {"_id": 0}).to_list(500)
        
        for s in shipments:
            if s.get("ebrc_due_date"):
                try:
                    due_date = datetime.fromisoformat(s["ebrc_due_date"].replace("Z", "+00:00"))
                    days_remaining = (due_date - now).days
                    
                    if 0 < days_remaining <= 15:
                        result = await NotificationService.send_ebrc_alert(user_email, s, days_remaining)
                        if result["success"]:
                            alerts_sent["ebrc"] += 1
                        else:
                            alerts_sent["errors"].append(f"e-BRC alert for {s['shipment_number']}: {result.get('error')}")
                except Exception as e:
                    alerts_sent["errors"].append(f"e-BRC check error: {str(e)}")
        
        # Check overdue payments (alert if >= 60 days)
        shipments_for_aging = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        for s in shipments_for_aging:
            payments = await db.payments.find({"shipment_id": s["id"], "company_id": company_id}, {"_id": 0}).to_list(100)
            total_paid = sum(p.get("amount", 0) for p in payments)
            outstanding = s["total_value"] - total_paid
            
            if outstanding > 0:
                try:
                    created = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))
                    days_outstanding = (now - created).days
                    
                    if days_outstanding >= 60:
                        receivable = {
                            "shipment_number": s.get("shipment_number"),
                            "buyer_name": s.get("buyer_name"),
                            "outstanding": outstanding,
                            "days_outstanding": days_outstanding
                        }
                        result = await NotificationService.send_overdue_payment_alert(user_email, receivable)
                        if result["success"]:
                            alerts_sent["overdue"] += 1
                        else:
                            alerts_sent["errors"].append(f"Payment alert for {s['shipment_number']}: {result.get('error')}")
                except Exception as e:
                    alerts_sent["errors"].append(f"Payment check error: {str(e)}")
        
        return alerts_sent
    
    @staticmethod
    async def get_notification_log(company_id: str, limit: int = 50) -> List[dict]:
        """Get notification history"""
        logs = await db.notification_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        return logs
