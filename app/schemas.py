from pydantic import BaseModel
from typing import Optional

# Pydantic 모델을 사용하여 API의 데이터 형태를 정의합니다.
# 이 모델들은 데이터의 유효성 검사, 자동 문서화 등에 사용됩니다.

# 1. 동아리 '생성' 시 클라이언트가 보내야 할 데이터 형태
# 기능 명세서의 "동아리 정보"에 해당합니다. 
class GroupCreate(BaseModel):
    name: str
    group_type: str
    topic: str
    description: Optional[str] = None # 설명은 선택사항일 수 있으므로 Optional
    password: str

# 2. 동아리 '참여' 시 클라이언트가 보내야 할 데이터 형태
# 기능 명세서의 "동아리 비밀번호 4자리"에 해당합니다. 
class GroupJoin(BaseModel):
    name: str # 참여할 동아리 이름
    password: str

# 3. 클라이언트에게 '응답'으로 보내줄 기본 동아리 정보 형태
# 보안상, 클라이언트에게 동아리의 비밀번호를 다시 보내주는 일은 없어야 합니다.
# 그래서 여기에는 `password` 필드가 없습니다.
class Group(BaseModel):
    id: int
    name: str
    group_type: str
    topic: str
    description: Optional[str] = None

    # 이 설정을 통해 SQLAlchemy 모델(models.py의 Group)을
    # Pydantic 모델로 자동으로 변환할 수 있게 됩니다.
    class Config:
        orm_mode = True