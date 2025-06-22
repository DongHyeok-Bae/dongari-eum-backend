from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 우리가 직접 만든 .py 파일들에서 필요한 것들을 가져옵니다.
from . import models
from .database import engine, Base
from .routers import clubs, auth, members, accounting, operation_logs

# 1. 데이터베이스 테이블 생성
# 앱이 시작될 때, models.py에서 정의한 모든 테이블을 데이터베이스에 생성합니다.
# (이미 존재하면 아무 동작도 하지 않습니다.)
Base.metadata.create_all(bind=engine)

# 2. FastAPI 앱 인스턴스 생성
app = FastAPI()

# /routers/ 디렉터리의 각 파일에 정의된 API 엔드포인트들을 앱에 포함시킵니다.
app.include_router(clubs.router)
app.include_router(auth.router)
app.include_router(members.router)
app.include_router(accounting.router)
app.include_router(operation_logs.router)

# static 디렉토리를 /static 경로에 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

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

# --- API 엔드포인트 구현 ---

@app.get("/")
def read_root():
    return {"message": "동아리음 백엔드 서버입니다."}

# [삭제] 동아리 생성 API (routers/groups.py로 이동)
# [삭제] 동아리 검색 API (routers/groups.py로 이동)
# [삭제] 동아리 참여 API (routers/groups.py로 이동)