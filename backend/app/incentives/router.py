from fastapi import APIRouter, Depends, Query
from typing import List
from ..core.dependencies import get_current_user
from .models import IncentiveCalculateRequest
from .service import IncentiveService
from .hs_database import search_hs_codes

router = APIRouter(prefix="/incentives", tags=["Incentives"])

@router.get("/rodtep-eligibility")
async def check_rodtep_eligibility(hs_code: str = Query(...)):
    """Check RoDTEP/RoSCTL eligibility for an HS code"""
    eligibility = await IncentiveService.check_eligibility(hs_code)
    return {
        "hs_code": eligibility["hs_code"],
        "eligible": eligibility["eligible"]["rodtep"],
        "chapter": eligibility["chapter"],
        "description": eligibility["description"],
        "rate_percent": eligibility["rates"]["rodtep"],
        "scheme": "RoDTEP",
        "notes": eligibility["notes"],
        "all_rates": eligibility["rates"]
    }

@router.post("/calculate")
async def calculate_incentive(data: IncentiveCalculateRequest, user: dict = Depends(get_current_user)):
    """Calculate incentives for a shipment"""
    result = await IncentiveService.calculate(data, user)
    return {
        "id": result["id"],
        "shipment_id": result["shipment_id"],
        "hs_code": result["hs_code"],
        "fob_value": result["fob_value"],
        "rate_percent": result["total_rate"],
        "incentive_amount": result["total_incentive"],
        "incentives_breakdown": result["incentives"],
        "status": result["status"]
    }

@router.get("/lost-money")
async def get_lost_incentives(user: dict = Depends(get_current_user)):
    """Get potential lost incentives from unclaimed shipments"""
    lost = await IncentiveService.get_lost_money(user)
    return {
        "potential_incentive_loss": lost["total_potential_loss"],
        "unclaimed_shipments": lost["unclaimed_shipments_count"],
        "shipments": lost["unclaimed_shipments"],
        "recommendation": lost["recommendation"],
        "priority": lost["priority_action"]
    }

@router.get("/summary")
async def get_incentives_summary(user: dict = Depends(get_current_user)):
    """Get incentives summary with breakdown by scheme"""
    return await IncentiveService.get_summary(user)

@router.get("/leakage-dashboard")
async def get_leakage_dashboard(user: dict = Depends(get_current_user)):
    """Get comprehensive 'Money Left on Table' dashboard data"""
    return await IncentiveService.get_leakage_dashboard(user)

@router.get("/shipment-analysis")
async def get_shipment_analysis(user: dict = Depends(get_current_user)):
    """Get detailed shipment-by-shipment incentive analysis"""
    return await IncentiveService.get_shipment_analysis(user)

@router.get("/hs-codes/search")
async def search_hs_codes_endpoint(q: str = Query(..., min_length=2), limit: int = 20):
    """Search HS codes by description or code"""
    return await IncentiveService.search_hs_codes(q, limit)
