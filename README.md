# Board Backend

게시판 서비스의 백엔드 API 서버입니다.

## 기술 스택

| 분류 | 기술 | 버전 |
|------|------|------|
| 언어 | Python | 3.11+ |
| 웹 프레임워크 | FastAPI | 0.115.6 |
| ASGI 서버 | Uvicorn | 0.34.0 |
| ORM | SQLAlchemy | 2.0.37 |
| DB 마이그레이션 | Alembic | 1.14.1 |
| 데이터베이스 | Supabase (PostgreSQL) | - |
| DB 드라이버 | psycopg2-binary | 2.9.11 |
| 데이터 검증 | Pydantic | 2.10.4 |

## 폴더 구조

```
board-backend/
├── app/
│   ├── main.py                  # FastAPI 앱 진입점
│   ├── core/
│   │   ├── config.py            # 환경 변수 관리
│   │   ├── database.py          # DB 엔진 & 세션 설정
│   ├── models/                  # SQLAlchemy ORM 모델 (DB 테이블 정의)
│   ├── schemas/                 # Pydantic 스키마 (API 요청/응답 형식)
│   ├── api/
│   │   └── v1/                  # API v1 엔드포인트
│   ├── services/                # 비즈니스 로직
│   ├── repositories/            # DB CRUD 레이어
│   └── dependencies/            # FastAPI 의존성 주입
├── alembic/                     # DB 마이그레이션
├── tests/                       # 테스트
├── .env.example                 # 환경 변수 예시
├── alembic.ini                  # Alembic 설정
└── requirements.txt             # 패키지 목록
```

## 아키텍처

계층 분리 구조를 따릅니다. 각 레이어는 바로 아래 레이어만 호출합니다.

```
HTTP 요청
    ↓
API Layer (Router)    — HTTP 요청/응답 처리
    ↓
Service Layer         — 비즈니스 로직
    ↓
Repository Layer      — DB CRUD
    ↓
Database (Supabase)
```

---

## 초기 셋업 가이드

### 1. Supabase 프로젝트 생성

1. [https://supabase.com](https://supabase.com) 에서 무료 계정 생성
2. **New project** 클릭 → 프로젝트 이름 & DB 비밀번호 설정
3. 프로젝트 생성 완료 후 → 좌측 메뉴 **Connect** 버튼 클릭
4. **Session Pooler** 탭의 URI 복사 (포트 5432)

> ⚠️ Direct connection (`db.xxx.supabase.co`) 은 Supabase 정책 변경으로 사용 불가합니다.
> **Session Pooler** URL을 사용해야 합니다.

### 2. 프로젝트 클론 & 패키지 설치

```bash
git clone <repo-url>
pip3 install -r requirements.txt
```

> Python 3.11 이상이 설치되어 있어야 합니다.

### 3. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값들을 수정합니다.

```env
# Supabase에서 복사한 Session Pooler URI
DATABASE_URL=postgresql://postgres.프로젝트ID:비밀번호@aws-0-리전.pooler.supabase.com:5432/postgres
```

### 4. DB 마이그레이션

Supabase에 테이블을 생성합니다.

```bash
alembic upgrade head
```

### 5. 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 아래 URL에서 확인할 수 있습니다.

| URL | 설명 |
|-----|------|
| http://localhost:8000/docs | Swagger UI (API 문서 & 테스트) |
| http://localhost:8000/redoc | ReDoc (API 문서) |
| http://localhost:8000/api/v1/health | 헬스체크 |

---

## 마이그레이션 명령어

```bash
# 모델 변경 후 마이그레이션 파일 생성
alembic revision --autogenerate -m "변경사항 설명"

# 마이그레이션 적용
alembic upgrade head

# 이전 버전으로 롤백
alembic downgrade -1

# 현재 상태 확인
alembic current
```

## 테스트 실행

```bash
pytest tests/ -v
```

---

## 배포 구조

```
[브라우저]
    ↓
[Vercel] — 프론트엔드 (Next.js / React)
    ↓ API 호출
[Railway or Render] — FastAPI 백엔드
    ↓
[Supabase] — PostgreSQL 데이터베이스
```

백엔드 배포 추천:
- **Railway** ([railway.app](https://railway.app)): GitHub 연동 자동 배포
- **Render** ([render.com](https://render.com)): 무료 플랜 (슬립 모드 주의)

배포 시 각 서비스 대시보드에서 `.env`와 동일한 환경 변수를 설정해야 합니다.
