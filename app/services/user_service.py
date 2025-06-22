from sqlalchemy.orm import Session
from fastapi import HTTPException

from .. import models, schemas, auth

def create_user(db: Session, user_create: schemas.UserCreate) -> models.UserDB:
    """
    새로운 사용자를 생성(회원가입)합니다.
    """
    if db.query(models.UserDB).filter(models.UserDB.email == user_create.email).first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    
    hashed_password = auth.get_password_hash(user_create.password)
    db_user = models.UserDB(
        email=user_create.email,
        hashed_password=hashed_password,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        phone_number=user_create.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user 