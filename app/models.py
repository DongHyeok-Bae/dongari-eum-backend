from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime, JSON, Date
from sqlalchemy.orm import relationship
from .database import Base # 방금 만든 database.py에서 Base를 가져옵니다.
from datetime import datetime

# User와 Club 간의 다대다 관계를 위한 연결 테이블
user_club_association = Table('user_club_association', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('club_id', Integer, ForeignKey('clubs.id'))
)

# 'users' 테이블 모델
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String, nullable=True)

    # 사용자가 속한 동아리 목록
    clubs = relationship("ClubDB",
                          secondary=user_club_association,
                          back_populates="members")
    # 사용자가 작성한 기록
    operation_logs = relationship("OperationLogDB", back_populates="author")

# 'clubs'라는 이름의 테이블에 매핑될 ClubDB 클래스
class ClubDB(Base):
    __tablename__ = "clubs"

    # 테이블의 컬럼(속성)들을 정의합니다.
    id = Column(Integer, primary_key=True, index=True) # 자동 생성될 고유 ID
    name = Column(String, unique=True, index=True) # 동아리 이름 
    club_type = Column(String) # 동아리 유형 
    topic = Column(String)      # 동아리 주제 
    description = Column(String, nullable=True) # 동아리 설명 
    password = Column(String(4)) # 4자리 비밀번호
    image_url = Column(String, nullable=True)

    # 동아리에 속한 사용자(멤버) 목록
    members = relationship("UserDB",
                           secondary=user_club_association,
                           back_populates="clubs")
                           
    # 이 동아리에 속한 부원 목록 (운영진이 관리)
    club_members = relationship("ClubMemberDB", back_populates="club")
    
    # 이 동아리의 회계 내역 목록
    accounting_entries = relationship("AccountingEntryDB", back_populates="club", cascade="all, delete-orphan")

    # 이 동아리의 기록 목록
    operation_logs = relationship("OperationLogDB", back_populates="club", cascade="all, delete-orphan")

# 'club_members' 테이블 모델 (동아리 운영진이 관리하는 명단)
class ClubMemberDB(Base):
    __tablename__ = "club_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    birth_date = Column(String, nullable=True)
    student_id = Column(String, nullable=True)
    major = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    member_year = Column(Integer, nullable=True) # 기수
    role = Column(String, default="부원") # 직책
    memo = Column(String, nullable=True) # 메모

    # 이 부원이 속한 동아리
    club_id = Column(Integer, ForeignKey("clubs.id"))
    club = relationship("ClubDB", back_populates="club_members")

# 'accounting_entries' 테이블 모델
class AccountingEntryDB(Base):
    __tablename__ = "accounting_entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    manager = Column(String) # 담당자
    description = Column(String, nullable=False) # 내역
    amount = Column(Integer, nullable=False) # 금액 (수입: 양수, 지출: 음수)
    photo_url = Column(String, nullable=True) # 영수증 사진 경로

    # 이 회계 내역이 속한 동아리
    club_id = Column(Integer, ForeignKey("clubs.id"))
    club = relationship("ClubDB", back_populates="accounting_entries")

# 'posts' 테이블 모델
class OperationLogDB(Base):
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True) # 제목 필드 추가
    post_type = Column(String) # 예: 'meeting_minutes', 'proposal', 'report' 등
    
    # --- 새로 추가되는 컬럼 ---
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    team = Column(String, nullable=True)
    # -------------------------

    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    club = relationship("ClubDB", back_populates="operation_logs")
    author = relationship("UserDB", back_populates="operation_logs")
    files = relationship("UploadedFileDB", back_populates="operation_log", cascade="all, delete-orphan")

class UploadedFileDB(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String)
    operation_log_id = Column(Integer, ForeignKey("operation_logs.id"))

    operation_log = relationship("OperationLogDB", back_populates="files")