from sqlmodel.ext.asyncio.session import AsyncSession
from src.bank.models import Bank
from sqlmodel import select
from src.utils.logger import logger
from typing import List
from datetime import datetime, timedelta


_banks_cache: list[Bank] = []
_banks_cache_expires_at: datetime | None = None
_BANKS_CACHE_TTL_SECONDS = 300


class BankServices:
    async def get_all_banks(self, session: AsyncSession) -> List[Bank]:
        logger.info("Fetching all banks")

        global _banks_cache, _banks_cache_expires_at
        now = datetime.utcnow()

        if _banks_cache_expires_at and now < _banks_cache_expires_at and _banks_cache:
            return _banks_cache

        try:
            statement = select(Bank).where(Bank.active == True)
            result = await session.exec(statement)
            banks = result.all()
            
            if not banks:
                logger.info("No active banks found")
                return []

            _banks_cache = banks
            _banks_cache_expires_at = now + timedelta(seconds=_BANKS_CACHE_TTL_SECONDS)
            
            logger.info(f"Successfully retrieved {len(banks)} banks")
            return banks
        except Exception as e:
            logger.error(f"Error fetching banks: {str(e)}", exc_info=True)
            raise
