import uuid
from sqlmodel import select
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.models import User
from src.interswitch.services import InterswitchMarketplaceServices
from src.investors.schemas import VerifyBVNInput, AddBankAccountInput
from src.utils.bank import names_match
from src.utils.logger import logger
from sqlalchemy.exc import DatabaseError

interswitch_marketplace_services = InterswitchMarketplaceServices()

class InvestorServices:

    async def verify_bvn(self, bvn: VerifyBVNInput, session: AsyncSession, user_id: uuid.UUID):
        statement = select(User).where(User.uid == user_id)
        result = await session.exec(statement)
        user = result.first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )

        if user.bvn_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="BVN already verified"
            )

        bvn_details = await interswitch_marketplace_services.get_bvn(bvn.bvn)
        
        if not bvn_details.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid BVN. Please check and try again."
            )

        bvn_name = bvn_details.get("bvn_name", "")

        user.bvn = bvn.bvn
        user.bvn_verified = True
        user.bvn_name = bvn_name

        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return {
                "bvn_verified": user.bvn_verified,
                "bvn_name": user.bvn_name,
            }
        
        except DatabaseError as e:
            logger.error(f"Database error during BVN verification for user {user_id}: {str(e)}", exc_info=True)
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="account verification failed"
            )

    async def add_account(self, bank_account_input: AddBankAccountInput, session: AsyncSession, user_id: uuid.UUID):
        account = await interswitch_marketplace_services.user_account_lookup(bank_account_input.account_num, bank_account_input.bank_code)

        if not account.get("success") or str(account.get("code")) != "200":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="unable to fetch account details"
            )
        
        data = account.get("data", {})
        account_bank_details = data.get("bankDetails", {})

        statement = select(User).where(User.uid == user_id)
        result = await session.exec(statement)
        user = result.first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )

        if not account_bank_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        account_name = account_bank_details.get("accountName")
        bank_code = bank_account_input.bank_code
        account_num = bank_account_input.account_num

        bvn_name_match = False
        if user.bvn_name:
            bvn_name_match = names_match(user.bvn_name, account_name)

        business_name_match = False
        if user.business_name:
            business_name_match = names_match(user.business_name, account_name)

        user.account_name = account_name
        user.account_number = account_num
        user.bank_code = bank_code
        user.bank_verified = True

        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            return {
                "bank_verified": user.bank_verified,
                "account_name": user.account_name,
                "bank_name_match": bool(bvn_name_match or business_name_match),
            }
        
        except DatabaseError as e:
            logger.error(f"Database error during bank account addition for user {user_id}: {str(e)}", exc_info=True)
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bank account addition failed"
            )
