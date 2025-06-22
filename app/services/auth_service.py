from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from .. import models, schemas, auth, database

def authenticate_user(db: Session, email: str, password: str) -> models.UserDB:
    """
    사용자를 인증합니다. 실패 시 None을 반환합니다.
    """
    user = db.query(models.UserDB).filter(models.UserDB.email == email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return None
    return user

def create_token_for_user(user: models.UserDB) -> dict:
    """
    사용자 정보를 바탕으로 액세스 토큰을 생성합니다.
    """
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 