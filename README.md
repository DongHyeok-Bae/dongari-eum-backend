# 동아리음 (Dongari-eum) 백엔드 서버

'동아리음' 웹 애플리케이션의 백엔드 서버입니다. 동아리 정보 관리, 회원 관리, 회계 및 활동 기록 관리 등 핵심 비즈니스 로직과 데이터베이스를 처리합니다.

## 🚀 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Schema Validation**: Pydantic
- **Web Server**: Uvicorn

## 📂 프로젝트 구조

```
dongari-eum-backend/
├── app/                  # 핵심 애플리케이션 로직
│   ├── routers/          # API 엔드포인트 정의 (라우팅)
│   ├── services/         # 비즈니스 로직 처리
│   ├── models.py         # 데이터베이스 테이블 모델 (SQLAlchemy)
│   ├── schemas.py        # 데이터 유효성 검사 모델 (Pydantic)
│   ├── database.py       # 데이터베이스 연결 및 세션 관리
│   ├── auth.py           # 인증 관련 유틸리티
│   └── main.py           # FastAPI 앱 진입점 및 미들웨어 설정
├── static/               # 정적 파일 (이미지, 첨부파일 등)
│   ├── images/
│   └── files/
├── dongari.db            # SQLite 데이터베이스 파일
├── requirements.txt      # 프로젝트 의존성 패키지 목록
└── README.md             # 프로젝트 설명서
```

## ⚙️ 설치 및 실행 방법

1.  **가상환경 생성 및 활성화**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate  # Windows
    ```

2.  **의존성 패키지 설치**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uvicorn 서버 실행**
    `dongari-eum-backend` 디렉터리 내에서 다음 명령어를 실행합니다. `--reload` 옵션은 코드 변경 시 서버를 자동으로 재시작해줍니다.
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

4.  **API 문서 확인**
    서버가 실행되면, 다음 주소에서 자동 생성된 API 문서를 확인할 수 있습니다.
    - **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    - **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 🔗 API 명세

> 모든 API는 `/docs` 에서 확인하고 직접 테스트할 수 있습니다. 각 API 호출은 인증이 필요한 경우 `Authorization: Bearer <TOKEN>` 헤더를 포함해야 합니다.

---

### **Authentication**
-   **Prefix**: `/auth`

| Method | Path              | 설명                          | 요청 (Body / Form)             | 성공 응답 (2xx)                         |
| :----- | :---------------- | :---------------------------- | :--------------------------- | :-------------------------------------- |
| `POST` | `/signup`         | 새로운 사용자를 생성(회원가입)합니다. | **Body**: `email`, `password`, `first_name` 등 | `201` `User` 객체                     |
| `POST` | `/token`          | 로그인 후 액세스 토큰을 발급합니다.  | **Form**: `username` (email), `password` | `200` `{"access_token": "...", "token_type": "bearer"}` |
| `GET`  | `/users/me`       | 현재 로그인된 사용자 정보를 반환합니다. | (없음)                       | `200` `User` 객체                     |

---

### **Clubs**
-   **Prefix**: `/clubs`

| Method | Path              | 설명                          | 파라미터 / 요청 (Body / Form)           | 성공 응답 (2xx)                         |
| :----- | :---------------- | :---------------------------- | :----------------------------- | :-------------------------------------- |
| `POST` | `/`               | 신규 동아리를 생성합니다.         | **Form**: `name`, `club_type`, `topic`, `password`, `description` (선택), `file` (선택) | `200` `Club` 객체                     |
| `GET`  | `/`               | 동아리 목록을 조회/검색합니다.     | **Query**: `name: str` (선택)    | `200` `List[Club]` 객체               |
| `POST` | `/join`           | 동아리에 가입합니다.              | **Body**: `name`, `password` | `200` `{"message": "...", "club_id": ...}` |
| `GET`  | `/{club_id}`      | 특정 동아리 정보를 조회합니다.      | **Path**: `club_id: int`         | `200` `Club` 객체                     |

---

### **Club Members**
-   **Prefix**: `/clubs/{club_id}/members`

| Method   | Path            | 설명                       | 파라미터 / 요청 (Body)            | 성공 응답 (2xx)           |
| :------- | :-------------- | :------------------------- | :------------------------------ | :------------------------ |
| `POST`   | `/`             | 동아리에 신규 부원을 추가합니다. | **Path**: `club_id: int`<br/>**Body**: `name`, `birth_date`, `student_id` 등 | `200` `ClubMember` 객체 |
| `GET`    | `/`             | 특정 동아리의 부원 목록을 조회합니다. | **Path**: `club_id: int`          | `200` `List[ClubMember]` |
| `PATCH`  | `/{member_id}`  | 부원 정보를 수정합니다.        | **Path**: `club_id: int`, `member_id: int`<br/>**Body**: (수정할 필드들) | `200` `ClubMember` 객체 |
| `DELETE` | `/{member_id}`  | 부원을 삭제합니다.             | **Path**: `club_id: int`, `member_id: int` | `204` No Content        |

---

### **Accounting**
- **Prefix**: `/clubs/{club_id}/accounting`

| Method | Path | 설명 | 파라미터 / 요청 (Form) | 성공 응답 (2xx) |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/` | 신규 회계 내역을 추가합니다. | **Path**: `club_id: int`<br/>**Form**: `date`, `description`, `amount`, `manager` (선택), `photo` (선택) | `200` `AccountingEntry` 객체 |
| `GET` | `/` | 회계 내역을 조회하거나<br/>엑셀 파일로 내보냅니다. | **Path**: `club_id: int`<br/>**Query**: `export: bool` (선택) | `200` `List[AccountingEntry]`<br/>또는 Excel 파일 |

---

### **Operation Logs**
- **Prefix**: `/clubs/{club_id}/operation-logs`

| Method | Path | 설명 | 파라미터 / 요청 (Form) | 성공 응답 (2xx) |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/` | 신규 활동 기록을 추가합니다. | **Path**: `club_id: int`<br/>**Form**: `log_data` (JSON 문자열), `files` (선택) | `200` `OperationLog` 객체 |
| `GET` | `/` | 활동 기록 목록을 조회합니다. | **Path**: `club_id: int` | `200` `List[OperationLog]` |
| `GET` | `/{log_id}` | 특정 활동 기록을 조회합니다. | **Path**: `club_id: int`, `log_id: int` | `200` `OperationLog` 객체 |
