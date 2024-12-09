# inventory/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas, crud
from .database import async_engine, get_async_db
from typing import List

# Create all tables (if not using init_db.sql for inventory)
models.Base.metadata.create_all(bind=async_engine)

app = FastAPI(title="Inventory Service")

@app.post("/inventory", response_model=schemas.InventoryResponse, status_code=status.HTTP_201_CREATED)
async def add_goods(item: schemas.InventoryCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.create_inventory_item(db=db, item=item)

@app.delete("/inventory/{item_id}", response_model=schemas.InventoryResponse)
async def deduct_goods(item_id: int, db: AsyncSession = Depends(get_async_db)):
    db_item = await crud.deduct_stock(db, item_id=item_id, quantity=1)  # Assuming deducting 1 unit
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found or insufficient stock")
    return db_item

@app.put("/inventory/{item_id}", response_model=schemas.InventoryResponse)
async def update_goods(item_id: int, updates: schemas.InventoryUpdate, db: AsyncSession = Depends(get_async_db)):
    db_item = await crud.update_inventory_item(db, item_id=item_id, updates=updates)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/inventory", response_model=List[schemas.InventoryResponse])
async def get_all_goods(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_inventory_items(db, skip=skip, limit=limit)

@app.get("/inventory/{item_id}", response_model=schemas.InventoryResponse)
async def get_goods_details(item_id: int, db: AsyncSession = Depends(get_async_db)):
    db_item = await crud.get_inventory_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return {"status": "ok"}
