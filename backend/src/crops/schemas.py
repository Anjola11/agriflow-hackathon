import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class CropReferenceOut(BaseModel):
    id: uuid.UUID
    name: str
    local_name: Optional[str] = None
    unit: str
    growing_months_min: int
    growing_months_max: int
    cost_per_hectare_min: int
    cost_per_hectare_max: int
    yield_per_hectare_min: float
    yield_per_hectare_max: float
    market_price_min: int
    market_price_max: int
    max_return_rate: float
    suitable_states: list
    default_milestones: list

class CropEstimateOut(BaseModel):
    crop_name: str
    farm_size_ha: float
    budget_min: int
    budget_max: int
    yield_min: float
    yield_max: float
    revenue_min: int
    revenue_max: int
    growing_months_min: int
    growing_months_max: int
    max_return_rate: float
    default_milestones: List[Dict[str, Any]]
    suitable_states: List[str]
