from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..services import member_service

router = APIRouter(
    prefix="/clubs/{club_id}/members",
    tags=["Club Members"],
)

@router.post("", response_model=schemas.ClubMember)
def create_member_for_club(
    club_id: int,
    member: schemas.ClubMemberCreate,
    db: Session = Depends(get_db)
):
    """
    특정 동아리에 새로운 부원을 추가합니다.
    """
    return member_service.create_member(db=db, club_id=club_id, member_data=member)

@router.get("", response_model=List[schemas.ClubMember])
def get_members_for_club(club_id: int, db: Session = Depends(get_db)):
    """
    특정 동아리의 모든 부원 목록을 조회합니다.
    """
    return member_service.get_members_by_club(db=db, club_id=club_id)

@router.patch("/{member_id}", response_model=schemas.ClubMember)
def update_member(
    club_id: int, # 경로 일관성을 위해 추가되었지만, 서비스 로직에서는 사용되지 않을 수 있습니다.
    member_id: int,
    member_update: schemas.ClubMemberUpdate,
    db: Session = Depends(get_db)
):
    """
    특정 부원의 정보를 수정합니다.
    """
    return member_service.update_member_info(db=db, member_id=member_id, member_update=member_update)

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    club_id: int, # 경로 일관성을 위해 추가되었지만, 서비스 로직에서는 사용되지 않을 수 있습니다.
    member_id: int, 
    db: Session = Depends(get_db)
):
    """
    특정 부원을 삭제합니다.
    """
    member_service.delete_member(db=db, member_id=member_id)
    return 