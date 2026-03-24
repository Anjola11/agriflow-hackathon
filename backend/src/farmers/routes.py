from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.farmers.services import FarmerServices
from src.farmers.schemas import VerifyBVNInput, AddBankAccountInput
from src.utils.dependencies import get_current_farmer
from src.utils.logger import logger

farmer_router = APIRouter()

def get_farmer_services() -> FarmerServices:
    return FarmerServices()

@farmer_router.post('/verify-bvn', status_code=status.HTTP_200_OK)
async def verify_bvn(
    bvn_input: VerifyBVNInput,
    current_farmer = Depends(get_current_farmer),
    session: AsyncSession = Depends(get_session),
    farmer_services: FarmerServices = Depends(get_farmer_services)
):
    logger.info(f"Initiating BVN verification for farmer {current_farmer.uid}")
    bvn_data = await farmer_services.verify_bvn(bvn_input, session, current_farmer.uid)
    logger.info(f"Successfully verified BVN for farmer {current_farmer.uid}.")
    
    return {
        "success": True,
        "message": "BVN verified successfully",
        "data": bvn_data
    }

@farmer_router.post('/bank-account', status_code=status.HTTP_200_OK)
async def add_bank_account(
    bank_account_input: AddBankAccountInput,
    current_farmer = Depends(get_current_farmer),
    session: AsyncSession = Depends(get_session),
    farmer_services: FarmerServices = Depends(get_farmer_services)
):
    logger.info(f"Initiating bank account addition for farmer {current_farmer.uid}")
    account_data = await farmer_services.add_account(bank_account_input, session, current_farmer.uid)
    logger.info(f"Successfully added bank account for farmer {current_farmer.uid}. Match: {account_data.get('bank_name_match')}")

    return {
        "success": True,
        "message": "Bank account added successfully",
        "data": account_data
    }