from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional

from . import models, schemas, database

# --- 비밀번호 암호화 설정 ---
# 사용할 암호화 알고리즘(bcrypt)과 컨텍스트를 설정합니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 인증 스키마 설정
# /token 경로에서 토큰을 발급받도록 설정합니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# --- 환경변수 설정 (보안상 매우 중요) ---
# 실제 운영 환경에서는 .env 파일이나 다른 방법을 통해 관리해야 합니다.
SECRET_KEY = "your-secret-key"  # TODO: 실제 배포 시에는 반드시 강력하고 안전한 키로 변경하세요.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- 핵심 인증 함수 ---

def verify_password(plain_password, hashed_password):
    """일반 비밀번호와 해시된 비밀번호를 비교합니다."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """비밀번호를 해싱합니다."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    토큰을 검증하고 현재 사용자를 반환하는 의존성 함수.
    이 함수를 API 엔드포인트의 Depends에 추가하면 해당 API는 보호됩니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.UserDB).filter(models.UserDB.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """
    현재 사용자가 활성 상태인지 확인합니다. (현재는 항상 True)
    향후 is_active 플래그 등을 모델에 추가하여 확장할 수 있습니다.
    """
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 