 # inventory/app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_inventory_item(db: Session, item_id: int):
    return db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()

def get_inventory_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.InventoryItem).offset(skip).limit(limit).all()

def create_inventory_item(db: Session, item: schemas.InventoryCreate):
    print("test-"*50)
    db_item = models.InventoryItem(
        name=item.name,
        category=item.category,
        price=item.price,
        description=item.description,
        stock_count=item.stock_count,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_inventory_item(db: Session, item_id: int, updates: schemas.InventoryUpdate):
    db_item = get_inventory_item(db, item_id)
    if not db_item:
        return None
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db_item.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_inventory_item(db: Session, item_id: int):
    db_item = get_inventory_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

def deduct_stock(db: Session, item_id: int, quantity: int):
    db_item = get_inventory_item(db, item_id)
    if db_item and db_item.stock_count >= quantity:
        db_item.stock_count -= quantity
        db_item.updated_at = datetime.utcnow().isoformat()
        db.commit()
        db.refresh(db_item)
        return db_item
    return None

