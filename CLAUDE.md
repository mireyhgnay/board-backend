# Board Backend - CLAUDE.md

> Claude Code가 이 프로젝트에서 일관되게 작업할 수 있도록 하는 가이드입니다.
> 이 프로젝트는 **프론트엔드 개발자가 백엔드를 학습**하기 위한 목적으로 만들어졌습니다.

---

## 프로젝트 개요

**게시판 백엔드 API 서버**

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.11+ |
| 프레임워크 | FastAPI |
| 서버 | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| DB | Supabase (PostgreSQL 기반 클라우드 DB) |
| DB 드라이버 | psycopg2-binary |
| 마이그레이션 | Alembic |

---

## 폴더 구조 & 각 파일의 역할

```
board-backend/
├── app/                         # 메인 애플리케이션 코드
│   ├── main.py                  # FastAPI 앱 생성 & 설정 (진입점)
│   │
│   ├── core/                    # 앱 핵심 설정 (변경 빈도 낮음)
│   │   ├── config.py            # 환경 변수 관리 (pydantic-settings)
│   │   └── database.py          # DB 엔진, 세션, Base 설정
│   │
│   ├── models/                  # SQLAlchemy ORM 모델 (DB 테이블 정의)
│   │   ├── __init__.py          # ⚠️ 새 모델 추가 시 반드시 여기에 import
│   │   └── base.py              # 공통 필드 (id, created_at, updated_at)
│   │
│   ├── schemas/                 # Pydantic 스키마 (API 요청/응답 형식 정의)
│   │   ├── __init__.py
│   │   └── common.py            # 공통 응답 구조 (BaseResponse, PaginatedResponse)
│   │
│   ├── api/                     # API 엔드포인트 (라우터)
│   │   └── v1/
│   │       ├── router.py        # v1 라우터 통합 (새 라우터는 여기에 등록)
│   │       ├── posts.py         # (추후) 게시글 API
│   │       └── comments.py      # (추후) 댓글 API
│   │
│   ├── services/                # 비즈니스 로직 (핵심 처리 로직)
│   │   └── post_service.py      # (추후) 게시글 로직
│   │
│   ├── repositories/            # 데이터 접근 레이어 (DB CRUD)
│   │   └── post_repository.py   # (추후) Post CRUD
│   │
│   └── dependencies/            # FastAPI 의존성 주입
│       └── __init__.py
│
├── alembic/                     # DB 마이그레이션
│   ├── env.py                   # Alembic 환경 설정 (⚠️ 모델 import 필수)
│   └── versions/                # 마이그레이션 파일 자동 생성 위치
│
├── tests/                       # 테스트
│   ├── conftest.py              # 공통 픽스처 (테스트 DB, 클라이언트)
│   └── test_posts.py            # (추후) 게시글 테스트
│
├── .env                         # 환경 변수 (git 제외 - 직접 생성 필요)
├── .env.example                 # 환경 변수 예시 (git 포함)
├── .gitignore
├── alembic.ini                  # Alembic 설정
├── requirements.txt             # Python 패키지 목록
└── CLAUDE.md                    # 이 파일
```

---

## 아키텍처: 계층 구조 (Layered Architecture)

```
HTTP 요청
    ↓
[Router / API Layer]     → HTTP 요청/응답 처리만 담당
    ↓
[Service Layer]          → 비즈니스 로직 (규칙, 계산, 검증)
    ↓
[Repository Layer]       → DB CRUD만 담당 (SQL 쿼리)
    ↓
[Database (MySQL)]
```

각 레이어는 바로 아래 레이어만 호출합니다. Router → Repository 직접 호출은 금지.

---

## 개발 규칙 & 컨벤션

### 필수 규칙

1. **모든 주석은 한국어로** 작성한다 (학습 목적)
2. **새 기능마다 주석 필수**: 함수, 클래스, 중요 로직에 `"""docstring"""` 또는 `#` 주석
3. **왜(Why)를 설명**: 단순히 "무엇을" 하는지가 아닌 "왜" 이렇게 했는지 설명
4. **계층 분리 준수**: Router는 Service를, Service는 Repository를 호출

### 새 기능 추가 순서

