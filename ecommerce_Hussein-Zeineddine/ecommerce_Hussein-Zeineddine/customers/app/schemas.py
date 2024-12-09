 
# customers/app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional

class CustomerBase(BaseModel):
    full_name: str
    username: str
    age: int
    address: str
    gender: str
    marital_status: str

class CustomerCreate(CustomerBase):
    password: str

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    wallet_balance: float

    class Config:
        orm_mode = True

class WalletOperation(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
