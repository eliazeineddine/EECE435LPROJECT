 # sales/app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional

class SaleBase(BaseModel):
    product_id: int
    customer_username: str
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")

class SaleCreate(SaleBase):
    pass

class SaleResponse(BaseModel):
    id: int
    customer_id: int
    item_id: int
    sale_date: str
    amount: float

    class Config:
        orm_mode = True

