from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import uuid
import pandas as pd
from fastapi.responses import StreamingResponse
import io
from urllib.parse import quote

from .. import models, schemas
from ..database import get_db
from ..services import accounting_service

router = APIRouter(
    prefix="/clubs/{club_id}/accounting",
    tags=["Accounting"],
)

@router.post("", response_model=schemas.AccountingEntry)
def create_accounting_entry(
    club_id: int,
    date: str = Form(...),
    description: str = Form(...),
    amount: int = Form(...),
    manager: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    새로운 회계 내역을 생성합니다 (사진 업로드 포함).
    """
    return accounting_service.create_new_entry(
        db=db,
        club_id=club_id,
        date=date,
        description=description,
        amount=amount,
        manager=manager,
        photo=photo
    )

@router.get("", response_model=List[schemas.AccountingEntry])
def get_accounting_entries(
    club_id: int, 
    db: Session = Depends(get_db),
    export: bool = False
):
    """
    특정 동아리의 모든 회계 내역을 조회합니다.
    export=true 쿼리 파라미터가 있으면 엑셀 파일로 내보냅니다.
    """
    if export:
        excel_data, club_name = accounting_service.export_to_excel(db, club_id)
        filename = f"회계내역_{club_name}.xlsx"
        encoded_filename = quote(filename)
        
        headers = {
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"
        }
        
        return StreamingResponse(
            excel_data, 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers=headers
        )
    
    # export=false 인 경우
    db_club = db.query(models.ClubDB).filter(models.ClubDB.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="해당 동아리를 찾을 수 없습니다.")
    return db_club.accounting_entries 