 # sales/app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_sale(db: Session, sale_id: int):
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()

def get_sales(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sale).offset(skip).limit(limit).all()

def create_sale(db: Session, sale: schemas.SaleCreate):
    # Fetch customer by username
    customer = db.query(models.Customer).filter(models.Customer.username == sale.customer_username).first()
    if not customer:
        return None, "Customer not found"
    
    # Fetch inventory item by product_id
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == sale.product_id).first()
    if not item:
        return None, "Product not found"
    
    # Calculate total amount
    total_amount = item.price * sale.quantity
    
    # Check if customer has enough balance
    if customer.wallet_balance < total_amount:
        return None, "Insufficient funds"
    
    # Check if enough stock is available
    if item.stock_count < sale.quantity:
        return None, "Insufficient stock"
    
    # Deduct amount from customer's wallet
    customer.wallet_balance -= total_amount
    
    # Deduct stock from inventory
    item.stock_count -= sale.quantity
    
    # Create sale record
    db_sale = models.Sale(
        customer_id=customer.id,
        item_id=item.id,
        sale_date=datetime.utcnow().isoformat(),
        amount=total_amount
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale, None

