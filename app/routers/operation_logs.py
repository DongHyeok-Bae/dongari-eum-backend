from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException
from pydantic import ValidationError

from .. import models, schemas, auth as auth_utils
from ..database import get_db
from ..services import operation_log_service

router = APIRouter(
    prefix="/clubs/{club_id}/operation-logs",
    tags=["Operation Logs"],
)

@router.post("", response_model=schemas.OperationLog)
def create_operation_log_for_club(
    club_id: int,
    log_data: str = Form(...),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.UserDB = Depends(auth_utils.get_current_active_user),
):
    """
    특정 동아리에 새로운 활동 기록을 생성합니다.
    """
    try:
        log_create = schemas.OperationLogCreate.model_validate_json(log_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    return operation_log_service.create_operation_log(
        db=db,
        club_id=club_id,
        log_create=log_create,
        current_user=current_user,
        files=files,
    )

@router.get("", response_model=List[schemas.OperationLog])
def get_operation_logs_for_club(club_id: int, db: Session = Depends(get_db)):
    """
    특정 동아리의 모든 활동 기록 목록을 조회합니다.
    """
    return operation_log_service.get_operation_logs_by_club(db=db, club_id=club_id)

@router.get("/{log_id}", response_model=schemas.OperationLog)
def get_operation_log(
    club_id: int, 
    log_id: int, 
    db: Session = Depends(get_db)
):
    """
    특정 ID를 가진 활동 기록의 상세 정보를 조회합니다.
    """
    # club_id는 경로에 있지만, log_id만으로 조회가 가능하므로 직접 사용하지는 않습니다.
    # 하지만 경로의 일관성을 위해 유지합니다.
    log = operation_log_service.get_operation_log_by_id(db=db, log_id=log_id)
    if not log or log.club_id != club_id:
        raise HTTPException(status_code=404, detail="활동 기록을 찾을 수 없습니다.")
    return log 