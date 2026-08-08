import pytest
from fastapi.testclient import TestClient
from app import app
from sqlalchemy import text
from database.connection import SessionLocal
import uuid

@pytest.fixture(scope="session")
def auth_client():
    client = TestClient(app)
    db = SessionLocal()
    
    # Generate unique test user
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    
    try:
        # Register
        resp = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "password123"
        })
        assert resp.status_code == 201
        
        # Login
        resp = client.post("/api/v1/auth/login", data={
            "username": username,
            "password": "password123"
        })
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        
        # Set headers
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client
    finally:
        # Cleanup
        db.execute(text("DELETE FROM users WHERE username = :username"), {"username": username})
        db.commit()
        db.close()
