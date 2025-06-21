from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import uuid

# 현재 폴더(routers)의 상위 폴더(app)에 있는 파일들을 참조하기 위한 설정
from .. import models, schemas
from ..database import get_db

# APIRouter 인스턴스 생성
router = APIRouter()

# --- API 엔드포인트 구현 ---

@router.post("/groups/", response_model=schemas.Group, tags=["Groups"])
def create_group(
    name: str = Form(...),
    group_type: str = Form(...),
    topic: str = Form(...),
    password: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = File(None)
):
    """
    새로운 동아리를 생성합니다 (이미지 업로드 포함).
    """
    db_group = db.query(models.Group).filter(models.Group.name == name).first()
    if db_group:
        raise HTTPException(status_code=400, detail="이미 존재하는 동아리 이름입니다.")
    
    if not (password.isdigit() and len(password) == 4):
        raise HTTPException(status_code=400, detail="비밀번호는 4자리 숫자여야 합니다.")

    image_url_path = None
    if file:
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"static/images/{unique_filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        image_url_path = f"/{file_path}"

    new_group_data = schemas.GroupCreate(
        name=name,
        group_type=group_type,
        topic=topic,
        description=description,
        password=password
    )
    new_group = models.Group(**new_group_data.dict(), image_url=image_url_path)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

@router.get("/groups/search/", response_model=List[schemas.Group], tags=["Groups"])
def search_group(name: str, db: Session = Depends(get_db)):
    """
    이름에 포함된 키워드로 동아리를 검색합니다.
    """
    if not name.strip():
         raise HTTPException(status_code=400, detail="검색할 동아리 이름을 입력해주세요.")
    groups = db.query(models.Group).filter(models.Group.name.contains(name)).all()
    return groups

@router.post("/groups/join/", tags=["Groups"])
def join_group(join_request: schemas.GroupJoin, db: Session = Depends(get_db)):
    """
    이름과 비밀번호로 특정 동아리에 참여합니다.
    """
    db_group = db.query(models.Group).filter(models.Group.name == join_request.name).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="존재하지 않는 동아리입니다.")

    if db_group.password != join_request.password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    return {"detail": "동아리 참여에 성공했습니다."} 