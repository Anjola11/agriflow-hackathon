import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg

def utc_now():
    return datetime.now(timezone.utc)

class CropReference(SQLModel, table=True):
    __tablename__ = "crop_references"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    local_name: Optional[str] = Field(default=None)
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
    
    # Deviation defaults
    max_budget_deviation: float = Field(default=0.20)
    max_yield_deviation: float = Field(default=0.30)
    
    min_farm_size_ha: float
    max_farm_size_ha: float
    
    suitable_states: list = Field(default=[], sa_column=Column(pg.JSONB))  
    default_milestones: list = Field(default=[], sa_column=Column(pg.JSONB)) 
    
    is_active: bool = Field(default=True)
    
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )
