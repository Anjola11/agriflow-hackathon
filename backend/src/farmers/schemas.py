from pydantic import BaseModel, Field

class VerifyBVNInput(BaseModel):
    bvn: str = Field(min_length=11, max_length=11, pattern=r'^\d{11}$',)

class AddBankAccountInput(BaseModel):
    bank_code: str
    account_num: str = Field(min_length=10, max_length=10, pattern=r'^\d{10}$')