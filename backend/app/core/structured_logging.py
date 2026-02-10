"""
Structured Logging with PII Masking
Production-grade logging that automatically masks sensitive data
"""
import re
import logging
import structlog
from typing import Any, Dict, List
from functools import lru_cache
import os

# PII patterns to mask
PII_PATTERNS = {
    # Bank account numbers (various formats)
    "bank_account": re.compile(r'\b\d{9,18}\b'),
    # Phone numbers (Indian and international)
    "phone": re.compile(r'\b(?:\+?91[-\s]?)?[6-9]\d{9}\b|\b\+?[1-9]\d{10,14}\b'),
    # PAN numbers (Indian)
    "pan": re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', re.IGNORECASE),
    # Email addresses
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    # Aadhaar numbers (Indian)
    "aadhaar": re.compile(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b'),
    # Credit card numbers
    "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    # GSTIN (Indian)
    "gstin": re.compile(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z][Z][0-9A-Z]\b', re.IGNORECASE),
    # IEC Code (Indian)
    "iec": re.compile(r'\b[A-Z0-9]{10}\b'),
}

# Fields that should always be masked
SENSITIVE_FIELD_NAMES = {
    "password", "secret", "token", "api_key", "apikey", "access_token",
    "refresh_token", "authorization", "auth", "credential", "private_key",
    "bank_account", "account_number", "buyer_bank_account", "pan", "buyer_pan",
    "phone", "buyer_phone", "mobile", "aadhaar", "ssn", "credit_card",
    "card_number", "cvv", "pin", "otp"
}


def mask_value(value: str, visible_chars: int = 4) -> str:
    """Mask a value showing only last few characters"""
    if not value or len(str(value)) <= visible_chars:
        return "****"
    value_str = str(value)
    return "*" * (len(value_str) - visible_chars) + value_str[-visible_chars:]


def mask_pii_in_string(text: str) -> str:
    """Mask all PII patterns found in a string"""
    if not isinstance(text, str):
        return text
    
    masked = text
    for pattern_name, pattern in PII_PATTERNS.items():
        masked = pattern.sub(lambda m: mask_value(m.group(), 4), masked)
    
    return masked


def mask_dict_pii(data: Dict[str, Any], depth: int = 0, max_depth: int = 10) -> Dict[str, Any]:
    """Recursively mask PII in a dictionary"""
    if depth >= max_depth:
        return data
    
    masked = {}
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if field name is sensitive
        if any(sensitive in key_lower for sensitive in SENSITIVE_FIELD_NAMES):
            if isinstance(value, str):
                masked[key] = mask_value(value)
            elif value is not None:
                masked[key] = "****"
            else:
                masked[key] = None
        elif isinstance(value, dict):
            masked[key] = mask_dict_pii(value, depth + 1, max_depth)
        elif isinstance(value, list):
            masked[key] = [
                mask_dict_pii(item, depth + 1, max_depth) if isinstance(item, dict)
                else mask_pii_in_string(item) if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, str):
            masked[key] = mask_pii_in_string(value)
        else:
            masked[key] = value
    
    return masked


class PIIMaskingProcessor:
    """Structlog processor that masks PII in log events"""
    
    def __call__(self, logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Process log event and mask PII"""
        return mask_dict_pii(event_dict)


class ProductionRenderer:
    """Custom renderer for production logs"""
    
    def __call__(self, logger: Any, method_name: str, event_dict: Dict[str, Any]) -> str:
        """Render log event as JSON-like string for production"""
        # Remove internal structlog keys for cleaner output
        event = event_dict.pop("event", "")
        timestamp = event_dict.pop("timestamp", "")
        level = event_dict.pop("level", method_name.upper())
        
        # Build log line
        parts = [f"[{timestamp}]", f"[{level}]", event]
        
        # Add remaining context
        if event_dict:
            context = " ".join(f"{k}={v}" for k, v in event_dict.items() if v is not None)
            if context:
                parts.append(f"| {context}")
        
        return " ".join(parts)


def configure_logging(production: bool = None):
    """
    Configure structured logging with PII masking
    
    Args:
        production: If True, use production settings. If None, detect from environment.
    """
    if production is None:
        production = os.environ.get("ENVIRONMENT", "production").lower() == "production"
    
    # Shared processors
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        PIIMaskingProcessor(),  # Always mask PII
    ]
    
    if production:
        # Production: JSON format, no colors
        structlog.configure(
            processors=shared_processors + [
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Development: Colorful, human-readable
        structlog.configure(
            processors=shared_processors + [
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    # Configure standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )


@lru_cache(maxsize=128)
def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name or __name__)


# Initialize logging on import
configure_logging()

# Export commonly used logger
logger = get_logger("app")
