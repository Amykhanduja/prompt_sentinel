import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        try:
            stmt = select(User).where(User.id == user_id)
            return self.db.execute(stmt).scalars().first()
        except Exception:
            self.db.rollback()
            raise

    def get_by_username(self, username: str) -> Optional[User]:
        try:
            stmt = select(User).where(User.username == username)
            return self.db.execute(stmt).scalars().first()
        except Exception:
            self.db.rollback()
            raise

    def get_by_email(self, email: str) -> Optional[User]:
        try:
            stmt = select(User).where(User.email == email)
            return self.db.execute(stmt).scalars().first()
        except Exception:
            self.db.rollback()
            raise

    def create(self, username: str, email: str, hashed_password: str, is_active: bool = True) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active
        )
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise
