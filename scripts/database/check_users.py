from database.connection import SessionLocal
from database.models.models import User
from services.auth_service import get_password_hash

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(u.username, u.email)
    
if not users:
    print("No users found! Creating one...")
    new_user = User(
        username="test",
        email="test@example.com",
        hashed_password=get_password_hash("password123")
    )
    db.add(new_user)
    db.commit()
    print("Created test/password123 user")
