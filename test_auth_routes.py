import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app import app
from database.connection import SessionLocal

client = TestClient(app)

def test_imports():
    from app import app
    from api.auth import router
    assert app
    assert router

def test_routes_exist():
    def _get_paths(routes):
        paths = []
        for r in routes:
            if hasattr(r, "path"):
                paths.append(r.path)
            elif hasattr(r, "routes"):
                paths.extend(_get_paths(r.routes))
        return paths
    routes = _get_paths(app.routes)
    assert "/api/v1/auth/register" in routes
    assert "/api/v1/auth/login" in routes
    assert "/api/v1/auth/me" in routes

def setup_module(module):
    db = SessionLocal()
    db.execute(text("DELETE FROM users WHERE username = 'routetestuser'"))
    db.commit()
    db.close()

def teardown_module(module):
    db = SessionLocal()
    db.execute(text("DELETE FROM users WHERE username = 'routetestuser'"))
    db.commit()
    db.close()

def test_registration():
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "routetestuser", "email": "routetest@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "routetestuser"
    assert data["email"] == "routetest@example.com"
    assert "hashed_password" not in data
    assert "id" in data
    assert data["is_active"] == True
    
    # Verify database contains hash
    db = SessionLocal()
    user = db.execute(text("SELECT hashed_password FROM users WHERE username = 'routetestuser'")).fetchone()
    db.close()
    assert user is not None
    assert user[0] != "password123"

def test_duplicate_registration():
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "routetestuser", "email": "routetest@example.com", "password": "password123"}
    )
    assert response.status_code == 400

def test_login_and_me():
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "routetestuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    token = data["access_token"]
    
    # ME authenticated
    response_me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response_me.status_code == 200
    me_data = response_me.json()
    assert me_data["username"] == "routetestuser"
    assert "hashed_password" not in me_data
    
    # Wrong password
    response_wrong = client.post(
        "/api/v1/auth/login",
        data={"username": "routetestuser", "password": "wrongpassword"}
    )
    assert response_wrong.status_code == 401

def test_me_unauthenticated():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_invalid_token():
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
