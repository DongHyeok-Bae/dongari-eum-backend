from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 데이터베이스 파일 경로 설정 (SQLite 사용)
SQLALCHEMY_DATABASE_URL = "sqlite:///./dongari.db"

# 2. 데이터베이스 엔진 생성
# connect_args는 SQLite를 사용할 때만 필요한 설정입니다. (쓰레드 관련)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. 데이터베이스와 통신을 위한 세션(Session) 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 모델 클래스들이 상속받을 Base 클래스 생성
Base = declarative_base()

# 5. [추가] 데이터베이스 세션을 가져오는 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()