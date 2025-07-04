from fastapi import APIRouter, Depends, Form, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas
from ..database import get_db
from ..services import club_service

router = APIRouter(
    prefix="/clubs",
    tags=["Clubs"]
)

@router.post("", response_model=schemas.Club)
def create_club(
    name: str = Form(...),
    club_type: str = Form(...),
    topic: str = Form(...),
    password: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = File(None)
):
    """
    새로운 동아리를 생성합니다 (이미지 업로드 포함).
    """
    return club_service.create_club(
        db=db, 
        name=name, 
        club_type=club_type, 
        topic=topic, 
        password=password, 
        description=description, 
        file=file
    )

@router.get("", response_model=List[schemas.Club])
def get_clubs(
    db: Session = Depends(get_db),
    name: Optional[str] = None
):
    """
    동아리 목록을 조회합니다.
    'name' 쿼리 파라미터가 제공되면, 해당 이름으로 동아리를 검색합니다.
    """
    if name:
        return club_service.search_clubs_by_name(db=db, name=name)
    return club_service.get_all_clubs(db=db)

@router.post("/join", response_model=schemas.JoinClubResponse)
def join_club(join_request: schemas.ClubJoin, db: Session = Depends(get_db)):
    """
    이름과 비밀번호로 특정 동아리에 참여합니다.
    """
    db_club = club_service.join_club(db=db, join_request=join_request)
    return {"message": "가입에 성공했습니다.", "club_id": db_club.id}

@router.get("/{club_id}", response_model=schemas.Club)
def get_club_by_id(club_id: int, db: Session = Depends(get_db)):
    """
    ID로 특정 동아리의 id, name, image_url, description, club_type, topic을 반환합니다.
    """
    club = club_service.get_club_by_id(db=db, club_id=club_id)
    # 필요한 필드만 추출해서 반환
    return {
        "id": club.id,
        "name": club.name,
        "image_url": club.image_url,
        "description": club.description,
        "club_type": club.club_type,
        "topic": club.topic
    } 