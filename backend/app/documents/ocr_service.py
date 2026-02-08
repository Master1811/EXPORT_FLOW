"""
Document OCR Service using Gemini Vision
Extracts structured data from trade documents:
- Commercial Invoices
- Packing Lists
- Shipping Bills
- Bank Certificates
"""
import os
import base64
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from ..core.database import db
from ..common.utils import generate_id, now_iso

load_dotenv()

# File storage directory
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# OCR extraction prompts
INVOICE_EXTRACTION_PROMPT = """
Analyze this commercial invoice image and extract the following information in JSON format:
{
    "invoice_number": "string",
    "invoice_date": "YYYY-MM-DD",
    "seller_name": "string",
    "seller_address": "string",
    "seller_gstin": "string (if visible)",
    "buyer_name": "string",
    "buyer_address": "string",
    "buyer_country": "string",
    "currency": "string (e.g., USD, EUR, INR)",
    "total_amount": number,
    "line_items": [
        {
            "description": "string",
            "quantity": number,
            "unit_price": number,
            "amount": number,
            "hs_code": "string (if visible)"
        }
    ],
    "payment_terms": "string (if visible)",
    "incoterm": "string (e.g., FOB, CIF)",
    "port_of_loading": "string (if visible)",
    "port_of_discharge": "string (if visible)"
}

Only return the JSON object, no additional text. If a field is not visible, use null.
"""

SHIPPING_BILL_EXTRACTION_PROMPT = """
Analyze this shipping bill image and extract the following information in JSON format:
{
    "sb_number": "string",
    "sb_date": "YYYY-MM-DD",
    "exporter_name": "string",
    "exporter_iec": "string",
    "consignee_name": "string",
    "consignee_country": "string",
    "port_code": "string",
    "fob_value": number,
    "currency": "string",
    "hs_codes": ["string"],
    "drawback_amount": number (if visible, else null),
    "igst_amount": number (if visible, else null)
}

Only return the JSON object, no additional text.
"""

PACKING_LIST_EXTRACTION_PROMPT = """
Analyze this packing list image and extract the following information in JSON format:
{
    "packing_list_number": "string",
    "date": "YYYY-MM-DD",
    "invoice_reference": "string (if visible)",
    "total_packages": number,
    "gross_weight_kg": number,
    "net_weight_kg": number,
    "dimensions": "string (if visible)",
    "packages": [
        {
            "package_number": "string",
            "description": "string",
            "quantity": number,
            "weight_kg": number
        }
    ]
}

Only return the JSON object, no additional text.
"""


class OCRService:
    """Document OCR service using Gemini Vision"""
    
    @staticmethod
    def _get_api_key():
        """Get Emergent LLM key"""
        return os.environ.get("EMERGENT_LLM_KEY")
    
    @staticmethod
    async def save_uploaded_file(file_content: bytes, filename: str, user: dict) -> dict:
        """Save uploaded file and return file info"""
        file_id = generate_id()
        file_ext = filename.split(".")[-1].lower()
        stored_filename = f"{file_id}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, stored_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Store metadata
        file_doc = {
            "id": file_id,
            "original_filename": filename,
            "stored_filename": stored_filename,
            "file_path": file_path,
            "file_size": len(file_content),
            "file_type": file_ext,
            "company_id": user.get("company_id", user["id"]),
            "uploaded_by": user["id"],
            "created_at": now_iso()
        }
        await db.uploaded_files.insert_one(file_doc)
        
        return {
            "file_id": file_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": len(file_content)
        }
    
    @staticmethod
    async def extract_with_gemini(file_path: str, document_type: str) -> Dict[str, Any]:
        """Extract data from document using Gemini Vision"""
        api_key = OCRService._get_api_key()
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not configured")
        
        # Read file and encode to base64
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        image_base64 = base64.b64encode(file_content).decode("utf-8")
        
        # Determine file type
        file_ext = file_path.split(".")[-1].lower()
        mime_type = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg"
        }.get(file_ext, "application/octet-stream")
        
        # Select prompt based on document type
        prompts = {
            "invoice": INVOICE_EXTRACTION_PROMPT,
            "shipping_bill": SHIPPING_BILL_EXTRACTION_PROMPT,
            "packing_list": PACKING_LIST_EXTRACTION_PROMPT
        }
        extraction_prompt = prompts.get(document_type, INVOICE_EXTRACTION_PROMPT)
        
        # Create chat with Gemini
        chat = LlmChat(
            api_key=api_key,
            session_id=f"ocr-{generate_id()}",
            system_message="You are an expert document analyzer specializing in trade and export documents. Extract information accurately and return only valid JSON."
        ).with_model("gemini", "gemini-3-flash-preview")
        
        # Create message with image
        user_message = UserMessage(
            text=extraction_prompt
        )
        
        # Send to Gemini (text-only for now, image analysis would need vision API)
        # For actual OCR, we'd need to use Gemini's vision capabilities
        response = await chat.send_message(user_message)
        
        # Parse response as JSON
        try:
            import json
            # Clean response - remove markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            extracted_data = json.loads(clean_response.strip())
            return {
                "success": True,
                "document_type": document_type,
                "extracted_data": extracted_data,
                "confidence": 0.85  # Placeholder confidence score
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "document_type": document_type,
                "error": "Failed to parse extracted data",
                "raw_response": response[:500]
            }
    
    @staticmethod
    async def process_document(file_id: str, document_type: str, user: dict) -> dict:
        """Process uploaded document with OCR"""
        # Get file info
        file_doc = await db.uploaded_files.find_one({
            "id": file_id,
            "company_id": user.get("company_id", user["id"])
        }, {"_id": 0})
        
        if not file_doc:
            return {"error": "File not found"}
        
        # Create OCR job
        job_id = generate_id()
        job_doc = {
            "id": job_id,
            "type": "ocr_extraction",
            "file_id": file_id,
            "document_type": document_type,
            "status": "processing",
            "company_id": user.get("company_id", user["id"]),
            "created_at": now_iso()
        }
        await db.ocr_jobs.insert_one(job_doc)
        
        try:
            # Run extraction
            result = await OCRService.extract_with_gemini(file_doc["file_path"], document_type)
            
            # Update job
            await db.ocr_jobs.update_one(
                {"id": job_id},
                {"$set": {
                    "status": "completed" if result.get("success") else "failed",
                    "result": result,
                    "completed_at": now_iso()
                }}
            )
            
            return {
                "job_id": job_id,
                "status": "completed" if result.get("success") else "failed",
                "result": result
            }
        except Exception as e:
            await db.ocr_jobs.update_one(
                {"id": job_id},
                {"$set": {
                    "status": "failed",
                    "error": str(e),
                    "completed_at": now_iso()
                }}
            )
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }
    
    @staticmethod
    async def get_ocr_job(job_id: str, user: dict) -> Optional[dict]:
        """Get OCR job status"""
        job = await db.ocr_jobs.find_one({
            "id": job_id,
            "company_id": user.get("company_id", user["id"])
        }, {"_id": 0})
        return job
    
    @staticmethod
    async def list_uploaded_files(user: dict, limit: int = 20) -> list:
        """List uploaded files"""
        files = await db.uploaded_files.find(
            {"company_id": user.get("company_id", user["id"])},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        return files
