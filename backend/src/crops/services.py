import uuid
from sqlmodel import select
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crops.models import CropReference
from src.crops.schemas import CropEstimateOut

class CropServices:
    async def get_all_crops(self, session: AsyncSession):
        statement = select(CropReference).where(CropReference.is_active == True)
        result = await session.exec(statement)
        return result.all()

    async def get_crop_estimate(self, crop_id: uuid.UUID, farm_size_ha: float, session: AsyncSession) -> CropEstimateOut:
        if farm_size_ha <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="farm size must be greater than 0"
            )

        crop = await session.get(CropReference, crop_id)
        if not crop or not crop.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Crop not found"
            )

        budget_min = int(crop.cost_per_hectare_min * farm_size_ha)
        budget_max = int(crop.cost_per_hectare_max * farm_size_ha * (1.0 + crop.max_budget_deviation))
        
        yield_min = crop.yield_per_hectare_min * farm_size_ha
        yield_max = crop.yield_per_hectare_max * farm_size_ha * (1.0 + crop.max_yield_deviation)

        revenue_min = int(yield_min * crop.market_price_min)
        revenue_max = int(yield_max * crop.market_price_max)

        return CropEstimateOut(
            crop_name=crop.name,
            farm_size_ha=farm_size_ha,
            budget_min=budget_min,
            budget_max=budget_max,
            yield_min=yield_min,
            yield_max=yield_max,
            revenue_min=revenue_min,
            revenue_max=revenue_max,
            growing_months_min=crop.growing_months_min,
            growing_months_max=crop.growing_months_max,
            max_return_rate=crop.max_return_rate,
            default_milestones=crop.default_milestones or [],
            suitable_states=crop.suitable_states or []
        )
