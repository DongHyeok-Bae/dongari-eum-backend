from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date

# Pydantic 모델을 사용하여 API의 데이터 형태를 정의합니다.
# 이 모델들은 데이터의 유효성 검사, 자동 문서화 등에 사용됩니다.

# --- User Schemas ---

class UserBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    clubs: List['Club'] = []
    operation_logs: List['OperationLog'] = []

    class Config:
        from_attributes = True


# --- Club Schemas (기존 Group 스키마 수정) ---

class ClubBase(BaseModel):
    name: str
    club_type: str
    topic: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class ClubCreate(ClubBase):
    password: str

class ClubJoin(BaseModel):
    name: str
    password: str

# Club 스키마에 members 필드 추가
class Club(ClubBase):
    id: int
    members: List[User] = []
    club_members: List['ClubMember'] = []
    accounting_entries: List['AccountingEntry'] = []
    operation_logs: List['OperationLog'] = []

    class Config:
        from_attributes = True

# --- ClubMember Schemas ---

class ClubMemberBase(BaseModel):
    name: str
    birth_date: Optional[str] = None
    student_id: Optional[str] = None
    major: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    member_year: Optional[int] = None
    role: Optional[str] = "부원"
    memo: Optional[str] = None

class ClubMemberCreate(ClubMemberBase):
    pass

class ClubMember(ClubMemberBase):
    id: int
    club_id: int

    class Config:
        from_attributes = True

class ClubMemberUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[str] = None
    student_id: Optional[str] = None
    major: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    member_year: Optional[int] = None
    role: Optional[str] = None
    memo: Optional[str] = None

# --- Token Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Accounting Schemas ---

class AccountingEntryBase(BaseModel):
    date: str
    manager: Optional[str] = None
    description: str
    amount: int
    photo_url: Optional[str] = None

class AccountingEntryCreate(AccountingEntryBase):
    pass

class AccountingEntry(AccountingEntryBase):
    id: int
    club_id: int

    class Config:
        from_attributes = True

# --- UploadedFile ---
class UploadedFile(BaseModel):
    id: int
    file_name: str
    file_path: str

    class Config:
        orm_mode = True

# --- OperationLog ---
class OperationLogBase(BaseModel):
    title: str
    post_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    team: Optional[str] = None
    content: dict

class OperationLog(OperationLogBase):
    id: int
    author_id: Optional[int] = None
    files: List[UploadedFile] = []

    class Config:
        orm_mode = True

class OperationLogCreate(OperationLogBase):
    pass

# User와 Club 스키마가 서로 참조할 수 있도록 업데이트
User.model_rebuild()
Club.model_rebuild()