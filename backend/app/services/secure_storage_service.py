"""
Secure Storage Service
S3-compatible object storage with tenant-scoped paths and magic-byte validation.
"""

import os
import io
import hashlib
import magic
from typing import Optional, Tuple, Dict, Any, BinaryIO
from datetime import datetime, timezone, timedelta
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile

from ..core.config import settings
from ..core.database import db
from ..common.utils import generate_id, now_iso

logger = logging.getLogger(__name__)


# Allowed MIME types with their extensions and magic bytes signatures
ALLOWED_FILE_TYPES = {
    # Documents
    "application/pdf": {
        "extensions": [".pdf"],
        "magic_bytes": [b"%PDF-"],
        "max_size": 50 * 1024 * 1024  # 50MB
    },
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
        "extensions": [".xlsx"],
        "magic_bytes": [b"PK\x03\x04"],  # XLSX is a ZIP file
        "max_size": 25 * 1024 * 1024  # 25MB
    },
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
        "extensions": [".docx"],
        "magic_bytes": [b"PK\x03\x04"],
        "max_size": 25 * 1024 * 1024
    },
    # Images
    "image/jpeg": {
        "extensions": [".jpg", ".jpeg"],
        "magic_bytes": [b"\xff\xd8\xff"],
        "max_size": 10 * 1024 * 1024  # 10MB
    },
    "image/png": {
        "extensions": [".png"],
        "magic_bytes": [b"\x89PNG\r\n\x1a\n"],
        "max_size": 10 * 1024 * 1024
    },
    # Text
    "text/csv": {
        "extensions": [".csv"],
        "magic_bytes": None,  # CSV has no magic bytes
        "max_size": 50 * 1024 * 1024
    },
}


