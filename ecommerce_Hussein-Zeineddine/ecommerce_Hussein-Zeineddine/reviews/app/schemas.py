 # reviews/app/schemas.py

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    customer_id: int

    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v

class ReviewModeration(BaseModel):
    action: str

    @validator('action')
    def validate_action(cls, v):
        if v not in {"flag", "approve"}:
            raise ValueError("Action must be 'flag' or 'approve'")
        return v

class ReviewResponse(ReviewBase):
    id: int
    customer_id: int
    is_flagged: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

