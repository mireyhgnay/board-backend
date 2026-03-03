"""
📌 main.py - FastAPI 애플리케이션 진입점(Entry Point)

【 역할 】
    FastAPI 앱 인스턴스를 생성하고 모든 설정을 적용합니다.
    서버를 실행하면 이 파일이 가장 먼저 실행됩니다.

【 실행 방법 】
    개발 서버 실행:
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

    - uvicorn: Python ASGI 웹 서버 (Node.js의 Express 서버와 비슷한 역할)
    - app.main: app 패키지의 main 모듈
    - :app: main 모듈에서 'app' 변수를 찾아 실행
    - --reload: 코드 변경 시 자동 재시작 (개발 시 편리)
    - --host 0.0.0.0: 모든 IP에서 접근 허용
    - --port 8000: 8000번 포트 사용

【 접속 방법 】
    - API: http://localhost:8000
    - Swagger UI: http://localhost:8000/docs    (API 문서 & 테스트)
    - ReDoc:      http://localhost:8000/redoc   (API 문서 - 읽기 좋은 형식)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import check_db_connection


# ────────────────────────────────────────────────────────────────
# 🚀 앱 시작/종료 이벤트 관리 (Lifespan)
# ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    📌 앱 시작과 종료 시 실행할 코드를 관리합니다.

    yield 이전: 서버 시작 시 실행 (DB 연결 확인, 초기화 등)
    yield 이후: 서버 종료 시 실행 (정리 작업)

    이전 방식(@app.on_event("startup"))은 deprecated(사용 중단 예정)되어
    최신 FastAPI에서는 lifespan 방식을 권장합니다.
    """
    # ── 서버 시작 시 ──
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 시작!")
    print(f"📊 DEBUG 모드: {settings.DEBUG}")

    # Supabase DB 연결 확인
    if check_db_connection():
        print("✅ Supabase DB 연결 성공!")
    else:
        print("❌ Supabase DB 연결 실패! .env 파일의 DATABASE_URL을 확인하세요.")

    yield  # 여기서 앱이 실행됩니다

    # ── 서버 종료 시 ──
    print(f"🛑 {settings.APP_NAME} 종료 중...")


# ────────────────────────────────────────────────────────────────
# 🏗️ FastAPI 앱 인스턴스 생성
# ────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## 게시판 백엔드 API

    FastAPI + SQLAlchemy + Supabase(PostgreSQL)로 구성된 게시판 백엔드 서버입니다.

    ### 주요 기능
    - 🔐 JWT 기반 사용자 인증
    - 📝 게시글 CRUD
    - 💬 댓글 CRUD
    - 👤 사용자 관리
    """,

    # Swagger UI 접속 경로 설정
    docs_url="/docs",      # Swagger UI: http://localhost:8000/docs
    redoc_url="/redoc",    # ReDoc:       http://localhost:8000/redoc

    # 라이프사이클 관리자 연결
    lifespan=lifespan,
)


# ────────────────────────────────────────────────────────────────
# 🌐 CORS 미들웨어 설정
# ────────────────────────────────────────────────────────────────
# 미들웨어: 요청이 처리되기 전/후에 실행되는 코드
# CORS 미들웨어: 다른 출처(origin)에서 오는 요청을 허용/차단
#
# Vercel(프론트) → Railway/Render(백엔드) 통신을 위해 반드시 필요합니다!

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # 허용할 프론트엔드 주소 목록
    allow_credentials=True,                   # 쿠키/인증 헤더 허용
    allow_methods=["*"],                      # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],                      # 모든 헤더 허용
)


# ────────────────────────────────────────────────────────────────
# 📡 라우터 등록
# ────────────────────────────────────────────────────────────────
# prefix="/api/v1": 모든 API URL 앞에 /api/v1 이 붙습니다
# 예: GET /api/v1/health, POST /api/v1/auth/login
app.include_router(api_router, prefix="/api/v1")


# ────────────────────────────────────────────────────────────────
# 🏠 루트 엔드포인트
# ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    """
    📌 API 서버 루트 경로

    서버가 실행 중인지 확인하는 가장 기본적인 엔드포인트입니다.
    접속: http://localhost:8000/
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
