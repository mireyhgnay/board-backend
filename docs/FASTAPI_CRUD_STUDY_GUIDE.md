# FastAPI CRUD 핵심 학습 가이드

> 프론트엔드 개발자가 백엔드를 이해하기 위해 **꼭 알아야 할 것**만 정리했습니다.
> 이 프로젝트(board-backend)의 실제 코드를 예시로 사용합니다.

---

## 목차

1. [전체 그림: 프론트 vs 백엔드](#1-전체-그림-프론트-vs-백엔드)
2. [FastAPI 기본 구조](#2-fastapi-기본-구조)
3. [계층 구조 (Layered Architecture)](#3-계층-구조-layered-architecture)
4. [CRUD 핵심 5가지](#4-crud-핵심-5가지)
5. [데이터 흐름 한눈에 보기](#5-데이터-흐름-한눈에-보기)
6. [학습 로드맵](#6-학습-로드맵)

---

## 1. 전체 그림: 프론트 vs 백엔드

프론트엔드 개념과 1:1 대응시켜서 이해하면 빠릅니다.

| 프론트엔드 (React/Next.js) | 백엔드 (FastAPI) | 설명 |
|---|---|---|
| `fetch('/api/posts')` | `@router.get("/posts")` | 요청을 보내는 쪽 vs 받는 쪽 |
| TypeScript interface | Pydantic schema | 데이터 형태(타입) 정의 |
| Zod / yup validation | Pydantic Field 검증 | 입력값 유효성 검사 |
| React state | DB 테이블 (SQLAlchemy model) | 데이터 저장소 |
| `useEffect` 에서 API 호출 | Router 함수가 요청 처리 | 이벤트 → 액션 |
| Next.js API Routes | FastAPI Router | 엔드포인트 정의 |
| `.env.local` | `.env` + `pydantic-settings` | 환경변수 관리 |

**핵심 포인트**: 프론트에서 `fetch`로 보내는 요청을 백엔드에서 "받아서 처리하고 응답"하는 것이 전부입니다.

---

## 2. FastAPI 기본 구조

### 앱 진입점 (`app/main.py`)

```
FastAPI()로 앱 생성 → 미들웨어 설정 → 라우터 연결
```

프론트의 `next.config.js` + `app/layout.tsx`와 비슷한 역할입니다.

**꼭 알아야 할 것:**
- `FastAPI()` — 앱 인스턴스 생성 (Next.js의 `createApp`같은 것)
- `app.add_middleware(CORSMiddleware, ...)` — 프론트에서 API 호출 시 CORS 허용
- `app.include_router(router)` — URL 라우팅 등록

### CORS가 중요한 이유

프론트(`localhost:3000`)에서 백엔드(`localhost:8000`)를 호출하면 **브라우저가 차단**합니다.
`CORSMiddleware`로 허용 도메인을 등록해야 합니다. 프론트 개발 시 겪던 CORS 에러의 해결책이 바로 여기에 있습니다.

---

## 3. 계층 구조 (Layered Architecture)

```
📁 프론트엔드 비유              📁 백엔드 (이 프로젝트)
─────────────────           ─────────────────
pages/api/                  api/v1/posts.py        ← Router (HTTP 처리)
   ↓                           ↓
hooks/usePost.ts            services/post_service.py  ← Service (비즈니스 로직)
   ↓                           ↓
lib/api.ts                  repositories/post_repository.py  ← Repository (DB 접근)
   ↓                           ↓
외부 API 서버               Database (Supabase)
```

### 왜 이렇게 나눌까?

- **Router**: "이 URL로 요청 오면 이 함수 실행해" (Express의 `app.get()`과 동일)
- **Service**: "게시글이 없으면 404 에러" 같은 규칙 처리
- **Repository**: "DB에서 SELECT/INSERT/UPDATE/DELETE" 실제 쿼리

프론트에서 컴포넌트/훅/API유틸을 분리하는 것과 같은 이유입니다: **관심사 분리**.

---

## 4. CRUD 핵심 5가지

### 핵심 ① — 라우터 (Router)

> 📍 파일: `app/api/v1/posts.py`
> 📍 프론트 대응: Next.js API Routes (`pages/api/posts.ts`)

**이것만 기억하세요:**

| HTTP 메서드 | 데코레이터 | 용도 | 프론트 fetch |
|---|---|---|---|
| GET | `@router.get("/posts")` | 목록 조회 | `fetch('/api/v1/posts')` |
| GET | `@router.get("/posts/{post_id}")` | 단건 조회 | `fetch('/api/v1/posts/1')` |
| POST | `@router.post("/posts")` | 생성 | `fetch('/api/v1/posts', {method:'POST', body:...})` |
| PUT | `@router.put("/posts/{post_id}")` | 수정 | `fetch('/api/v1/posts/1', {method:'PUT', body:...})` |
| DELETE | `@router.delete("/posts/{post_id}")` | 삭제 | `fetch('/api/v1/posts/1', {method:'DELETE'})` |

**공부 포인트:**

```python
# 경로 파라미터 — URL에서 값 추출 (프론트의 params.id와 동일)
@router.get("/{post_id}")
def get_post(post_id: int = Path(..., ge=1)):
    ...

# 쿼리 파라미터 — ?page=1&size=10 (프론트의 searchParams와 동일)
@router.get("/")
def get_posts(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    ...

# 요청 바디 — JSON 데이터 수신 (프론트에서 body로 보내는 것)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    ...
```

---

### 핵심 ② — 스키마 (Pydantic)

> 📍 파일: `app/schemas/post.py`
> 📍 프론트 대응: TypeScript interface + Zod 유효성 검증

**TypeScript와 비교:**

```typescript
// 프론트: TypeScript interface
interface PostCreate {
  title: string;   // 필수, 1~200자
  content: string; // 필수
}

interface PostResponse {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}
```

```python
# 백엔드: Pydantic schema (같은 역할!)
class PostCreate(PostBase):
    # title: str = Field(min_length=1, max_length=200)  ← PostBase에서 상속
    # content: str = Field(min_length=1)                 ← PostBase에서 상속
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}  # SQLAlchemy 객체 → JSON 변환 허용
```

**공부 포인트:**
- `Field(min_length=1, max_length=200)` — Zod의 `.min(1).max(200)`과 동일
- `Optional[str]` — TypeScript의 `title?: string`과 동일
- `model_config = {"from_attributes": True}` — DB 모델 → 응답 JSON 자동 변환
- `model_dump(exclude_unset=True)` — 보내지 않은 필드는 제외 (PATCH 업데이트용)

---

### 핵심 ③ — ORM 모델 (SQLAlchemy)

> 📍 파일: `app/models/post.py`
> 📍 프론트 대응: DB 스키마 (Prisma schema / Supabase 테이블 정의)

```python
class Post(BaseModel):
    __tablename__ = "posts"  # 실제 DB 테이블 이름

    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    # id, created_at, updated_at는 BaseModel에서 상속
```

**프론트 개발자를 위한 핵심 개념:**

| SQLAlchemy | Prisma (프론트에서 접했을 수 있는 것) | SQL |
|---|---|---|
| `Column(String(200))` | `String @db.VarChar(200)` | `VARCHAR(200)` |
| `Column(Text)` | `String` | `TEXT` |
| `nullable=False` | 필드에 `?` 없음 | `NOT NULL` |
| `index=True` | `@@index` | `CREATE INDEX` |

**공부 포인트:**
- ORM = "SQL을 Python 코드로 작성하는 것" (SQL 몰라도 DB 조작 가능)
- 모델 변경 → Alembic 마이그레이션 필수 (Prisma migrate와 동일한 개념)

---

### 핵심 ④ — Repository (DB CRUD 함수)

> 📍 파일: `app/repositories/post_repository.py`
> 📍 프론트 대응: `lib/api.ts`의 fetch 함수들

**CRUD 작업별 SQLAlchemy 패턴:**

```python
# CREATE — INSERT INTO posts VALUES (...)
def create_post(db, post_data):
    new_post = Post(**post_data.model_dump())  # 스키마 → 모델 변환
    db.add(new_post)       # DB 세션에 추가 (아직 저장 안 됨)
    db.commit()            # 실제 DB에 저장 (git commit과 비슷)
    db.refresh(new_post)   # DB에서 자동생성된 id, created_at 등을 다시 읽어옴
    return new_post

# READ (목록) — SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 0
def get_posts(db, skip, limit):
    return db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

# READ (단건) — SELECT * FROM posts WHERE id = 1
def get_post_by_id(db, post_id):
    return db.query(Post).filter(Post.id == post_id).first()

# UPDATE — UPDATE posts SET title='새제목' WHERE id = 1
def update_post(db, post, update_data):
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(post, key, value)  # 동적으로 속성 업데이트
    db.commit()
    db.refresh(post)
    return post

# DELETE — DELETE FROM posts WHERE id = 1
def delete_post(db, post):
    db.delete(post)
    db.commit()
```

**공부 포인트:**
- `db.add()` → `db.commit()` → `db.refresh()` 3단계 흐름
- `db.query(Model).filter().first()` — 기본 조회 패턴
- `exclude_unset=True` — 프론트에서 안 보낸 필드는 건드리지 않음 (부분 수정)

---

### 핵심 ⑤ — 의존성 주입 (Dependency Injection)

> 📍 파일: `app/core/database.py`의 `get_db()`
> 📍 프론트 대응: React Context / Provider 패턴

```python
# DB 세션을 자동으로 만들고 → 사용하고 → 닫아주는 함수
def get_db():
    db = SessionLocal()  # DB 연결 열기
    try:
        yield db         # 라우터 함수에 db 전달
    except Exception:
        db.rollback()    # 에러 나면 되돌리기
    finally:
        db.close()       # 항상 연결 닫기

# 사용하는 쪽 — Depends()로 자동 주입
@router.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # db를 직접 생성하지 않아도 자동으로 주입됨!
    ...
```

**프론트 비유:**

```tsx
// React Context와 비슷한 개념
// Provider가 값을 제공하고, useContext로 가져다 쓰는 것처럼
// get_db가 세션을 제공하고, Depends(get_db)로 가져다 씀

const db = useContext(DatabaseContext);  // ≈ db: Session = Depends(get_db)
```

**공부 포인트:**
- `Depends()` — FastAPI가 함수 호출 시 자동으로 필요한 것을 넣어줌
- `yield` — `try/finally`와 함께 써서 리소스를 안전하게 관리
- 프론트의 `useContext` 같은 것이라고 이해하면 됨

---

## 5. 데이터 흐름 한눈에 보기

### 게시글 생성 (POST) 전체 흐름

```
[프론트엔드]
fetch('/api/v1/posts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title: '제목', content: '내용' })
})
    │
    ▼
[Router] app/api/v1/posts.py
    │  post_data: PostCreate  ← JSON을 Pydantic이 자동 파싱 & 검증
    │  db: Session             ← Depends(get_db)가 자동 주입
    ▼
[Service] app/services/post_service.py
    │  비즈니스 로직 처리 (현재는 단순 위임)
    ▼
[Repository] app/repositories/post_repository.py
    │  Post 모델 생성 → db.add → db.commit → db.refresh
    ▼
[Database] Supabase (PostgreSQL)
    │  INSERT INTO posts (title, content) VALUES ('제목', '내용')
    ▼
[응답] → JSON으로 변환 → 프론트엔드에 전달
{
  "success": true,
  "message": "게시글이 생성되었습니다",
  "data": { "id": 1, "title": "제목", "content": "내용", ... }
}
```

### 게시글 목록 조회 + 페이지네이션

```
[프론트] fetch('/api/v1/posts?page=2&size=10')
    │
    ▼
[Router] page=2, size=10 을 Query 파라미터로 받음
    ▼
[Service] skip = (2-1) * 10 = 10  ← 10개 건너뛰고
          limit = 10                ← 10개 가져와
          total_pages = (전체개수 + 10 - 1) // 10
    ▼
[Repository] db.query(Post).offset(10).limit(10).all()
    ▼
[응답]
{
  "success": true,
  "data": [...10개 게시글...],
  "total": 35,
  "page": 2,
  "size": 10,
  "total_pages": 4
}
```

---

## 6. 학습 로드맵

### Phase 1: 코드 읽기 (1~2일)

아래 순서대로 파일을 읽으면서 주석을 따라가세요.

| 순서 | 파일 | 핵심 질문 |
|---|---|---|
| 1 | `app/schemas/post.py` | "프론트의 TypeScript interface와 뭐가 다르지?" |
| 2 | `app/models/post.py` | "DB 테이블이 코드로 어떻게 정의되지?" |
| 3 | `app/repositories/post_repository.py` | "CRUD가 SQL 없이 어떻게 동작하지?" |
| 4 | `app/services/post_service.py` | "비즈니스 로직이란 뭐지? 왜 분리하지?" |
| 5 | `app/api/v1/posts.py` | "프론트에서 보내는 요청을 어떻게 받지?" |
| 6 | `app/core/database.py` | "DB 연결은 어떻게 관리되지?" |

### Phase 2: Swagger UI로 실험 (1일)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000/docs 접속
```

1. Swagger UI에서 POST로 게시글 3개 생성
2. GET으로 목록 조회 (page, size 파라미터 바꿔보기)
3. PUT으로 제목만 수정 (content 안 보내도 되는지 확인)
4. DELETE로 삭제 후 다시 GET으로 확인

### Phase 3: 프론트엔드 연동 (1~2일)

실제 프론트에서 이 API를 호출해보세요.

```typescript
// 예시: Next.js에서 게시글 목록 가져오기
const res = await fetch('http://localhost:8000/api/v1/posts?page=1&size=10');
const data = await res.json();
// data.data → 게시글 배열
// data.total_pages → 전체 페이지 수
```

### Phase 4: 직접 만들어보기 (2~3일)

댓글(Comment) 기능을 직접 구현해보세요. 순서:

1. `app/models/comment.py` — Comment 모델 (post_id 외래키 포함)
2. `app/models/__init__.py` — import 추가
3. `alembic revision --autogenerate -m "add comments table"` → `alembic upgrade head`
4. `app/schemas/comment.py` — CommentCreate, CommentResponse
5. `app/repositories/comment_repository.py` — CRUD 함수
6. `app/services/comment_service.py` — 비즈니스 로직
7. `app/api/v1/comments.py` — 라우터
8. `app/api/v1/router.py` — 라우터 등록

---

## 부록: 자주 쓰는 FastAPI 패턴 요약

### 패턴 1: 경로 파라미터

```python
# URL: /posts/42
@router.get("/{post_id}")
def get(post_id: int = Path(..., ge=1)):  # ge=1: 1 이상만 허용
    ...
```

### 패턴 2: 쿼리 파라미터

```python
# URL: /posts?page=1&size=20
@router.get("/")
def list(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    ...
```

### 패턴 3: 요청 바디

```python
# JSON Body: {"title": "제목", "content": "내용"}
@router.post("/")
def create(post_data: PostCreate):  # Pydantic이 자동으로 파싱 + 검증
    ...
```

### 패턴 4: 응답 코드 지정

```python
@router.post("/", status_code=status.HTTP_201_CREATED)   # 생성 성공
@router.delete("/{id}", status_code=status.HTTP_200_OK)   # 삭제 성공
# 에러 시: raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
```

### 패턴 5: 의존성 주입

```python
@router.get("/")
def get_posts(db: Session = Depends(get_db)):  # 자동으로 DB 세션 주입
    ...
```

---

## 한줄 요약

> **FastAPI CRUD = 라우터(URL 매핑) + 스키마(데이터 검증) + 모델(DB 테이블) + 리포지토리(DB 조작) + 의존성 주입(자동 연결)**

프론트에서 `fetch` → 백엔드 `Router` → `Service` → `Repository` → `DB` → 응답 JSON → 프론트에서 사용.
이 흐름 하나만 완벽히 이해하면 백엔드의 80%를 이해한 겁니다.
