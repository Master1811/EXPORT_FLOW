"""
Field-Level Encryption Service (Vault Strategy)
AES-256 encryption for sensitive data fields.
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Optional, Union
import json

class EncryptionService:
    """
    AES-256-GCM encryption service for field-level data protection.
    Even database administrators cannot read plain-text financials.
    """
    
    def __init__(self):
        # Get encryption key from environment or generate deterministic key
        self._master_key = self._get_or_create_key()
    
    def _get_or_create_key(self) -> bytes:
        """Get encryption key from environment variable."""
        key_str = os.environ.get('ENCRYPTION_KEY')
        if key_str:
            # Decode base64 key from environment
            return base64.b64decode(key_str)
        else:
            # Generate a deterministic key for development (NOT for production)
            # In production, set ENCRYPTION_KEY environment variable
            secret = os.environ.get('JWT_SECRET', 'exportflow-default-secret-key-2024')
            return hashlib.sha256(secret.encode()).digest()
    
    def _derive_field_key(self, field_name: str) -> bytes:
        """Derive a unique key for each field type for added security."""
        combined = self._master_key + field_name.encode()
        return hashlib.sha256(combined).digest()
    
    def encrypt(self, plaintext: Union[str, int, float], field_name: str = "default") -> str:
        """
        Encrypt a value using AES-256-GCM.
        
        Args:
            plaintext: The value to encrypt (string, int, or float)
            field_name: Field identifier for key derivation
        
        Returns:
            Base64 encoded encrypted string with format: nonce:tag:ciphertext
        """
        if plaintext is None:
            return None
        
        # Convert to string if numeric
        if isinstance(plaintext, (int, float)):
            plaintext = json.dumps({"type": "number", "value": plaintext})
        else:
            plaintext = json.dumps({"type": "string", "value": str(plaintext)})
        
        # Generate random nonce (12 bytes for GCM)
        nonce = os.urandom(12)
        
        # Get field-specific key
        key = self._derive_field_key(field_name)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt
        ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
        
        # Combine nonce + tag + ciphertext and encode as base64
        encrypted_data = nonce + encryptor.tag + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_value: str, field_name: str = "default") -> Union[str, int, float, None]:
        """
        Decrypt an AES-256-GCM encrypted value.
        
        Args:
            encrypted_value: Base64 encoded encrypted string
            field_name: Field identifier for key derivation
        
        Returns:
            Decrypted value (original type preserved)
        """
        if encrypted_value is None or encrypted_value == "":
            return None
        
        try:
            # Decode base64
            encrypted_data = base64.b64decode(encrypted_value)
            
            # Extract components (nonce: 12 bytes, tag: 16 bytes, rest is ciphertext)
            nonce = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            # Get field-specific key
            key = self._derive_field_key(field_name)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Parse JSON to restore original type
            data = json.loads(plaintext.decode('utf-8'))
            if data["type"] == "number":
                return data["value"]
            return data["value"]
            
        except Exception as e:
            # Return original value if decryption fails (might be unencrypted legacy data)
            return encrypted_value
    
    def is_encrypted(self, value: str) -> bool:
        """Check if a value appears to be encrypted."""
        if not value or not isinstance(value, str):
            return False
        try:
            decoded = base64.b64decode(value)
            # Encrypted data should be at least 28 bytes (12 nonce + 16 tag)
            return len(decoded) >= 28
        except:
            return False
    
    def mask_value(self, value: str, visible_chars: int = 4) -> str:
        """
        Mask a sensitive value for display.
        
        Args:
            value: The value to mask
            visible_chars: Number of characters to show at the end
        
        Returns:
            Masked string (e.g., "******1234")
        """
        if not value:
            return None
        
        value_str = str(value)
        if len(value_str) <= visible_chars:
            return "*" * len(value_str)
        
        masked_length = len(value_str) - visible_chars
        return "*" * masked_length + value_str[-visible_chars:]


# Singleton instance
encryption_service = EncryptionService()


# Convenience functions
def encrypt_field(value: Union[str, int, float], field_name: str) -> str:
    """Encrypt a field value."""
    return encryption_service.encrypt(value, field_name)


def decrypt_field(value: str, field_name: str) -> Union[str, int, float]:
    """Decrypt a field value."""
    return encryption_service.decrypt(value, field_name)


def mask_field(value: str, visible_chars: int = 4) -> str:
    """Mask a field value for display."""
    return encryption_service.mask_value(value, visible_chars)


# List of sensitive fields that should be encrypted
SENSITIVE_FIELDS = [
    "buyer_name",
    "buyer_phone", 
    "buyer_pan",
    "buyer_bank_account",
    "buyer_email",
    "total_value",
    "invoice_value",
    "bank_details",
    "account_number",
    "ifsc_code"
]


def encrypt_document(doc: dict, fields_to_encrypt: list = None) -> dict:
    """
    Encrypt sensitive fields in a document.
    
    Args:
        doc: Document dictionary
        fields_to_encrypt: List of field names to encrypt (defaults to SENSITIVE_FIELDS)
    
    Returns:
        Document with encrypted fields
    """
    if fields_to_encrypt is None:
        fields_to_encrypt = SENSITIVE_FIELDS
    
    encrypted_doc = doc.copy()
    for field in fields_to_encrypt:
        if field in encrypted_doc and encrypted_doc[field] is not None:
            # Don't re-encrypt already encrypted values
            if not encryption_service.is_encrypted(str(encrypted_doc[field])):
                encrypted_doc[field] = encrypt_field(encrypted_doc[field], field)
                encrypted_doc[f"{field}_encrypted"] = True
    
    return encrypted_doc


def decrypt_document(doc: dict, fields_to_decrypt: list = None) -> dict:
    """
    Decrypt sensitive fields in a document.
    
    Args:
        doc: Document dictionary with encrypted fields
        fields_to_decrypt: List of field names to decrypt (defaults to SENSITIVE_FIELDS)
    
    Returns:
        Document with decrypted fields
    """
    if fields_to_decrypt is None:
        fields_to_decrypt = SENSITIVE_FIELDS
    
    decrypted_doc = doc.copy()
    for field in fields_to_decrypt:
        if field in decrypted_doc and decrypted_doc[field] is not None:
            if encryption_service.is_encrypted(str(decrypted_doc[field])):
                decrypted_doc[field] = decrypt_field(decrypted_doc[field], field)
    
    return decrypted_doc
