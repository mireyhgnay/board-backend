"""
📌 posts.py - 게시글 API 엔드포인트

【 역할 】
    게시글 관련 HTTP 요청을 받아 처리하는 라우터입니다.
    HTTP 요청/응답 처리만 담당하고, 실제 로직은 Service에 위임합니다.

【 REST API 설계 원칙 】
    HTTP 메서드와 URL로 어떤 동작을 할지 표현합니다:
    ┌─────────┬──────────────────┬─────────────────┐
    │ 메서드   │ URL              │ 동작             │
    ├─────────┼──────────────────┼─────────────────┤
    │ POST    │ /api/v1/posts    │ 게시글 생성       │
    │ GET     │ /api/v1/posts    │ 게시글 목록 조회   │
    │ GET     │ /api/v1/posts/1  │ 게시글 상세 조회   │
    │ PUT     │ /api/v1/posts/1  │ 게시글 수정       │
    │ DELETE  │ /api/v1/posts/1  │ 게시글 삭제       │
    └─────────┴──────────────────┴─────────────────┘

【 Depends(get_db)란? 】
    FastAPI의 의존성 주입(Dependency Injection) 기능입니다.
    API 함수가 호출될 때 자동으로 DB 세션을 생성해서 넘겨줍니다.
    함수가 끝나면 자동으로 세션을 정리(close)합니다.
    → DB 세션 관리를 신경 쓰지 않아도 됩니다!
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.post import PostCreate, PostResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.services import post_service

# 이 파일의 라우터 객체: router.py에서 이것을 가져다 등록합니다
router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[PostResponse],
    summary="게시글 목록 조회",
    description="게시글 목록을 페이지네이션으로 조회합니다.",
)
def get_posts(
    page: int = Query(
        default=1,
        ge=1,  # ge = greater than or equal (1 이상)
        description="페이지 번호 (1부터 시작)",
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=100,  # le = less than or equal (최대 100개)
        description="한 페이지에 보여줄 게시글 수 (기본 20, 최대 100)",
    ),
    db: Session = Depends(get_db),
):
    """
    📌 게시글 목록 조회 API

    【 요청 예시 】
        GET /api/v1/posts?page=1&size=10

    【 Query Parameter란? 】
        URL의 ? 뒤에 오는 값입니다.
        /api/v1/posts?page=2&size=5 → page=2, size=5
        FastAPI의 Query()를 사용하면 자동으로 파싱 & 검증됩니다.

    【 응답 예시 】
        200 OK
        {
            "success": true,
            "message": "게시글 목록을 조회했습니다.",
            "data": [
                {
                    "id": 2,
                    "title": "두 번째 게시글",
                    "content": "내용...",
                    "created_at": "...",
                    "updated_at": "..."
                },
                {
                    "id": 1,
                    "title": "첫 번째 게시글",
                    "content": "내용...",
                    "created_at": "...",
                    "updated_at": "..."
                }
            ],
            "total": 2,
            "page": 1,
            "size": 10,
            "total_pages": 1
        }

    Args:
        page: 페이지 번호 (Query Parameter, 기본값 1)
        size: 페이지 크기 (Query Parameter, 기본값 10)
        db: DB 세션 (Depends로 자동 주입)

    Returns:
        PaginatedResponse[PostResponse]: 게시글 목록 + 페이지네이션 정보
    """

    # Service 레이어에 비즈니스 로직 위임
    result = post_service.get_posts(db=db, page=page, size=size)

    # PaginatedResponse 형식으로 응답 구성
    return PaginatedResponse[PostResponse](
        message="게시글 목록을 조회했습니다.",
        data=[PostResponse.model_validate(post) for post in result["posts"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        total_pages=result["total_pages"],
    )


@router.post(
    "",
    response_model=DataResponse[PostResponse],
    status_code=status.HTTP_201_CREATED,
    summary="게시글 생성",
    description="새로운 게시글을 생성합니다. 제목과 내용을 입력해야 합니다.",
)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
):
    """
    📌 게시글 생성 API

    【 요청 예시 】
        POST /api/v1/posts
        {
            "title": "첫 번째 게시글",
            "content": "안녕하세요! 첫 게시글입니다."
        }

    【 응답 예시 】
        201 Created
        {
            "success": true,
            "message": "게시글이 생성되었습니다.",
            "data": {
                "id": 1,
                "title": "첫 번째 게시글",
                "content": "안녕하세요! 첫 게시글입니다.",
                "created_at": "2026-03-09T12:00:00+00:00",
                "updated_at": "2026-03-09T12:00:00+00:00"
            }
        }

    【 동작 흐름 】
        1. 클라이언트가 JSON 데이터를 보냄
        2. FastAPI가 PostCreate 스키마로 자동 검증 (유효하지 않으면 422 에러)
        3. Service → Repository → DB 순서로 데이터 저장
        4. 생성된 게시글을 DataResponse 형식으로 응답

    Args:
        post_data: 게시글 생성 요청 데이터 (title, content)
        db: DB 세션 (Depends로 자동 주입)

    Returns:
        DataResponse[PostResponse]: 생성된 게시글 정보를 포함한 응답
    """

    # Service 레이어에 비즈니스 로직 위임
    created_post = post_service.create_post(db=db, post_data=post_data)

    # PostResponse 스키마로 변환하여 응답
    # from_attributes=True 설정 덕분에 SQLAlchemy 모델 → Pydantic 스키마 자동 변환
    return DataResponse[PostResponse](
        message="게시글이 생성되었습니다.",
        data=PostResponse.model_validate(created_post),
    )
