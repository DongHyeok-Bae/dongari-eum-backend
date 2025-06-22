from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, UploadFile
from typing import List, Optional
import json
import os
import uuid
import shutil

from .. import models, schemas

def _save_uploaded_file(file: UploadFile) -> str:
    """
    업로드된 파일을 저장하고 URL 경로를 반환합니다.
    """
    UPLOAD_DIR = "static/files"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path.replace(os.path.sep, '/')
    finally:
        file.file.close()

def create_operation_log(
    db: Session,
    club_id: int,
    log_create: schemas.OperationLogCreate,
    current_user: models.UserDB,
    files: List[UploadFile],
) -> models.OperationLogDB:
    """새로운 활동 기록을 데이터베이스에 생성합니다."""
    club = db.query(models.ClubDB).filter(models.ClubDB.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="해당 동아리를 찾을 수 없습니다.")

    author = db.query(models.UserDB).filter(models.UserDB.id == current_user.id).first()
    if not author:
        raise HTTPException(status_code=404, detail="작성자를 찾을 수 없습니다.")

    db_log = models.OperationLogDB(
        **log_create.model_dump(exclude={"content"}),
        content=log_create.content,
        club_id=club_id,
        author_id=author.id,
    )

    if files:
        for file in files:
            file_path = _save_uploaded_file(file)
            db_file = models.UploadedFileDB(
                file_name=file.filename,
                file_path=file_path.replace(os.path.sep, "/"),
            )
            db_log.files.append(db_file)
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_operation_logs_by_club(db: Session, club_id: int) -> List[models.OperationLogDB]:
    """
    특정 동아리의 모든 활동 기록 목록을 조회합니다.
    """
    db_club = db.query(models.ClubDB).filter(models.ClubDB.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="해당 동아리를 찾을 수 없습니다.")
    
    return sorted(db_club.operation_logs, key=lambda x: x.created_at, reverse=True)

def get_operation_log_by_id(db: Session, log_id: int) -> Optional[models.OperationLogDB]:
    """
    ID로 특정 활동 기록을 조회합니다.
    (연결된 파일 목록을 함께 로드합니다)
    """
    return db.query(models.OperationLogDB).options(
        selectinload(models.OperationLogDB.files)
    ).filter(models.OperationLogDB.id == log_id).first() 