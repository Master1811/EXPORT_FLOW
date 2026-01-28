from fastapi import APIRouter, Depends
from typing import Dict
from ..core.dependencies import get_current_user
from .service import ConnectorService

router = APIRouter(tags=["Connectors"])

@router.post("/connect/bank/initiate")
async def initiate_bank_connection(data: Dict, user: dict = Depends(get_current_user)):
    return await ConnectorService.initiate_bank(data, user)

@router.post("/connect/bank/consent")
async def bank_consent(data: Dict, user: dict = Depends(get_current_user)):
    return await ConnectorService.bank_consent(data, user)

@router.get("/sync/bank")
async def sync_bank_data(user: dict = Depends(get_current_user)):
    return await ConnectorService.sync_bank(user)

@router.post("/connect/gst/link")
async def link_gst(data: Dict, user: dict = Depends(get_current_user)):
    return await ConnectorService.link_gst(data, user)

@router.get("/sync/gst")
async def sync_gst_data(user: dict = Depends(get_current_user)):
    return await ConnectorService.sync_gst(user)

@router.post("/connect/customs/link")
async def link_customs(data: Dict, user: dict = Depends(get_current_user)):
    return await ConnectorService.link_customs(data, user)

@router.get("/sync/customs")
async def sync_customs_data(user: dict = Depends(get_current_user)):
    return await ConnectorService.sync_customs(user)
