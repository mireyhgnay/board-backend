"""
📌 router.py - API v1 라우터 통합 관리

【 역할 】
    v1의 모든 API 라우터를 한 곳에서 모아 등록합니다.
    main.py에서는 이 파일 하나만 include하면 모든 API가 등록됩니다.

【 APIRouter란? 】
    FastAPI에서 라우터를 분리하기 위한 클래스입니다.
    Express.js의 Router()와 비슷합니다.

    각 기능별로 APIRouter를 만들고, 여기서 하나로 합칩니다.

【 새 라우터 추가 방법 】
    1. api/v1/ 에 새 파일 생성 (예: posts.py)
    2. 파일에 router = APIRouter() 생성 및 엔드포인트 작성
    3. 이 파일에서 import 후 api_router.include_router() 로 등록

【 현재 등록된 API 그룹 】
    - /api/v1/health  : 서버 상태 확인 (헬스체크)
    (추후 추가 예정)
    - /api/v1/posts   : 게시글
    - /api/v1/comments: 댓글
"""

from fastapi import APIRouter

# 메인 라우터: 모든 v1 API의 집합점
api_router = APIRouter()


# ────────────────────────────────────────────────────────────────
# 🏥 헬스체크 엔드포인트
# ────────────────────────────────────────────────────────────────
@api_router.get(
    "/health",
    tags=["Health"],            # Swagger UI에서 그룹으로 묶임
    summary="서버 상태 확인",   # Swagger UI에 표시될 요약
    description="서버가 정상적으로 동작하는지 확인하는 엔드포인트입니다."
)
def health_check():
    """
    📌 서버 상태 확인 API

    서버가 살아있는지 확인하는 가장 기본적인 API입니다.
    보통 모니터링 시스템이나 배포 시 서버 준비 여부 확인에 사용합니다.

    응답: {"status": "ok", "message": "서버가 정상 작동 중입니다."}
    """
    return {
        "status": "ok",
        "message": "서버가 정상 작동 중입니다.",
        "version": "v1"
    }


# ────────────────────────────────────────────────────────────────
# 📦 각 기능별 라우터 등록 (기능을 추가할 때 여기에 등록하세요)
# ────────────────────────────────────────────────────────────────

# 게시글 API 라우터 등록
from app.api.v1 import posts
api_router.include_router(
    posts.router,
    prefix="/posts",
    tags=["Posts"],
)

# 아래는 라우터 추가 예시입니다. 파일 생성 후 주석을 해제하세요.

# from app.api.v1 import comments
# api_router.include_router(
#     comments.router,
#     prefix="/comments",
#     tags=["Comments"],
# )
