# reviews/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas, crud, auth
from .database import async_engine, Base, get_async_db
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta

# Create all tables
Base.metadata.create_all(bind=async_engine)

app = FastAPI(title="Reviews Service")

@app.post("/token", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/reviews", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
async def submit_review(review: schemas.ReviewCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.create_review(db=db, review=review)

@app.put("/reviews/{review_id}", response_model=schemas.ReviewResponse)
async def update_review(review_id: int, updates: schemas.ReviewUpdate, db: AsyncSession = Depends(get_async_db)):
    db_review = await crud.get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return await crud.update_review(db=db, review_id=review_id, updates=updates)

@app.delete("/reviews/{review_id}", response_model=schemas.ReviewResponse)
async def delete_review(review_id: int, db: AsyncSession = Depends(get_async_db)):
    db_review = await crud.get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return await crud.delete_review(db=db, review_id=review_id)

@app.get("/reviews/product/{product_id}", response_model=List[schemas.ReviewResponse])
async def get_product_reviews(product_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_reviews_by_product(db, product_id=product_id)

@app.get("/reviews/customer/{customer_id}", response_model=List[schemas.ReviewResponse])
async def get_customer_reviews(customer_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_reviews_by_customer(db, customer_id=customer_id)

@app.post("/reviews/{review_id}/moderate", response_model=schemas.ReviewResponse)
async def moderate_review(review_id: int, moderation: schemas.ReviewModeration, db: AsyncSession = Depends(get_async_db)):
    db_review = await crud.get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return await crud.moderate_review(db=db, review_id=review_id, action=moderation.action)

@app.get("/reviews/{review_id}", response_model=schemas.ReviewResponse)
async def get_review_details(review_id: int, db: AsyncSession = Depends(get_async_db)):
    db_review = await crud.get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return {"status": "ok"}
