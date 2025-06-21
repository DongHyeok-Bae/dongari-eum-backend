from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# 우리가 직접 만든 .py 파일들에서 필요한 것들을 가져옵니다.
from . import models, schemas
from .database import SessionLocal, engine

# 1. 데이터베이스 테이블 생성
# 앱이 시작될 때, models.py에서 정의한 모든 테이블을 데이터베이스에 생성합니다.
# (이미 존재하면 아무 동작도 하지 않습니다.)
models.Base.metadata.create_all(bind=engine)

# 2. FastAPI 앱 인스턴스 생성
app = FastAPI()
# --- CORS 미들웨어 설정 시작 ---
# 허용할 출처(프론트엔드 주소) 목록
origins = [
    "http://localhost:3000", # 로컬 개발 환경
    "*"  # 나중에 Netlify 배포 주소를 여기에 추가하거나, 지금은 모든 주소를 허용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 모든 HTTP 메소드 허용
    allow_headers=["*"], # 모든 HTTP 헤더 허용
)
# --- CORS 미들웨어 설정 끝 ---


# 3. 데이터베이스 세션을 가져오는 의존성 함수
# API 요청이 들어올 때마다 DB 세션을 생성하고, 요청 처리가 끝나면 세션을 닫습니다.
# 이를 통해 데이터베이스 연결을 안전하고 효율적으로 관리할 수 있습니다.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API 엔드포인트 구현 ---

@app.get("/")
def read_root():
    return {"message": "동아리음 백엔드 서버입니다."}

# 동아리 생성 API
@app.post("/groups/", response_model=schemas.Group, tags=["Groups"])
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    """
    새로운 동아리를 생성합니다.

    - **name**: 동아리 이름 (고유해야 함)
    - **group_type**: 동아리 유형
    - **topic**: 동아리 주제
    - **description**: 동아리 설명 (선택)
    - **password**: 4자리 숫자 비밀번호
    """
    # 이미 같은 이름의 동아리가 있는지 확인
    db_group = db.query(models.Group).filter(models.Group.name == group.name).first()
    if db_group:
        raise HTTPException(status_code=400, detail="이미 존재하는 동아리 이름입니다.")
    
    # 비밀번호가 4자리 숫자인지 검증
    if not (group.password.isdigit() and len(group.password) == 4):
        raise HTTPException(status_code=400, detail="비밀번호는 4자리 숫자여야 합니다.")

    # 새 동아리 객체를 만들고 데이터베이스에 추가
    new_group = models.Group(**group.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    # TODO: 생성한 유저를 해당 동아리의 '관리자'로 자동 등록하는 로직 추가 필요
    return new_group

# 동아리 검색 API
@app.get("/groups/search/", response_model=List[schemas.Group], tags=["Groups"])
def search_group(name: str, db: Session = Depends(get_db)):
    """
    이름에 포함된 키워드로 동아리를 검색합니다.
    """
    if not name.strip():
         raise HTTPException(status_code=400, detail="검색할 동아리 이름을 입력해주세요.")
    groups = db.query(models.Group).filter(models.Group.name.contains(name)).all()
    return groups

# [수정됨] 동아리 참여 API
@app.post("/groups/join/", tags=["Groups"])
def join_group(join_request: schemas.GroupJoin, db: Session = Depends(get_db)):
    """
    이름과 비밀번호로 특정 동아리에 참여합니다.
    """
    # 요청받은 이름으로 동아리를 찾습니다.
    db_group = db.query(models.Group).filter(models.Group.name == join_request.name).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="존재하지 않는 동아리입니다.")

    # 비밀번호 일치 여부 확인
    if db_group.password != join_request.password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    # TODO: 현재 로그인한 사용자를 해당 동아리의 '멤버'로 등록하는 로직 추가 필요
    return {"detail": "동아리 참여에 성공했습니다."}