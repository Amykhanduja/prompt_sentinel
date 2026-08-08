import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.models.models import User
from database.repositories.user_repository import UserRepository
from api.security import get_password_hash, verify_password

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register_user(self, username: str, email: str, plain_password: str) -> User:
        if self.user_repo.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        if self.user_repo.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = get_password_hash(plain_password)
        return self.user_repo.create(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )

    def authenticate_user(self, username: str, plain_password: str) -> User:
        user = self.user_repo.get_by_username(username)
        # Prevent timing attacks to some extent by returning generic error
        if not user or not verify_password(plain_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)
