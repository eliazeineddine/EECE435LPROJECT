from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    marital_status = Column(String, nullable=False)
    wallet_balance = Column(Float, default=0.0)

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    # Same as above: define the minimal set of fields you require.
    # For Sales, you might need 'price' and 'stock_count' at least.
    price = Column(Float, nullable=False)
    stock_count = Column(Integer, nullable=False)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    sale_date = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    customer = relationship("Customer")
    item = relationship("InventoryItem")
