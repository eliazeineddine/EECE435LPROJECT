 # inventory/app/schemas.py

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class InventoryBase(BaseModel):
    name: str
    category: str
    price: float
    description: Optional[str] = None
    stock_count: int

    @validator('category')
    def validate_category(cls, v):
        allowed_categories = {'food', 'clothes', 'accessories', 'electronics'}
        if v not in allowed_categories:
            raise ValueError(f"Category must be one of {allowed_categories}")
        return v

    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v

    @validator('stock_count')
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError("Stock count must be non-negative")
        return v

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    stock_count: Optional[int] = None

    @validator('category')
    def validate_category(cls, v):
        if v is None:
            return v
        allowed_categories = {'food', 'clothes', 'accessories', 'electronics'}
        if v not in allowed_categories:
            raise ValueError(f"Category must be one of {allowed_categories}")
        return v

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Price must be non-negative")
        return v

    @validator('stock_count')
    def validate_stock(cls, v):
        if v is not None and v < 0:
            raise ValueError("Stock count must be non-negative")
        return v

class InventoryResponse(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