```
1. models/      → DB 테이블 정의 (SQLAlchemy 모델)
2. models/__init__.py → 새 모델 import 추가
3. alembic 마이그레이션 실행
4. schemas/     → API 요청/응답 스키마 (Pydantic)
5. repositories/ → DB CRUD 함수
6. services/    → 비즈니스 로직
7. api/v1/      → API 엔드포인트 (라우터)
8. api/v1/router.py → 새 라우터 등록
```

### 코드 스타일

- **함수명**: snake_case (예: `get_user_by_id`)
- **클래스명**: PascalCase (예: `UserService`)
- **상수명**: UPPER_SNAKE_CASE (예: `MAX_RETRY_COUNT`)
- **파일명**: snake_case (예: `user_service.py`)
- **라인 길이**: 최대 100자

### 스키마 네이밍

```python
PostBase      # 공통 필드
PostCreate    # 생성 요청 데이터
PostUpdate    # 수정 요청 데이터 (Optional 필드)
PostResponse  # 응답 데이터
```

---

## 환경 설정 방법

### 1단계: Supabase 프로젝트 준비
1. https://supabase.com 에서 무료 계정 생성
2. "New project" 클릭 → 프로젝트 이름 & DB 비밀번호 설정
3. 프로젝트 생성 완료 후 → Settings → Database → Connection string → URI 복사

### 2단계: 로컬 개발 환경 셋업
Python 3.13이 전역 설치되어 있고 패키지도 전역으로 설치합니다. (가상환경 사용 안 함)

```bash
# 1. 패키지 설치 (최초 1회만)
pip3 install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 DATABASE_URL에 Supabase URI 붙여넣기

# 3. DB 마이그레이션 실행 (Supabase에 테이블 생성)
alembic upgrade head

# 4. 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 배포 구조 (Vercel 프론트 + 클라우드 백엔드)
```
[브라우저]
    ↓ HTTPS
[Vercel] - 프론트엔드 (Next.js / React)
    ↓ API 호출 (HTTPS)
[Railway or Render] - FastAPI 백엔드 서버
    ↓ PostgreSQL 연결
[Supabase] - 데이터베이스
```

백엔드 배포 추천:
- **Railway** (https://railway.app): GitHub 연동 자동 배포, 무료 플랜 있음
- **Render** (https://render.com): 무료 플랜 있음 (슬립 모드 주의)

배포 시 환경 변수를 각 서비스의 대시보드에서 설정해야 합니다.

---

## 마이그레이션 가이드

```bash
# 모델 변경 후 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "변경사항 설명"

# 마이그레이션 적용
alembic upgrade head

# 이전 버전으로 롤백
alembic downgrade -1

# 현재 상태 확인
alembic current

# 이력 확인
alembic history
```

⚠️ **중요**: 모델을 추가하면 `alembic/env.py`에 반드시 import 해야 합니다.

---

## API 응답 형식

모든 API는 일관된 응답 구조를 사용합니다 (`app/schemas/common.py` 참고):

```json
// 성공 (단건)
{
  "success": true,
  "message": "조회 성공",
  "data": { ... }
}

// 성공 (목록 + 페이지네이션)
{
  "success": true,
  "message": "조회 성공",
  "data": [ ... ],
  "total": 100,
  "page": 1,
  "size": 10,
  "total_pages": 10
}

// 실패
{
  "success": false,
  "message": "이미 사용 중인 이메일입니다.",
  "error_code": "EMAIL_ALREADY_EXISTS"
}
```

---

## 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 특정 파일 테스트
pytest tests/test_posts.py -v

# 커버리지 확인
pytest tests/ --cov=app
```

---

## 주요 URL

서버 실행 후 접속 가능:

| URL | 설명 |
|-----|------|
| `http://localhost:8000` | API 서버 루트 |
| `http://localhost:8000/docs` | Swagger UI (API 문서 & 테스트) |
| `http://localhost:8000/redoc` | ReDoc (API 문서) |
| `http://localhost:8000/api/v1/health` | 헬스체크 |

---

## Claude에게 요청 시 참고사항

- 이 프로젝트는 **학습 목적**이므로 주석을 상세하게 작성해주세요
- 새 기능 추가 시 **위의 계층 분리 규칙을 반드시 지켜주세요**
- 모든 주석과 docstring은 **한국어**로 작성해주세요
- **백엔드 개념 설명**을 코드 주석에 포함해주세요 (왜 이렇게 하는지)
- 새 모델 추가 시 `models/__init__.py`와 `alembic/env.py` import 업데이트를 잊지 마세요
