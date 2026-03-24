from src.interswitch.services import InterswitchMarketplaceServices
from src.farmers.schemas import VerifyBVNInput, AddBankAccountInput
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.models import User
import uuid
from sqlmodel import select
from fastapi import HTTPException, status
from src.utils.logger import logger
from sqlalchemy.exc import DatabaseError
from src.utils.bank import names_match
from src.auth.models import Role

interswitch_marketplace_services = InterswitchMarketplaceServices()

class FarmerServices:

    async def generate_credit_score(self, bvn: str):
        try:
            credit_history_request = await interswitch_marketplace_services.get_credit_history(bvn)
        except Exception as e:
            logger.warning(f"Credit history failed for BVN: {str(e)}")
            return 0
            
        if not credit_history_request.get("success") or str(credit_history_request.get("code")) != "200":
            return 0
        
        credit_data = credit_history_request.get("data", {})
        credit_history = credit_data.get("credit_history", [])

        score = 0
        all_entries = [
            entry
            for institution in credit_history
            for entry in institution.get("history", [])
        ]
        total_loans = len(all_entries)

        if total_loans == 0:
            score += 14
            return score

        #---loan perfomance - max 15 points---
        performing_loans = len([loan for loan in all_entries if loan.get("performance_status") == "performing"])
        non_performing_loans = total_loans - performing_loans

        if non_performing_loans == 0: #no non performing
            score += 20
        elif non_performing_loans / total_loans <= 0.25: #up to 25% non-performing
            score += 12
        elif non_performing_loans / total_loans <= 0.50: #up to 50% non-performing
            score += 6  
        else: # more than half non-performing
            score += 0 

        #---loan closure rate - max 20 points---
        closed_loans = len([e for e in all_entries if e.get("loan_status") == "closed"])
        open_loans = total_loans - closed_loans

        if open_loans >= 5: #signals potentially overextended
            score -= 3

        if total_loans == 0 and closed_loans == 0: #no loans means no closure history
            score += 0       
        else:
            closure_rate = closed_loans / total_loans
            if closure_rate == 1.0: #100% closure rate
                score += 20   
            elif closure_rate >= 0.75: #75-99% closed
                score += 16   
            elif closure_rate >= 0.50: #50-74% closed
                score += 11    
            elif closure_rate >= 0.25: #25-49% closed
                score += 6     
            else: #below 25% rate
                score += 3    

        #repayment consistency - max 15 points
        all_payments = [
            list(month.values())[0] if month else ""
            for entry in all_entries
            for month in entry.get("repayment_schedule", [])
        ]
        total_payments = len(all_payments)
        paid = sum(1 for p in all_payments if str(p).lower() == "paid")

        if total_payments == 0: # no repayment history, neutral
            score += 10   
        else:
            repayment_rate = paid / total_payments
            if repayment_rate == 1.0: #every single payment on time
                score += 15  
            elif repayment_rate >= 0.90: #90-99% paid
                score += 12   
            elif repayment_rate >= 0.75: #75-89% paid
                score += 8     
            elif repayment_rate >= 0.50: #50-74% paid
                score += 4    
            else: #less than 50% paid
                score += 0     

        return score


    async def verify_bvn(self,bvn: VerifyBVNInput, session: AsyncSession, user_id: uuid.UUID):
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

        trust_score = 20
        credit_score = await self.generate_credit_score(bvn.bvn)
        trust_score += credit_score

        user.bvn = bvn.bvn
        user.bvn_verified = True
        user.bvn_name = bvn_name
        user.trust_score = trust_score


        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return {
                "bvn_verified": user.bvn_verified,
                "bvn_name": user.bvn_name,
                "trust_score": user.trust_score,
                "trust_tier": user.trust_tier
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

        if user.role == Role.FARMER:
            user.trust_score += 10  # account verified
            if bvn_name_match or business_name_match:
                user.trust_score += 15  # name match
        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            return {
                "bank_verified": user.bank_verified,
                "account_name": user.account_name,
                "account_number": user.account_number,
                "bank_code": user.bank_code,
                "bank_name_match": bool(bvn_name_match or business_name_match),
                "trust_score": user.trust_score,
                "trust_tier": user.trust_tier
            }
        
        except DatabaseError as e:
            logger.error(f"Database error during bank account addition for user {user_id}: {str(e)}", exc_info=True)
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bank account addition failed"
            )



