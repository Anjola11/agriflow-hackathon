from pydantic import BaseModel
import uuid
from typing import List

class BankOut(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    active: bool


class BankListResponse(BaseModel):
    success: bool
    message: str
    data: List[BankOut]
