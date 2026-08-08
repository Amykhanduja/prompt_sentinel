from fastapi.testclient import TestClient
from sqlalchemy import text
from app import app
from database.connection import SessionLocal
import sys

print("Initializing test client...")
client = TestClient(app)

print("Checking routes...")
routes = [r.path for r in app.routes]
assert "/api/v1/auth/register" in routes
assert "/api/v1/auth/login" in routes
assert "/api/v1/auth/me" in routes

def run_tests():
    db = SessionLocal()
    db.execute(text("DELETE FROM users WHERE username = 'routetestuser'"))
    db.commit()
    db.close()

    print("Testing registration...")
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "routetestuser", "email": "routetest@example.com", "password": "password123"}
    )
    if response.status_code != 201:
        print("Registration failed:", response.text)
        sys.exit(1)
    
    data = response.json()
    assert data["username"] == "routetestuser"
    assert "hashed_password" not in data
    
    print("Testing login...")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "routetestuser", "password": "password123"}
    )
    if response.status_code != 200:
        print("Login failed:", response.text)
        sys.exit(1)
        
    token = response.json()["access_token"]
    
    print("Testing ME...")
    response_me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response_me.status_code != 200:
        print("ME failed:", response_me.text)
        sys.exit(1)
        
    print("Testing ME without token...")
    assert client.get("/api/v1/auth/me").status_code == 401
    
    print("Testing wrong password...")
    assert client.post("/api/v1/auth/login", data={"username": "routetestuser", "password": "wrong"}).status_code == 401
    
    print("Cleaning up...")
    db = SessionLocal()
    db.execute(text("DELETE FROM users WHERE username = 'routetestuser'"))
    db.commit()
    db.close()
    
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_tests()
