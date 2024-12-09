# sales/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas, crud
from .database import async_engine, Base, get_async_db
from typing import List

# Create all tables
Base.metadata.create_all(bind=async_engine)

app = FastAPI(title="Sales Service")

@app.post("/sales", response_model=schemas.SaleResponse, status_code=status.HTTP_201_CREATED)
async def process_sale(sale: schemas.SaleCreate, db: AsyncSession = Depends(get_async_db)):
    db_sale, error = await crud.create_sale(db=db, sale=sale)
    if error:
        if error in {"Customer not found", "Product not found"}:
            raise HTTPException(status_code=404, detail=error)
        elif error in {"Insufficient funds", "Insufficient stock"}:
            raise HTTPException(status_code=400, detail=error)
    return db_sale

@app.get("/sales", response_model=List[schemas.SaleResponse])
async def get_all_sales(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_sales(db, skip=skip, limit=limit)

@app.get("/sales/{sale_id}", response_model=schemas.SaleResponse)
async def get_sale(sale_id: int, db: AsyncSession = Depends(get_async_db)):
    db_sale = await crud.get_sale(db, sale_id=sale_id)
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return db_sale

@app.get("/sales/goods", response_model=List[dict])
async def display_available_goods(db: AsyncSession = Depends(get_async_db)):
    items = await db.execute(
        models.InventoryItem.select().where(models.InventoryItem.stock_count > 0)
    )
    result = [{"name": item.name, "price": item.price} for item in items.scalars()]
    return result

@app.get("/sales/goods/{item_id}", response_model=dict)
async def get_goods_details(item_id: int, db: AsyncSession = Depends(get_async_db)):
    item = await db.execute(
        models.InventoryItem.select().where(models.InventoryItem.id == item_id)
    )
    item = item.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": item.id,
        "customer_id": 0,
        "item_id": item.id,
        "sale_date": item.updated_at,
        "amount": item.price,
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return {"status": "ok"}
