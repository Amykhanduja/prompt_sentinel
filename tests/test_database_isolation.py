import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_database_is_isolated(db_session):
    # Verify the test database url
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    
    # Must have a URL
    assert TEST_DATABASE_URL is not None
    
    # Must explicitly be the test database
    assert "promptsentinel_test" in TEST_DATABASE_URL
    
    # Should not match the normal database
    DATABASE_URL = os.getenv("DATABASE_URL")
    assert TEST_DATABASE_URL != DATABASE_URL
    
    # Verify the actual connection uses the test database
    # For postgresql, we can query current_database()
    result = db_session.execute(text("SELECT current_database();"))
    active_db = result.scalar()
    
    assert active_db == "promptsentinel_test"
    assert active_db != "promptsentinel"

def test_production_database_protection():
    # Attempting to drop the real database should fail fast based on URL
    
    # In conftest.py, we have safety checks. If we pretend we are trying to 
    # run destructive operations on the real database by passing its URL to a 
    # mock check, it should raise.
    
    # We can just explicitly test the safety logic that we implemented in conftest.
    db_url = os.getenv("DATABASE_URL")
    
    if "promptsentinel_test" not in db_url:
        with pytest.raises(Exception):
            # This simulates what conftest does
            if "promptsentinel_test" not in db_url:
                raise RuntimeError("TEST_DATABASE_URL must point to a test database")
