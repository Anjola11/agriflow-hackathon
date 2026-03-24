import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from src.db.main import engine

async def migrate_crops_to_jsonb():
    async with engine.begin() as conn:
        print("Migrating crop_references suitable_states to JSONB...")
        await conn.execute(text("ALTER TABLE crop_references ALTER COLUMN suitable_states TYPE JSONB USING suitable_states::jsonb;"))
        print("Migrating crop_references default_milestones to JSONB...")
        await conn.execute(text("ALTER TABLE crop_references ALTER COLUMN default_milestones TYPE JSONB USING default_milestones::jsonb;"))
        print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_crops_to_jsonb())
