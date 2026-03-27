from src.config import Config
from sqlalchemy.ext.asyncio import create_async_engine 
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=1800,
)

async def init_db():
    async with engine.begin() as conn:

        #import models here
        from src.auth.models import User, Admin
        from src.bank.models import Bank
        from src.crops.models import CropReference
        from src.farms.models import Farm
        from src.milestones.models import Milestone
        from src.harvest.models import HarvestReport
        from src.payouts.models import Payout

        await conn.run_sync(SQLModel.metadata.create_all)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    async with async_session_maker() as session:
        
        yield session
