 
# customers/app/models.py

from sqlalchemy import Column, Integer, String, Float
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
