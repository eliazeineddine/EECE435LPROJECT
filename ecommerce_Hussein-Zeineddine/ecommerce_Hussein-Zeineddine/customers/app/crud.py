 
# customers/app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_customer(db: Session, customer: schemas.CustomerCreate):
    hashed_password = get_password_hash(customer.password)
    db_customer = models.Customer(
        full_name=customer.full_name,
        username=customer.username,
        hashed_password=hashed_password,
        age=customer.age,
        address=customer.address,
        gender=customer.gender,
        marital_status=customer.marital_status,
        wallet_balance=0.0
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def get_customer_by_username(db: Session, username: str):
    return db.query(models.Customer).filter(models.Customer.username == username).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def delete_customer(db: Session, username: str):
    customer = get_customer_by_username(db, username)
    if customer:
        db.delete(customer)
        db.commit()
    return customer

def update_customer(db: Session, username: str, updates: schemas.CustomerUpdate):
    customer = get_customer_by_username(db, username)
    if not customer:
        return None
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer

def charge_wallet(db: Session, username: str, amount: float):
    customer = get_customer_by_username(db, username)
    if customer:
        customer.wallet_balance += amount
        db.commit()
        db.refresh(customer)
    return customer

def deduct_wallet(db: Session, username: str, amount: float):
    customer = get_customer_by_username(db, username)
    if customer and customer.wallet_balance >= amount:
        customer.wallet_balance -= amount
        db.commit()
        db.refresh(customer)
        return customer
    return None