class SecureStorageService:
    """
    Production-ready storage service with:
    - S3-compatible object storage
    - Tenant-scoped paths (/tenant/{company_id}/...)
    - Magic-byte validation for security
    - Presigned URLs for secure downloads
    - Fallback to MongoDB GridFS for development
    """
    
    _s3_client = None
    _use_s3 = False
    
    @classmethod
    def _get_s3_client(cls):
        """Get or create S3 client"""
        if cls._s3_client is None:
            try:
                cls._s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.environ.get('AWS_REGION', 'ap-south-1')
                )
                # Test connection
                cls._s3_client.head_bucket(Bucket=os.environ.get('AWS_S3_BUCKET', 'exportflow-documents'))
                cls._use_s3 = True
                logger.info("S3 storage initialized successfully")
            except (ClientError, NoCredentialsError) as e:
                logger.warning(f"S3 not available, using MongoDB GridFS: {e}")
                cls._s3_client = None
                cls._use_s3 = False
        return cls._s3_client
    
    @staticmethod
    def validate_magic_bytes(content: bytes, expected_mime: str) -> bool:
        """
        Validate file content using magic bytes.
        Prevents file type spoofing attacks.
        """
        if expected_mime not in ALLOWED_FILE_TYPES:
            return False
        
        file_config = ALLOWED_FILE_TYPES[expected_mime]
        magic_signatures = file_config.get("magic_bytes")
        
        # If no magic bytes defined (e.g., CSV), use python-magic library
        if magic_signatures is None:
            try:
                detected_mime = magic.from_buffer(content, mime=True)
                return detected_mime == expected_mime or expected_mime.startswith("text/")
            except Exception as e:
                logger.error(f"Magic byte detection failed: {e}")
                return False
        
        # Check against known magic bytes
        for signature in magic_signatures:
            if content[:len(signature)] == signature:
                return True
        
        return False
    
    @staticmethod
    def calculate_checksum(content: bytes) -> str:
        """Calculate SHA-256 checksum for file integrity"""
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def get_tenant_path(company_id: str, doc_type: str, filename: str) -> str:
        """
        Generate tenant-scoped storage path.
        Format: tenant/{company_id}/{doc_type}/{year}/{month}/{filename}
        """
        now = datetime.now(timezone.utc)
        return f"tenant/{company_id}/{doc_type}/{now.year}/{now.month:02d}/{filename}"
    
    @classmethod
    async def upload_file(
        cls,
        file: UploadFile,
        company_id: str,
        doc_type: str = "document",
        shipment_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file with security validation.
        
        Args:
            file: FastAPI UploadFile
            company_id: Tenant identifier for path scoping
            doc_type: Document type for categorization
            shipment_id: Optional linked shipment
            user_id: Uploader's user ID
            
        Returns:
            File metadata including storage reference
            
        Raises:
            HTTPException: On validation failure
        """
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file type
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed: {content_type}"
            )
        
        # Validate file size
        max_size = ALLOWED_FILE_TYPES[content_type]["max_size"]
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_size / 1024 / 1024:.1f}MB"
            )
        
        # Magic byte validation
        if not cls.validate_magic_bytes(content, content_type):
            raise HTTPException(
                status_code=400,
                detail="File content does not match declared type (magic byte validation failed)"
            )
        
        # Generate unique filename and path
        file_id = generate_id()
        ext = os.path.splitext(file.filename or "")[1] or ".bin"
        secure_filename = f"{file_id}{ext}"
        storage_path = cls.get_tenant_path(company_id, doc_type, secure_filename)
        
        # Calculate checksum
        checksum = cls.calculate_checksum(content)
        
        # Upload to storage
        s3_client = cls._get_s3_client()
        
        if cls._use_s3 and s3_client:
            try:
                bucket = os.environ.get('AWS_S3_BUCKET', 'exportflow-documents')
                s3_client.put_object(
                    Bucket=bucket,
                    Key=storage_path,
                    Body=content,
                    ContentType=content_type,
                    Metadata={
                        'company_id': company_id,
                        'original_filename': file.filename or 'unknown',
                        'checksum': checksum,
                        'uploaded_by': user_id or 'system'
                    }
                )
                storage_backend = "s3"
            except ClientError as e:
                logger.error(f"S3 upload failed: {e}")
                raise HTTPException(status_code=500, detail="File upload failed")
        else:
            # Fallback to MongoDB GridFS-style storage
            await db.file_storage.insert_one({
                "id": file_id,
                "path": storage_path,
                "content": content,  # In production, use GridFS for large files
                "content_type": content_type,
                "created_at": now_iso()
            })
            storage_backend = "mongodb"
        
        # Create file metadata record
        file_record = {
            "id": file_id,
            "original_filename": file.filename,
            "storage_path": storage_path,
            "storage_backend": storage_backend,
            "content_type": content_type,
            "size": file_size,
            "checksum": checksum,
            "company_id": company_id,
            "shipment_id": shipment_id,
            "doc_type": doc_type,
            "uploaded_by": user_id,
            "created_at": now_iso()
        }
        await db.uploaded_files.insert_one(file_record)
        
        # Log upload for audit
        await db.audit_logs.insert_one({
            "id": generate_id(),
            "action_type": "file_upload",
            "resource_type": "uploaded_file",
            "resource_id": file_id,
            "company_id": company_id,
            "user_id": user_id,
            "details": {
                "filename": file.filename,
                "size": file_size,
                "content_type": content_type,
                "checksum": checksum
            },
            "timestamp": now_iso()
        })
        
        # Return metadata (not the content)
        file_record.pop("_id", None)
        return file_record
    
    @classmethod
    async def get_file(
        cls,
        file_id: str,
        company_id: str
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Retrieve file content with tenant verification.
        
        Args:
            file_id: File identifier
            company_id: Requesting tenant's ID (for verification)
            
        Returns:
            Tuple of (file_content, file_metadata)
            
        Raises:
            HTTPException: If file not found or access denied
        """
        # Get file metadata with tenant check
        file_record = await db.uploaded_files.find_one({
            "id": file_id,
            "company_id": company_id
        }, {"_id": 0})
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        storage_backend = file_record.get("storage_backend", "mongodb")
        storage_path = file_record.get("storage_path")
        
        if storage_backend == "s3" and cls._use_s3:
            try:
                bucket = os.environ.get('AWS_S3_BUCKET', 'exportflow-documents')
                response = cls._get_s3_client().get_object(
                    Bucket=bucket,
                    Key=storage_path
                )
                content = response['Body'].read()
            except ClientError as e:
                logger.error(f"S3 download failed: {e}")
                raise HTTPException(status_code=500, detail="File retrieval failed")
        else:
            # MongoDB fallback
            stored = await db.file_storage.find_one({"id": file_id})
            if not stored:
                raise HTTPException(status_code=404, detail="File content not found")
            content = stored.get("content", b"")
        
        return content, file_record
    
    @classmethod
    async def get_presigned_url(
        cls,
        file_id: str,
        company_id: str,
        expiry_seconds: int = 3600
    ) -> str:
        """
        Generate a time-limited presigned URL for secure download.
        
        Args:
            file_id: File identifier
            company_id: Requesting tenant's ID
            expiry_seconds: URL validity period
            
        Returns:
            Presigned URL string
        """
        # Verify access
        file_record = await db.uploaded_files.find_one({
            "id": file_id,
            "company_id": company_id
        }, {"_id": 0})
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        if cls._use_s3:
            try:
                bucket = os.environ.get('AWS_S3_BUCKET', 'exportflow-documents')
                url = cls._get_s3_client().generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': bucket,
                        'Key': file_record.get("storage_path")
                    },
                    ExpiresIn=expiry_seconds
                )
                return url
            except ClientError as e:
                logger.error(f"Presigned URL generation failed: {e}")
                raise HTTPException(status_code=500, detail="URL generation failed")
        else:
            # For MongoDB storage, return API endpoint
            return f"/api/files/download/{file_id}"
    
    @classmethod
    async def delete_file(
        cls,
        file_id: str,
        company_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Delete file with tenant verification.
        """
        # Verify ownership
        file_record = await db.uploaded_files.find_one({
            "id": file_id,
            "company_id": company_id
        }, {"_id": 0})
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        storage_backend = file_record.get("storage_backend", "mongodb")
        storage_path = file_record.get("storage_path")
        
        # Delete from storage
        if storage_backend == "s3" and cls._use_s3:
            try:
                bucket = os.environ.get('AWS_S3_BUCKET', 'exportflow-documents')
                cls._get_s3_client().delete_object(
                    Bucket=bucket,
                    Key=storage_path
                )
            except ClientError as e:
                logger.error(f"S3 delete failed: {e}")
        else:
            await db.file_storage.delete_one({"id": file_id})
        
        # Delete metadata
        await db.uploaded_files.delete_one({"id": file_id})
        
        # Log deletion
        await db.audit_logs.insert_one({
            "id": generate_id(),
            "action_type": "file_delete",
            "resource_type": "uploaded_file",
            "resource_id": file_id,
            "company_id": company_id,
            "user_id": user_id,
            "details": {
                "filename": file_record.get("original_filename"),
                "storage_path": storage_path
            },
            "timestamp": now_iso()
        })
        
        return True
    
    @classmethod
    async def list_files(
        cls,
        company_id: str,
        shipment_id: Optional[str] = None,
        doc_type: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        List files for a tenant with optional filters.
        """
        query = {"company_id": company_id}
        if shipment_id:
            query["shipment_id"] = shipment_id
        if doc_type:
            query["doc_type"] = doc_type
        
        files = await db.uploaded_files.find(
            query,
            {"_id": 0, "content": 0}  # Exclude content from listing
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return files
