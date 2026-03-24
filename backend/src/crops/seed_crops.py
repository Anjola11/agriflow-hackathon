import asyncio
import sys
from pathlib import Path
from sqlmodel import select
from sqlalchemy.exc import DatabaseError

if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parents[2]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from src.db.main import async_session_maker, init_db
from src.crops.models import CropReference

SEED_DATA = [
    {
        "name": "Cassava",
        "unit": "tons",
        "growing_months_min": 9,
        "growing_months_max": 12,
        "cost_per_hectare_min": 150000,
        "cost_per_hectare_max": 250000,
        "yield_per_hectare_min": 8.0,
        "yield_per_hectare_max": 15.0,
        "market_price_min": 60000,
        "market_price_max": 90000,
        "max_return_rate": 0.20,
        "min_farm_size_ha": 0.5,
        "max_farm_size_ha": 10.0,
        "suitable_states": ["Oyo", "Osun", "Ondo", "Delta", "Rivers", "Benue", "Anambra"],
        "default_milestones": [
            { "name": "Land preparation & planting", "week": 1,  "percentage": 0.35 },
            { "name": "Fertiliser & weed control",   "week": 8,  "percentage": 0.30 },
            { "name": "Pest & disease management",   "week": 20, "percentage": 0.15 },
            { "name": "Harvest & processing",        "week": 40, "percentage": 0.20 }
        ]
    },
    {
        "name": "Maize",
        "unit": "tons",
        "growing_months_min": 3,
        "growing_months_max": 4,
        "cost_per_hectare_min": 120000,
        "cost_per_hectare_max": 200000,
        "yield_per_hectare_min": 2.0,
        "yield_per_hectare_max": 4.0,
        "market_price_min": 180000,
        "market_price_max": 260000,
        "max_return_rate": 0.22,
        "min_farm_size_ha": 0.5,
        "max_farm_size_ha": 10.0,
        "suitable_states": ["Kaduna", "Kano", "Plateau", "Benue", "Ogun", "Oyo", "Lagos"],
        "default_milestones": [
            { "name": "Land preparation & planting", "week": 1,  "percentage": 0.40 },
            { "name": "Fertiliser & weed control",   "week": 4,  "percentage": 0.30 },
            { "name": "Pest & disease management",   "week": 8,  "percentage": 0.15 },
            { "name": "Harvest & processing",        "week": 14, "percentage": 0.15 }
        ]
    },
    {
        "name": "Rice",
        "unit": "tons",
        "growing_months_min": 4,
        "growing_months_max": 6,
        "cost_per_hectare_min": 200000,
        "cost_per_hectare_max": 350000,
        "yield_per_hectare_min": 2.5,
        "yield_per_hectare_max": 5.0,
        "market_price_min": 300000,
        "market_price_max": 450000,
        "max_return_rate": 0.18,
        "min_farm_size_ha": 0.5,
        "max_farm_size_ha": 15.0,
        "suitable_states": ["Kebbi", "Niger", "Anambra", "Ebonyi", "Benue", "Taraba"],
        "default_milestones": [
            { "name": "Land preparation & planting", "week": 1,  "percentage": 0.35 },
            { "name": "Fertiliser & weed control",   "week": 5,  "percentage": 0.30 },
            { "name": "Pest & disease management",   "week": 12, "percentage": 0.15 },
            { "name": "Harvest & processing",        "week": 20, "percentage": 0.20 }
        ]
    },
    {
        "name": "Tomato",
        "unit": "tons",
        "growing_months_min": 3,
        "growing_months_max": 4,
        "cost_per_hectare_min": 300000,
        "cost_per_hectare_max": 500000,
        "yield_per_hectare_min": 8.0,
        "yield_per_hectare_max": 20.0,
        "market_price_min": 50000,
        "market_price_max": 150000,
        "max_return_rate": 0.25,
        "min_farm_size_ha": 0.25,
        "max_farm_size_ha": 5.0,
        "suitable_states": ["Kano", "Kaduna", "Plateau", "Benue", "Ogun", "Lagos"],
        "default_milestones": [
            { "name": "Land preparation & planting", "week": 1,  "percentage": 0.40 },
            { "name": "Fertiliser & irrigation",     "week": 3,  "percentage": 0.25 },
            { "name": "Pest & disease management",   "week": 7,  "percentage": 0.15 },
            { "name": "Harvest & processing",        "week": 14, "percentage": 0.20 }
        ]
    },
    {
        "name": "Yam",
        "unit": "tons",
        "growing_months_min": 6,
        "growing_months_max": 10,
        "cost_per_hectare_min": 250000,
        "cost_per_hectare_max": 400000,
        "yield_per_hectare_min": 4.0,
        "yield_per_hectare_max": 10.0,
        "market_price_min": 120000,
        "market_price_max": 200000,
        "max_return_rate": 0.20,
        "min_farm_size_ha": 0.5,
        "max_farm_size_ha": 8.0,
        "suitable_states": ["Benue", "Taraba", "Plateau", "Nassarawa", "Oyo", "Ekiti"],
        "default_milestones": [
            { "name": "Land preparation & planting", "week": 1,  "percentage": 0.40 },
            { "name": "Fertiliser & weed control",   "week": 6,  "percentage": 0.25 },
            { "name": "Pest & disease management",   "week": 16, "percentage": 0.15 },
            { "name": "Harvest & processing",        "week": 28, "percentage": 0.20 }
        ]
    },
    {
        "name": "Poultry",
        "unit": "birds",
        "growing_months_min": 2,
        "growing_months_max": 3,
        "cost_per_hectare_min": 180000,
        "cost_per_hectare_max": 300000,
        "yield_per_hectare_min": 500.0,
        "yield_per_hectare_max": 1000.0,
        "market_price_min": 2000,
        "market_price_max": 4000,
        "max_return_rate": 0.28,
        "min_farm_size_ha": 0.1,
        "max_farm_size_ha": 2.0,
        "suitable_states": [],
        "default_milestones": [
            { "name": "Setup & stocking",          "week": 1,  "percentage": 0.45 },
            { "name": "Feed & medication (mid)",   "week": 4,  "percentage": 0.30 },
            { "name": "Final feed & preparation",  "week": 7,  "percentage": 0.15 },
            { "name": "Harvest & sale",            "week": 10, "percentage": 0.10 }
        ]
    }
]

async def seed_crops():
    await init_db()
    async with async_session_maker() as session:
        statement = select(CropReference)
        result = await session.exec(statement)
        existing_crops = result.all()
        
        if len(existing_crops) > 0:
            print(f"Crops table already has {len(existing_crops)} records. Skipping seed.")
            return

        new_crops = [CropReference(**data) for data in SEED_DATA]
        
        try:
            session.add_all(new_crops)
            await session.commit()
            print("Done. 6 crops seeded.")
        except DatabaseError as e:
            await session.rollback()
            print(f"Error seeding crops: {str(e)}")

if __name__ == "__main__":
    asyncio.run(seed_crops())
