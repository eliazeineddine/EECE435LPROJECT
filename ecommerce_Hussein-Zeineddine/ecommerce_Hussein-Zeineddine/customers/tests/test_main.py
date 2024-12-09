 
# customers/tests/test_main.py

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

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

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

def test_register_customer():
    response = client.post(
        "/customers/register",
        json={
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St",
            "gender": "Male",
            "marital_status": "Single"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "johndoe"

def test_register_existing_username():
    # Register the same user again
    response = client.post(
        "/customers/register",
        json={
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St",
            "gender": "Male",
            "marital_status": "Single"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

def test_get_customer():
    response = client.get("/customers/johndoe")
    assert response.status_code == 200
    assert response.json()["username"] == "johndoe"

def test_get_nonexistent_customer():
    response = client.get("/customers/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

def test_charge_wallet():
    response = client.post(
        "/customers/johndoe/charge",
        json={"amount": 100.0}
    )
    assert response.status_code == 200
    assert response.json()["wallet_balance"] == 100.0

def test_deduct_wallet():
    response = client.post(
        "/customers/johndoe/deduct",
        json={"amount": 50.0}
    )
    assert response.status_code == 200
    assert response.json()["wallet_balance"] == 50.0

def test_deduct_wallet_insufficient_funds():
    response = client.post(
        "/customers/johndoe/deduct",
        json={"amount": 100.0}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds or customer not found"
