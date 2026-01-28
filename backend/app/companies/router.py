from fastapi import APIRouter, Depends
from ..core.dependencies import get_current_user
from .models import CompanyCreate, CompanyResponse
from .service import CompanyService

router = APIRouter(prefix="/company", tags=["Companies"])

@router.post("", response_model=CompanyResponse)
async def create_company(data: CompanyCreate, user: dict = Depends(get_current_user)):
    return await CompanyService.create(data, user)

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, user: dict = Depends(get_current_user)):
    return await CompanyService.get(company_id)

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: str, data: CompanyCreate, user: dict = Depends(get_current_user)):
    return await CompanyService.update(company_id, data)
