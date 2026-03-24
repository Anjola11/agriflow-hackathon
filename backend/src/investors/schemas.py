from pydantic import BaseModel, Field
from typing import Optional

class VerifyBVNInput(BaseModel):
    bvn: str = Field(min_length=11, max_length=11, pattern=r'^\d{11}$')

class AddBankAccountInput(BaseModel):
    bank_code: str
    account_num: str = Field(min_length=10, max_length=10, pattern=r'^\d{10}$')
    
class VerifyBVNOut(BaseModel):
    bvn_verified: bool
    bvn_name: Optional[str] = None

class AddBankAccountOut(BaseModel):
    bank_verified: bool
    account_name: Optional[str] = None
    bank_name_match: bool

class VerifyBVNResponse(BaseModel):
    success: bool
    message: str
    data: VerifyBVNOut

class AddBankAccountResponse(BaseModel):
    success: bool
    message: str
    data: AddBankAccountOut
