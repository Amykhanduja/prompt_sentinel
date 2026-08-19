import os
import pytest
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from alembic import command
from alembic.config import Config

from app import app
from database.dependencies import get_db
from database.base import Base
# Make sure all models are imported
from database.models import models, feedback, learning

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    pytest.exit("TEST_DATABASE_URL environment variable is not set. Aborting tests to prevent destruction of the real database.")

if "promptsentinel_test" not in TEST_DATABASE_URL:
    pytest.exit(f"TEST_DATABASE_URL must point to a test database (e.g., promptsentinel_test). Found: {TEST_DATABASE_URL}")

if TEST_DATABASE_URL == os.getenv("DATABASE_URL"):
    pytest.exit("TEST_DATABASE_URL cannot be identical to DATABASE_URL. Aborting tests.")

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Setup test DB tables using Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    
    # Clean the schema completely to avoid enum conflicts
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        conn.commit()
    
    command.upgrade(alembic_cfg, "head")

@pytest.fixture
def db_session():
    """Provides a fresh database session for a test."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    """Provides a TestClient with the get_db dependency overridden to use the test session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_client(client, db_session):
    """Provides an authenticated TestClient."""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    
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
    
    # We do not need explicit DELETE here because tests will use cleanup fixtures
    # or transaction rollback, but for completeness we can delete it
    with db_session.begin_nested() if db_session.in_transaction() else db_session.begin():
        db_session.execute(text("DELETE FROM users WHERE username = :username"), {"username": username})
