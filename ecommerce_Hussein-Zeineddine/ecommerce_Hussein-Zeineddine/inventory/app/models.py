 # inventory/app/models.py

from sqlalchemy import Column, Integer, String, Float, CheckConstraint
from .database import Base

class InventoryItem(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    stock_count = Column(Integer, nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("category IN ('food', 'clothes', 'accessories', 'electronics')", name='check_category'),
        CheckConstraint("price >= 0", name='check_price_positive'),
        CheckConstraint("stock_count >= 0", name='check_stock_positive'),
    )

