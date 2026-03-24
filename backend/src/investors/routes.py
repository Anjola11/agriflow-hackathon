from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.utils.dependencies import get_current_investor
from src.utils.logger import logger

from src.investors.services import InvestorServices
from src.investors.schemas import VerifyBVNInput, AddBankAccountInput

investor_router = APIRouter()

def get_investor_services() -> InvestorServices:
    return InvestorServices()

@investor_router.post('/verify-bvn', status_code=status.HTTP_200_OK)
async def verify_bvn(
    bvn_input: VerifyBVNInput,
    current_investor = Depends(get_current_investor),
    session: AsyncSession = Depends(get_session),
    investor_services: InvestorServices = Depends(get_investor_services)
):
    logger.info(f"Initiating BVN verification for investor {current_investor.uid}")
    bvn_data = await investor_services.verify_bvn(bvn_input, session, current_investor.uid)
    logger.info(f"Successfully verified BVN for investor {current_investor.uid}.")
    
    return {
        "success": True,
        "message": "BVN verified successfully",
        "data": bvn_data
    }

@investor_router.post('/bank-account', status_code=status.HTTP_200_OK)
async def add_bank_account(
    bank_account_input: AddBankAccountInput,
    current_investor = Depends(get_current_investor),
    session: AsyncSession = Depends(get_session),
    investor_services: InvestorServices = Depends(get_investor_services)
):
    logger.info(f"Initiating bank account addition for investor {current_investor.uid}")
    account_data = await investor_services.add_account(bank_account_input, session, current_investor.uid)
    logger.info(f"Successfully added bank account for investor {current_investor.uid}. Match: {account_data.get('bank_name_match')}")

    return {
        "success": True,
        "message": "Bank account added successfully",
        "data": account_data
    }
