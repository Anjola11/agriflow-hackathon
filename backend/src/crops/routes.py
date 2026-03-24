import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.crops.services import CropServices
from src.crops.schemas import CropReferenceOut, CropEstimateOut

crop_router = APIRouter()

def get_crop_services() -> CropServices:
    return CropServices()

@crop_router.get('', response_model=List[CropReferenceOut], status_code=status.HTTP_200_OK)
async def get_crops(
    session: AsyncSession = Depends(get_session),
    crop_services: CropServices = Depends(get_crop_services)
):
    return await crop_services.get_all_crops(session)

@crop_router.get('/{crop_id}/estimate', response_model=CropEstimateOut, status_code=status.HTTP_200_OK)
async def get_crop_estimate(
    crop_id: uuid.UUID,
    farm_size_ha: float,
    session: AsyncSession = Depends(get_session),
    crop_services: CropServices = Depends(get_crop_services)
):
    return await crop_services.get_crop_estimate(crop_id, farm_size_ha, session)
