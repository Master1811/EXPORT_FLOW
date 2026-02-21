"""
OFAC Sanctions Screening Service
Required for export compliance - screens buyers and companies against OFAC SDN list.
"""

import os
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging
import aiohttp

from ..core.database import db
from ..common.utils import generate_id, now_iso

logger = logging.getLogger(__name__)


# OFAC SDN List URL (free tier - daily updates)
OFAC_SDN_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"

# High-risk countries for additional screening
HIGH_RISK_COUNTRIES = {
    "IR": "Iran",
    "KP": "North Korea",
    "SY": "Syria",
    "CU": "Cuba",
    "VE": "Venezuela",
    "RU": "Russia",
    "BY": "Belarus"
}


class OFACScreeningResult:
    """Result of OFAC screening"""
    def __init__(
        self,
        is_clear: bool,
        risk_score: int,
        matches: List[Dict[str, Any]],
        screening_id: str,
        message: str
    ):
        self.is_clear = is_clear
        self.risk_score = risk_score
        self.matches = matches
        self.screening_id = screening_id
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_clear": self.is_clear,
            "risk_score": self.risk_score,
            "matches": self.matches,
            "screening_id": self.screening_id,
            "message": self.message,
            "timestamp": now_iso()
        }


class OFACScreeningService:
    """
    OFAC Sanctions Screening for Export Compliance.
    
    Features:
    - Name matching against SDN list
    - Country-based risk assessment
    - Fuzzy matching for name variations
    - Audit trail for all screenings
    """
    
    # In-memory cache of SDN entries (refreshed daily)
    _sdn_cache: List[Dict[str, Any]] = []
    _cache_timestamp: Optional[datetime] = None
    _cache_ttl_hours = 24
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        # Remove special characters, lowercase
        normalized = re.sub(r'[^a-z0-9\s]', '', name.lower())
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        return normalized
    
    @staticmethod
    def calculate_similarity(name1: str, name2: str) -> float:
        """Calculate name similarity using Jaccard coefficient"""
        if not name1 or not name2:
            return 0.0
        
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @classmethod
    async def refresh_sdn_list(cls) -> bool:
        """
        Refresh SDN list from OFAC website.
        In production, use a paid API for real-time updates.
        """
        try:
            # Check if cache is still valid
            if cls._cache_timestamp:
                age_hours = (datetime.now(timezone.utc) - cls._cache_timestamp).total_seconds() / 3600
                if age_hours < cls._cache_ttl_hours and cls._sdn_cache:
                    return True
            
            # For demo/development, use a simplified in-memory list
            # In production, integrate with Treasury API or compliance vendor
            cls._sdn_cache = await cls._load_cached_sdn()
            cls._cache_timestamp = datetime.now(timezone.utc)
            
            logger.info(f"OFAC SDN list refreshed: {len(cls._sdn_cache)} entries")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh SDN list: {e}")
            return False
    
    @classmethod
    async def _load_cached_sdn(cls) -> List[Dict[str, Any]]:
        """Load SDN entries from database cache or initialize"""
        # Check database cache first
        cached = await db.ofac_sdn_cache.find({}, {"_id": 0}).to_list(50000)
        
        if cached:
            return cached
        
        # Initialize with sample high-profile entries for demo
        # In production, this would be populated from official OFAC data
        sample_entries = [
            {"name": "sample blocked entity", "type": "ENTITY", "program": "SDGT", "country": "IR"},
            {"name": "sample blocked individual", "type": "INDIVIDUAL", "program": "SDGT", "country": "SY"},
        ]
        
        for entry in sample_entries:
            entry["id"] = generate_id()
            entry["normalized_name"] = cls.normalize_name(entry["name"])
        
        if sample_entries:
            await db.ofac_sdn_cache.insert_many(sample_entries)
        
        return sample_entries
    
    @classmethod
    async def screen_entity(
        cls,
        entity_name: str,
        entity_type: str,  # "buyer", "company", "individual"
        country_code: Optional[str],
        company_id: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> OFACScreeningResult:
        """
        Screen an entity against OFAC sanctions list.
        
        Args:
            entity_name: Name to screen
            entity_type: Type of entity being screened
            country_code: ISO country code (optional)
            company_id: Company performing the screening
            additional_info: Additional entity details
            
        Returns:
            OFACScreeningResult with screening outcome
        """
        screening_id = generate_id()
        
        # Refresh SDN list if needed
        await cls.refresh_sdn_list()
        
        normalized_name = cls.normalize_name(entity_name)
        matches = []
        risk_score = 0
        
        # Check country risk
        if country_code and country_code.upper() in HIGH_RISK_COUNTRIES:
            risk_score += 30
            matches.append({
                "type": "HIGH_RISK_COUNTRY",
                "match": HIGH_RISK_COUNTRIES[country_code.upper()],
                "confidence": 100,
                "message": f"Entity is in high-risk country: {HIGH_RISK_COUNTRIES[country_code.upper()]}"
            })
        
        # Screen against SDN list
        for sdn_entry in cls._sdn_cache:
            sdn_normalized = sdn_entry.get("normalized_name", cls.normalize_name(sdn_entry.get("name", "")))
            
            # Exact match
            if normalized_name == sdn_normalized:
                risk_score += 100
                matches.append({
                    "type": "EXACT_MATCH",
                    "sdn_name": sdn_entry.get("name"),
                    "program": sdn_entry.get("program"),
                    "confidence": 100,
                    "message": "Exact name match found on SDN list"
                })
                continue
            
            # Fuzzy match
            similarity = cls.calculate_similarity(normalized_name, sdn_normalized)
            if similarity >= 0.8:
                risk_score += int(similarity * 80)
                matches.append({
                    "type": "SIMILAR_MATCH",
                    "sdn_name": sdn_entry.get("name"),
                    "program": sdn_entry.get("program"),
                    "confidence": int(similarity * 100),
                    "message": f"Similar name match ({int(similarity * 100)}% confidence)"
                })
        
        # Determine screening outcome
        is_clear = risk_score < 50
        
        if risk_score >= 100:
            message = "BLOCKED: Entity appears on OFAC sanctions list. Transaction prohibited."
        elif risk_score >= 50:
            message = "WARNING: Potential match requires manual review before proceeding."
        elif risk_score >= 30:
            message = "CAUTION: High-risk country. Enhanced due diligence recommended."
        else:
            message = "CLEAR: No sanctions matches found."
        
        # Store screening record for audit
        screening_record = {
            "id": screening_id,
            "company_id": company_id,
            "entity_name": entity_name,
            "entity_type": entity_type,
            "country_code": country_code,
            "normalized_name": normalized_name,
            "risk_score": risk_score,
            "is_clear": is_clear,
            "matches": matches,
            "message": message,
            "additional_info": additional_info,
            "created_at": now_iso()
        }
        await db.ofac_screenings.insert_one(screening_record)
        
        # Log for audit trail
        await db.audit_logs.insert_one({
            "id": generate_id(),
            "action_type": "ofac_screening",
            "resource_type": "screening",
            "resource_id": screening_id,
            "company_id": company_id,
            "details": {
                "entity_name": entity_name,
                "entity_type": entity_type,
                "risk_score": risk_score,
                "is_clear": is_clear,
                "match_count": len(matches)
            },
            "timestamp": now_iso()
        })
        
        return OFACScreeningResult(
            is_clear=is_clear,
            risk_score=min(risk_score, 100),
            matches=matches,
            screening_id=screening_id,
            message=message
        )
    
    @classmethod
    async def get_screening_history(
        cls,
        company_id: str,
        entity_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get screening history for audit purposes"""
        query = {"company_id": company_id}
        if entity_name:
            query["entity_name"] = {"$regex": entity_name, "$options": "i"}
        
        return await db.ofac_screenings.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
    
    @classmethod
    async def screen_buyer_for_shipment(
        cls,
        shipment_id: str,
        buyer_name: str,
        buyer_country: str,
        company_id: str
    ) -> OFACScreeningResult:
        """
        Screen buyer before shipment creation/approval.
        This should be called during shipment workflow.
        """
        result = await cls.screen_entity(
            entity_name=buyer_name,
            entity_type="buyer",
            country_code=buyer_country,
            company_id=company_id,
            additional_info={"shipment_id": shipment_id}
        )
        
        # Link screening to shipment
        if not result.is_clear:
            await db.shipments.update_one(
                {"id": shipment_id, "company_id": company_id},
                {
                    "$set": {
                        "ofac_screening_id": result.screening_id,
                        "ofac_risk_score": result.risk_score,
                        "ofac_status": "flagged" if result.risk_score >= 50 else "caution",
                        "updated_at": now_iso()
                    }
                }
            )
        else:
            await db.shipments.update_one(
                {"id": shipment_id, "company_id": company_id},
                {
                    "$set": {
                        "ofac_screening_id": result.screening_id,
                        "ofac_risk_score": result.risk_score,
                        "ofac_status": "clear",
                        "updated_at": now_iso()
                    }
                }
            )
        
        return result
