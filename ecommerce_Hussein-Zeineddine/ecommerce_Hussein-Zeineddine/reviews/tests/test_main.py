# reviews/tests/test_main.py

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app import models, auth

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_reviews.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def create_user(db, username: str, password: str):
    hashed_password = auth.get_password_hash(password)
    user = models.Review(
        product_id=1,
        customer_id=1,
        rating=5,
        comment="Great product!",
        is_flagged=False,
        created_at="2024-04-27T12:34:56.789012",
        updated_at="2024-04-27T12:34:56.789012"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_submit_review():
    # First, create a user
    db = TestingSessionLocal()
    user = create_user(db, "testuser", "testpassword")
    db.close()

    # Authenticate to get token
    response = client.post(
        "/token",
        data={"username": "1", "password": "testpassword"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Submit a review
    response = client.post(
        "/reviews",
        json={
            "product_id": 1,
            "rating": 4,
            "comment": "Good quality."
        },
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["rating"] == 4
    assert response.json()["comment"] == "Good quality."

def test_update_review():
    db = TestingSessionLocal()
    review = models.Review(
        product_id=2,
        customer_id=1,
        rating=3,
        comment="Average product.",
        is_flagged=False,
        created_at="2024-04-27T12:34:56.789012",
        updated_at="2024-04-27T12:34:56.789012"
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    db.close()

    # Authenticate to get token
    response = client.post(
        "/token",
        data={"username": "1", "password": "testpassword"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Update the review
    response = client.put(
        f"/reviews/{review.id}",
        json={
            "rating": 5,
            "comment": "Actually, it's great!"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5
    assert response.json()["comment"] == "Actually, it's great!"

def test_delete_review():
    db = TestingSessionLocal()
    review = models.Review(
        product_id=3,
        customer_id=1,
        rating=2,
        comment="Not satisfied.",
        is_flagged=False,
        created_at="2024-04-27T12:34:56.789012",
        updated_at="2024-04-27T12:34:56.789012"
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    db.close()

    # Authenticate to get token
    response = client.post(
        "/token",
        data={"username": "1", "password": "testpassword"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Delete the review
    response = client.delete(
        f"/reviews/{review.id}",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == review.id

def test_get_product_reviews():
    db = TestingSessionLocal()
    review1 = models.Review(
        product_id=4,
        customer_id=1,
        rating=5,
        comment="Excellent!",
        is_flagged=False,
        created_at="2024-04-27T12:34:56.789012",
        updated_at="2024-04-27T12:34:56.789012"
    )
    review2 = models.Review(
        product_id=4,
        customer_id=1,
        rating=4,
        comment="Very good.",
        is_flagged=False,
        created_at="2024-04-27T12:35:56.789012",
        updated_at="2024-04-27T12:35:56.789012"
    )
    db.add(review1)
    db.add(review2)
    db.commit()
    db.close()

    response = client.get("/reviews/product/4")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_customer_reviews():
    db = TestingSessionLocal()
    review1 = models.Review(
        product_id=5,
        customer_id=2,
        rating=3,
        comment="It's okay.",
        is_flagged=False,
        created_at="2024-04-27T12:36:56.789012",
        updated_at="2024-04-27T12:36:56.789012"
    )
    review2 = models.Review(
        product_id=6,
        customer_id=2,
        rating=2,
        comment="Could be better.",
        is_flagged=False,
        created_at="2024-04-27T12:37:56.789012",
        updated_at="2024-04-27T12:37:56.789012"
    )
    db.add(review1)
    db.add(review2)
    db.commit()
    db.close()

    response = client.get("/reviews/customer/2")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_moderate_review():
    db = TestingSessionLocal()
    review = models.Review(
        product_id=7,
        customer_id=3,
        rating=1,
        comment="Terrible product.",
        is_flagged=False,
        created_at="2024-04-27T12:38:56.789012",
        updated_at="2024-04-27T12:38:56.789012"
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    db.close()

    # Authenticate as admin (assuming admin is user_id=0)
    response = client.post(
        "/token",
        data={"username": "0", "password": "adminpassword"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Flag the review
    response = client.post(
        f"/reviews/{review.id}/moderate",
        json={"action": "flag"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_flagged"] == True

    # Approve the review
    response = client.post(
        f"/reviews/{review.id}/moderate",
        json={"action": "approve"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_flagged"] == False
 
