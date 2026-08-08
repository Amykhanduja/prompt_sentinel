from database.connection import SessionLocal

def get_db():
    """FastAPI dependency for yielding DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
