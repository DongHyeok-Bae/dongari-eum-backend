from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from .. import models, schemas

def create_member(db: Session, club_id: int, member_data: schemas.ClubMemberCreate) -> models.ClubMemberDB:
    """
    특정 동아리에 새로운 부원을 추가합니다.
    """
    if not db.query(models.ClubDB).filter(models.ClubDB.id == club_id).first():
        raise HTTPException(status_code=404, detail="해당 동아리를 찾을 수 없습니다.")
    
    db_member = models.ClubMemberDB(**member_data.dict(), club_id=club_id)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_members_by_club(db: Session, club_id: int) -> List[models.ClubMemberDB]:
    """
    특정 동아리의 모든 부원 목록을 조회합니다.
    """
    db_club = db.query(models.ClubDB).filter(models.ClubDB.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="해당 동아리를 찾을 수 없습니다.")
    
    return db_club.club_members

def update_member_info(db: Session, member_id: int, member_update: schemas.ClubMemberUpdate) -> models.ClubMemberDB:
    """
    특정 부원의 정보를 수정합니다. (예: 역할 변경)
    """
    db_member = db.query(models.ClubMemberDB).filter(models.ClubMemberDB.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="해당 부원을 찾을 수 없습니다.")
    
    update_data = member_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_member, key, value)
        
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def delete_member(db: Session, member_id: int):
    """
    특정 부원을 삭제(추방)합니다.
    """
    db_member = db.query(models.ClubMemberDB).filter(models.ClubMemberDB.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="해당 부원을 찾을 수 없습니다.")

    db.delete(db_member)
    db.commit()
    return {"detail": "부원이 삭제되었습니다."} 