 
# sales/tests/test_main.py

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

# Import Customer and InventoryItem models
from customers.app.models import Customer
from inventory.app.models import InventoryItem

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sales.db"

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

def setup_test_data():
    db = TestingSessionLocal()
    # Create a customer
    customer = Customer(
        full_name="Test User",
        username="testuser",
        hashed_password="hashedpassword",
        age=30,
        address="123 Test St",
        gender="Non-binary",
        marital_status="Single",
        wallet_balance=1000.0
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    # Create inventory items
    item1 = InventoryItem(
        name="Test Product 1",
        category="electronics",
        price=100.0,
        description="A test electronic product",
        stock_count=10,
        created_at="2024-04-27T12:34:56.789012",
        updated_at="2024-04-27T12:34:56.789012"
    )
    item2 = InventoryItem(
        name="Test Product 2",
        category="clothes",
        price=50.0,
        description="A test clothing product",
        stock_count=5,
        created_at="2024-04-27T12:35:56.789012",
        updated_at="2024-04-27T12:35:56.789012"
    )
    db.add(item1)
    db.add(item2)
    db.commit()
    db.refresh(item1)
    db.refresh(item2)
    db.close()

def teardown_test_data():
    db = TestingSessionLocal()
    db.query(models.Sale).delete()
    db.query(Customer).delete()
    db.query(InventoryItem).delete()
    db.commit()
    db.close()

def test_process_sale():
    setup_test_data()
    response = client.post(
        "/sales",
        json={
            "product_id": 1,
            "customer_username": "testuser",
            "quantity": 2
        }
    )
    assert response.status_code == 201
    assert response.json()["customer_id"] == 1
    assert response.json()["item_id"] == 1
    assert response.json()["amount"] == 200.0
    teardown_test_data()

def test_process_sale_insufficient_funds():
    setup_test_data()
    response = client.post(
        "/sales",
        json={
            "product_id": 1,
            "customer_username": "testuser",
            "quantity": 20  # Total amount = 2000, which exceeds wallet_balance=1000
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"
    teardown_test_data()

def test_process_sale_insufficient_stock():
    setup_test_data()
    response = client.post(
        "/sales",
        json={
            "product_id": 2,
            "customer_username": "testuser",
            "quantity": 10  # stock_count=5
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock"
    teardown_test_data()

def test_get_all_sales():
    setup_test_data()
    # Create a sale
    response = client.post(
        "/sales",
        json={
            "product_id": 1,
            "customer_username": "testuser",
            "quantity": 1
        }
    )
    assert response.status_code == 201
    # Get all sales
    response = client.get("/sales")
    assert response.status_code == 200
    assert len(response.json()) == 1
    teardown_test_data()

def test_get_sale():
    setup_test_data()
    # Create a sale
    response = client.post(
        "/sales",
        json={
            "product_id": 1,
            "customer_username": "testuser",
            "quantity": 1
        }
    )
    assert response.status_code == 201
    sale_id = response.json()["id"]
    # Get the sale
    response = client.get(f"/sales/{sale_id}")
    assert response.status_code == 200
    assert response.json()["id"] == sale_id
    teardown_test_data()
