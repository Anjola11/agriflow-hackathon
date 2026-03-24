from sqlmodel.ext.asyncio.session import AsyncSession
from src.bank.models import Bank
from sqlmodel import select
from src.utils.logger import logger
from typing import List


class BankServices:
    async def get_all_banks(self, session: AsyncSession) -> List[Bank]:
        logger.info("Fetching all banks")
        try:
            statement = select(Bank).where(Bank.active == True)
            result = await session.exec(statement)
            banks = result.all()
            
            if not banks:
                logger.info("No active banks found")
                return []
            
            logger.info(f"Successfully retrieved {len(banks)} banks")
            return banks
        except Exception as e:
            logger.error(f"Error fetching banks: {str(e)}", exc_info=True)
            raise
