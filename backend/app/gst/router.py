from fastapi import APIRouter, Depends, Query
from typing import List, Dict
from ..core.dependencies import get_current_user
from .models import GSTInputCreditCreate, GSTSummaryResponse
from .service import GSTService

router = APIRouter(tags=["GST & Compliance"])

@router.post("/gst/input-credit")
async def add_gst_input_credit(data: GSTInputCreditCreate, user: dict = Depends(get_current_user)):
    return await GSTService.add_input_credit(data, user)

@router.get("/gst/summary/monthly", response_model=List[GSTSummaryResponse])
async def get_gst_monthly_summary(year: int = None, user: dict = Depends(get_current_user)):
    return await GSTService.get_monthly_summary(user, year)

@router.get("/gst/refund/expected")
async def get_expected_refund(user: dict = Depends(get_current_user)):
    return await GSTService.get_expected_refund(user)

@router.get("/gst/refund/status")
async def get_refund_status(user: dict = Depends(get_current_user)):
    return await GSTService.get_refund_status(user)

@router.get("/compliance/lut-status")
async def get_lut_status(user: dict = Depends(get_current_user)):
    return await GSTService.get_lut_status(user)

@router.post("/compliance/lut-link")
async def link_lut(data: Dict[str, str], user: dict = Depends(get_current_user)):
    return await GSTService.link_lut(data, user)
