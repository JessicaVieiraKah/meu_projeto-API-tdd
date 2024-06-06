import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

def test_create_product(client):
    response = client.post("/products/", json={"name": "Product 1", "price": 6000})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Product 1"
    assert data["price"] == 6000

def test_update_product_not_found(client):
    response = client.patch("/products/999", json={"name": "Updated Product"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}

def test_update_product(client):
    response = client.post("/products/", json={"name": "Product 2", "price": 7000})
    assert response.status_code == 201
    product_id = response.json()["id"]

    response = client.patch(f"/products/{product_id}", json={"name": "Updated Product 2"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product 2"

def test_filter_products(client):
    client.post("/products/", json={"name": "Product 3", "price": 7500})
    client.post("/products/", json={"name": "Product 4", "price": 8500})
    response = client.get("/products/filter/?min_price=5000&max_price=8000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(5000 < product["price"] < 8000 for product in data)
