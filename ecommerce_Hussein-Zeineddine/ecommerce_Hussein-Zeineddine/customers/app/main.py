 
# customers/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine
from .dependencies import get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customers Service")

@app.post("/customers/register", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def register_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_username(db, username=customer.username)
    if db_customer:
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_customer(db=db, customer=customer)

@app.delete("/customers/{username}", response_model=schemas.CustomerResponse)
def delete_customer(username: str, db: Session = Depends(get_db)):
    db_customer = crud.delete_customer(db, username=username)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.put("/customers/{username}", response_model=schemas.CustomerResponse)
def update_customer(username: str, updates: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = crud.update_customer(db, username=username, updates=updates)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.get("/customers", response_model=list[schemas.CustomerResponse])
def get_all_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return customers

@app.get("/customers/{username}", response_model=schemas.CustomerResponse)
def get_customer(username: str, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_username(db, username=username)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.post("/customers/{username}/charge", response_model=schemas.CustomerResponse)
def charge_wallet(username: str, wallet_op: schemas.WalletOperation, db: Session = Depends(get_db)):
    db_customer = crud.charge_wallet(db, username=username, amount=wallet_op.amount)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.post("/customers/{username}/deduct", response_model=schemas.CustomerResponse)
def deduct_wallet(username: str, wallet_op: schemas.WalletOperation, db: Session = Depends(get_db)):
    db_customer = crud.deduct_wallet(db, username=username, amount=wallet_op.amount)
    if not db_customer:
        raise HTTPException(status_code=400, detail="Insufficient funds or customer not found")
    return db_customer
