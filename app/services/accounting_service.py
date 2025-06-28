from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from typing import Optional
import shutil
import uuid
import io
import pandas as pd

from .. import models, schemas

def create_new_entry(
    db: Session, 
    club_id: int, 
    date: str, 
    description: str, 
    amount: int, 
    manager: Optional[str], 
    photo: Optional[UploadFile]
) -> models.AccountingEntryDB:
    """
    새로운 회계 내역을 데이터베이스에 생성하고, 첨부된 사진을 저장합니다.
    """
    # 1. 동아리 존재 여부 확인
    db_club = db.query(models.ClubDB).filter(models.ClubDB.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="해당 동아리를 찾을 수 없습니다.")

    # 2. 사진 파일 처리
    photo_url_path = None
    if photo and photo.filename:
        file_extension = photo.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"static/images/{unique_filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_url_path = file_path # URL 경로로 저장

    # 3. 데이터베이스에 내역 저장
    entry_data = schemas.AccountingEntryCreate(
        date=date,
        description=description,
        amount=amount,
        manager=manager,
        photo_url=photo_url_path
    )
    
    db_entry = models.AccountingEntryDB(**entry_data.dict(), club_id=club_id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry


def export_to_excel(db: Session, club_id: int):
    """
    특정 동아리의 회계 내역을 조회하고 엑셀 파일 데이터로 변환합니다.

    :param db: 데이터베이스 세션
    :param club_id: 동아리 ID
    :return: 엑셀 파일 데이터(BytesIO)와 동아리 이름을 튜플로 반환
    """
    # 1. 데이터베이스에서 회계 내역 조회
    db_club = db.query(models.ClubDB).filter(models.ClubDB.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="해당 동아리를 찾을 수 없습니다.")
    
    entries = db_club.accounting_entries
    if not entries:
        raise HTTPException(status_code=404, detail="내보낼 회계 내역이 없습니다.")

    # 2. Pandas 데이터프레임으로 변환
    data = [{
        "날짜": entry.date,
        "담당자": entry.manager,
        "내역": entry.description,
        "금액": entry.amount
    } for entry in sorted(entries, key=lambda x: x.date)]
    df = pd.DataFrame(data)

    # 3. 데이터프레임을 엑셀 파일로 메모리에 저장
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='회계 내역')
    
    output.seek(0)
    
    return output, db_club.name

def update_entry(db: Session, club_id: int, entry_id: int, entry_update: 'schemas.AccountingEntryUpdate'):
    db_entry = db.query(models.AccountingEntryDB).filter(
        models.AccountingEntryDB.id == entry_id,
        models.AccountingEntryDB.club_id == club_id
    ).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="해당 회계 내역을 찾을 수 없습니다.")
    for field, value in entry_update.dict(exclude_unset=True).items():
        setattr(db_entry, field, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def delete_entry(db: Session, club_id: int, entry_id: int):
    db_entry = db.query(models.AccountingEntryDB).filter(
        models.AccountingEntryDB.id == entry_id,
        models.AccountingEntryDB.club_id == club_id
    ).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="해당 회계 내역을 찾을 수 없습니다.")
    db.delete(db_entry)
    db.commit()
    return None