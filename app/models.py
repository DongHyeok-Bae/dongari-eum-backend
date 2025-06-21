from sqlalchemy import Column, Integer, String
from .database import Base # 방금 만든 database.py에서 Base를 가져옵니다.

# 'groups'라는 이름의 테이블에 매핑될 Group 클래스
class Group(Base):
    __tablename__ = "groups"

    # 테이블의 컬럼(속성)들을 정의합니다.
    id = Column(Integer, primary_key=True, index=True) # 자동 생성될 고유 ID
    name = Column(String, unique=True, index=True) # 동아리 이름 
    group_type = Column(String) # 동아리 유형 
    topic = Column(String)      # 동아리 주제 
    description = Column(String, nullable=True) # 동아리 설명 
    password = Column(String(4)) # 4자리 비밀번호
    image_url = Column(String, nullable=True)