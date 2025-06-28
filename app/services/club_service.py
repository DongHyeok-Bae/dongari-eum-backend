from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from typing import List, Optional
import shutil
import uuid
import os

from .. import models, schemas
from ..auth import get_password_hash

def _save_club_image(file: UploadFile) -> Optional[str]:
    """
    동아리 이미지를 저장하고 경로를 반환합니다.
    """
    if not file:
        return None
        
    UPLOAD_DIR = "static/images"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path.replace(os.path.sep, '/')
    finally:
        file.file.close()

def create_club(
    db: Session, 
    name: str, 
    club_type: str, 
    topic: str, 
    password: str, 
    description: Optional[str], 
    file: Optional[UploadFile]
) -> models.ClubDB:
    """
    새로운 동아리를 생성합니다.
    """
    if db.query(models.ClubDB).filter(models.ClubDB.name == name).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 동아리 이름입니다.")
    
    if not (password.isdigit() and len(password) == 6):
        raise HTTPException(status_code=400, detail="비밀번호는 6자리 숫자여야 합니다.")

    image_url_path = _save_club_image(file)

    club_data = schemas.ClubCreate(
        name=name,
        club_type=club_type,
        topic=topic,
        description=description,
        password=password
    )
    
    new_club = models.ClubDB(**club_data.model_dump())
    if image_url_path:
        new_club.image_url = image_url_path
        
    db.add(new_club)
    db.commit()
    db.refresh(new_club)
    return new_club

def get_all_clubs(db: Session):
    """모든 동아리 목록을 반환합니다."""
    return db.query(models.ClubDB).all()

def search_clubs_by_name(db: Session, name: str) -> List[models.ClubDB]:
    """
    이름으로 동아리를 검색합니다.
    """
    if not name.strip():
        raise HTTPException(status_code=400, detail="검색할 동아리 이름을 입력해주세요.")
    return db.query(models.ClubDB).filter(models.ClubDB.name.contains(name)).all()

def join_club(db: Session, join_request: schemas.ClubJoin):
    """
    동아리에 참여(가입)합니다.
    """
    db_club = db.query(models.ClubDB).filter(models.ClubDB.name == join_request.name).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="존재하지 않는 동아리입니다.")

    if db_club.password != join_request.password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    return db_club

def get_club_by_id(db: Session, club_id: int) -> models.ClubDB:
    """
    ID로 동아리 정보를 조회합니다.
    """
    db_club = db.query(models.ClubDB).filter(models.ClubDB.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="해당 ID의 동아리를 찾을 수 없습니다.")
    return db_club 