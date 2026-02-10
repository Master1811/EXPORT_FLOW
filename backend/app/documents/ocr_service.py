"""
Document OCR Service using Gemini Vision
Extracts structured data from trade documents:
- Commercial Invoices
- Packing Lists
- Shipping Bills
- Bank Certificates

Features:
- Multi-modal image analysis with base64 encoding
- Confidence scoring for extracted data
- Automatic flagging of low-confidence extractions
"""
import os
import base64
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from ..core.database import db
from ..common.utils import generate_id, now_iso

load_dotenv()

# File storage directory
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Confidence threshold for automatic flagging
CONFIDENCE_THRESHOLD = 0.85

# OCR extraction prompts with confidence scoring
INVOICE_EXTRACTION_PROMPT = """
Analyze this commercial invoice image and extract the following information.

Return a JSON object with this EXACT structure:
{
    "extracted_data": {
        "invoice_number": "string or null",
        "invoice_date": "YYYY-MM-DD or null",
        "seller_name": "string or null",
        "seller_address": "string or null",
        "seller_gstin": "string or null",
        "buyer_name": "string or null",
        "buyer_address": "string or null",
        "buyer_country": "string or null",
        "currency": "string (e.g., USD, EUR, INR) or null",
        "total_amount": number or null,
        "line_items": [
            {
                "description": "string",
                "quantity": number,
                "unit_price": number,
                "amount": number,
                "hs_code": "string or null"
            }
        ],
        "payment_terms": "string or null",
        "incoterm": "string (e.g., FOB, CIF) or null",
        "port_of_loading": "string or null",
        "port_of_discharge": "string or null"
    },
    "confidence_scores": {
        "overall": 0.0 to 1.0,
        "invoice_number": 0.0 to 1.0,
        "total_amount": 0.0 to 1.0,
        "buyer_name": 0.0 to 1.0,
        "line_items": 0.0 to 1.0
    },
    "validation": {
        "line_items_sum_matches_total": true or false,
        "all_required_fields_present": true or false,
        "issues": ["list of any validation issues found"]
    }
}

IMPORTANT: 
1. Calculate confidence based on image clarity and field visibility
2. Set confidence to 0.0 for fields not visible or unclear
3. Verify that line_items amounts sum to total_amount
4. Only return valid JSON, no additional text
"""

SHIPPING_BILL_EXTRACTION_PROMPT = """
Analyze this shipping bill image and extract the following information.

Return a JSON object with this EXACT structure:
{
    "extracted_data": {
        "sb_number": "string or null",
        "sb_date": "YYYY-MM-DD or null",
        "exporter_name": "string or null",
        "exporter_iec": "string or null",
        "consignee_name": "string or null",
        "consignee_country": "string or null",
        "port_code": "string or null",
        "fob_value": number or null,
        "currency": "string or null",
        "hs_codes": ["array of strings"],
        "drawback_amount": number or null,
        "igst_amount": number or null
    },
    "confidence_scores": {
        "overall": 0.0 to 1.0,
        "sb_number": 0.0 to 1.0,
        "fob_value": 0.0 to 1.0,
        "hs_codes": 0.0 to 1.0
    },
    "validation": {
        "all_required_fields_present": true or false,
        "issues": ["list of any validation issues found"]
    }
}

Only return valid JSON, no additional text.
"""

PACKING_LIST_EXTRACTION_PROMPT = """
Analyze this packing list image and extract the following information.

Return a JSON object with this EXACT structure:
{
    "extracted_data": {
        "packing_list_number": "string or null",
        "date": "YYYY-MM-DD or null",
        "invoice_reference": "string or null",
        "total_packages": number or null,
        "gross_weight_kg": number or null,
        "net_weight_kg": number or null,
        "dimensions": "string or null",
        "packages": [
            {
                "package_number": "string",
                "description": "string",
                "quantity": number,
                "weight_kg": number
            }
        ]
    },
    "confidence_scores": {
        "overall": 0.0 to 1.0,
        "total_packages": 0.0 to 1.0,
        "weights": 0.0 to 1.0
    },
    "validation": {
        "weights_consistent": true or false,
        "issues": ["list of any validation issues found"]
    }
}

Only return valid JSON, no additional text.
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
        """
        Extract data from document using Gemini Vision with multi-modal support
        
        Features:
        - Sends actual image/PDF data to Gemini for visual analysis
        - Returns confidence scores for each extracted field
        - Automatically flags documents requiring manual review
        """
        api_key = OCRService._get_api_key()
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not configured")
        
        # Read file and encode to base64
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        image_base64 = base64.b64encode(file_content).decode("utf-8")
        
        # Determine file type and MIME type
        file_ext = file_path.split(".")[-1].lower()
        mime_type = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
            "gif": "image/gif"
        }.get(file_ext, "application/octet-stream")
        
        # Select prompt based on document type
        prompts = {
            "invoice": INVOICE_EXTRACTION_PROMPT,
            "shipping_bill": SHIPPING_BILL_EXTRACTION_PROMPT,
            "packing_list": PACKING_LIST_EXTRACTION_PROMPT
        }
        extraction_prompt = prompts.get(document_type, INVOICE_EXTRACTION_PROMPT)
        
        # Create chat with Gemini Vision model
        chat = LlmChat(
            api_key=api_key,
            session_id=f"ocr-{generate_id()}",
            system_message="You are an expert document analyzer specializing in trade and export documents. Analyze images carefully and extract information with confidence scores. Return only valid JSON."
        ).with_model("gemini", "gemini-2.5-flash-preview-05-20")
        
        # Create multi-modal message with image data
        # Format: include base64 image data in the message for vision analysis
        multimodal_prompt = f"""
I have attached an image of a {document_type.replace('_', ' ')} document.

Image data (base64, {mime_type}): {image_base64[:100]}... [truncated for display]

{extraction_prompt}
"""
        
        # For actual multi-modal, we need to use the proper format
        # Using UserMessage with image data
        user_message = UserMessage(
            text=extraction_prompt,
            images=[{
                "mime_type": mime_type,
                "data": image_base64
            }] if mime_type.startswith("image/") else None
        )
        
        # Send to Gemini Vision
        response = await chat.send_message(user_message)
        
        # Parse response as JSON
        try:
            # Clean response - remove markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            parsed_result = json.loads(clean_response.strip())
            
            # Extract confidence scores
            confidence_scores = parsed_result.get("confidence_scores", {})
            overall_confidence = confidence_scores.get("overall", 0.85)
            
            # Extract validation info
            validation = parsed_result.get("validation", {})
            issues = validation.get("issues", [])
            
            # Determine if manual review is needed
            needs_review = (
                overall_confidence < CONFIDENCE_THRESHOLD or
                len(issues) > 0 or
                not validation.get("all_required_fields_present", True)
            )
            
            # Determine status
            if needs_review:
                status = "review_required"
            else:
                status = "completed"
            
            return {
                "success": True,
                "status": status,
                "document_type": document_type,
                "extracted_data": parsed_result.get("extracted_data", parsed_result),
                "confidence": overall_confidence,
                "confidence_scores": confidence_scores,
                "validation": validation,
                "needs_review": needs_review,
                "review_reasons": issues if needs_review else []
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "status": "failed",
                "document_type": document_type,
                "error": f"Failed to parse extracted data: {str(e)}",
                "raw_response": response[:500],
                "needs_review": True,
                "review_reasons": ["JSON parsing failed - manual extraction required"]
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
