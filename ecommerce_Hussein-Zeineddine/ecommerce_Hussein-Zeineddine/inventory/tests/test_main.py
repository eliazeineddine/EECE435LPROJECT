 # inventory/tests/test_main.py

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Adjust the path to import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app import models

# Use a separate database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_inventory.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database and the tables
Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_add_goods():
    response = client.post(
        "/inventory",
        json={
            "name": "Smartphone",
            "category": "electronics",
            "price": 699.99,
            "description": "Latest model smartphone with advanced features",
            "stock_count": 50
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Smartphone"
    assert response.json()["category"] == "electronics"
    assert response.json()["price"] == 699.99
    assert response.json()["stock_count"] == 50

def test_add_goods_invalid_category():
    response = client.post(
        "/inventory",
        json={
            "name": "T-Shirt",
            "category": "invalid_category",
            "price": 19.99,
            "description": "Comfortable cotton t-shirt",
            "stock_count": 100
        }
    )
    assert response.status_code == 422  # Validation error

def test_get_all_goods():
    # Assuming at least one item has been added
    response = client.get("/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_get_goods_details():
    # First, add a new item to get its ID
    response = client.post(
        "/inventory",
        json={
            "name": "Jeans",
            "category": "clothes",
            "price": 49.99,
            "description": "Stylish denim jeans",
            "stock_count": 30
        }
    )
    assert response.status_code == 201
    item_id = response.json()["id"]

    # Now, retrieve the item details
    response = client.get(f"/inventory/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Jeans"

def test_update_goods():
    # First, add a new item to update
    response = client.post(
        "/inventory",
        json={
            "name": "Headphones",
            "category": "electronics",
            "price": 199.99,
            "description": "Noise-cancelling over-ear headphones",
            "stock_count": 20
        }
    )
    assert response.status_code == 201
    item_id = response.json()["id"]

    # Update the price and stock_count
    response = client.put(
        f"/inventory/{item_id}",
        json={
            "price": 149.99,
            "stock_count": 25
        }
    )
    assert response.status_code == 200
    assert response.json()["price"] == 149.99
    assert response.json()["stock_count"] == 25

def test_deduct_goods():
    # First, add a new item to deduct
    response = client.post(
        "/inventory",
        json={
            "name": "Coffee Mug",
            "category": "accessories",
            "price": 9.99,
            "description": "Ceramic coffee mug",
            "stock_count": 10
        }
    )
    assert response.status_code == 201
    item_id = response.json()["id"]

    # Deduct one unit from stock
    response = client.delete(f"/inventory/{item_id}")
    assert response.status_code == 200
    assert response.json()["stock_count"] == 9

def test_deduct_goods_insufficient_stock():
    # First, add a new item with stock_count = 0
    response = client.post(
        "/inventory",
        json={
            "name": "Limited Edition Sneakers",
            "category": "clothes",
            "price": 299.99,
            "description": "Exclusive sneakers release",
            "stock_count": 0
        }
    )
    assert response.status_code == 201
    item_id = response.json()["id"]

    # Attempt to deduct stock
    response = client.delete(f"/inventory/{item_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found or insufficient stock"

