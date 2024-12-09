 # reviews/app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_review(db: Session, review_id: int):
    return db.query(models.Review).filter(models.Review.id == review_id).first()

def get_reviews_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Review).filter(models.Review.product_id == product_id).offset(skip).limit(limit).all()

def get_reviews_by_customer(db: Session, customer_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Review).filter(models.Review.customer_id == customer_id).offset(skip).limit(limit).all()

def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(
        product_id=review.product_id,
        customer_id=review.customer_id,
        rating=review.rating,
        comment=review.comment,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def update_review(db: Session, review_id: int, updates: schemas.ReviewUpdate):
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
    db_review.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_review(db: Session, review_id: int):
    db_review = get_review(db, review_id)
    if db_review:
        db.delete(db_review)
        db.commit()
    return db_review

def moderate_review(db: Session, review_id: int, action: str):
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    if action == "flag":
        db_review.is_flagged = True
    elif action == "approve":
        db_review.is_flagged = False
    db_review.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(db_review)
    return db_review

