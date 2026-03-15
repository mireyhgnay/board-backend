"""
📌 post.py - 게시글 API 요청/응답 스키마 정의

【 역할 】
    게시글 관련 API에서 주고받는 데이터의 형식(구조)을 정의합니다.
    Pydantic이 자동으로 데이터 유효성을 검사해줍니다.

【 왜 스키마를 나누나요? 】
    - PostCreate: 게시글 생성 시 클라이언트가 보내는 데이터 (title, content만)
    - PostResponse: 서버가 응답으로 보내는 데이터 (id, created_at 등 포함)

    생성 요청에는 id가 없지만 응답에는 id가 있어야 합니다.
    이렇게 용도별로 분리하면 불필요한 데이터 전송을 방지할 수 있습니다.

【 Pydantic의 자동 검증 예시 】
    PostCreate(title="", content="내용")
    → title이 빈 문자열이면 min_length=1 조건에 의해 422 에러 자동 반환
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PostBase(BaseModel):
    """
    📌 게시글 공통 필드

    PostCreate와 PostResponse가 공유하는 필드를 정의합니다.
    공통 필드를 한 곳에서 관리하면 중복을 줄일 수 있습니다.
    """

    # Field(): Pydantic에서 필드에 제약 조건을 추가하는 방법
    # min_length=1: 최소 1자 이상 (빈 문자열 방지)
    # max_length=200: 최대 200자 (DB 컬럼 길이와 일치시킴)
    title: str = Field(
        ...,  # ... 은 필수 입력이라는 의미 (None 불가)
        min_length=1,
        max_length=200,
        description="게시글 제목",
        examples=["첫 번째 게시글"]
    )

    # 게시글 내용: 최소 1자 이상 입력 필수
    content: str = Field(
        ...,
        min_length=1,
        description="게시글 내용",
        examples=["안녕하세요! 첫 게시글입니다."]
    )


class PostCreate(PostBase):
    """
    📌 게시글 생성 요청 스키마

    클라이언트가 POST /api/v1/posts 로 보내는 데이터 형식입니다.
    title과 content만 있으면 됩니다. (id, created_at 등은 서버에서 자동 생성)
    """
    pass  # PostBase의 필드를 그대로 사용


class PostUpdate(BaseModel):
    """
    📌 게시글 수정 요청 스키마

    클라이언트가 PUT /api/v1/posts/{post_id} 로 보내는 데이터 형식입니다.

    【 왜 Optional을 사용하나요? 】
        수정 시에는 제목만 바꾸거나, 내용만 바꿀 수도 있습니다.
        Optional로 선언하면 보내지 않은 필드는 None이 되어
        "변경하지 않겠다"는 의미로 처리할 수 있습니다.

    【 PostBase를 상속하지 않는 이유 】
        PostBase는 title, content가 모두 필수(...)입니다.
        수정 시에는 둘 다 선택적이어야 하므로 별도로 정의합니다.
    """

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="수정할 게시글 제목 (보내지 않으면 변경 안 함)",
        examples=["수정된 제목"]
    )

    content: Optional[str] = Field(
        default=None,
        min_length=1,
        description="수정할 게시글 내용 (보내지 않으면 변경 안 함)",
        examples=["수정된 내용입니다."]
    )


class PostResponse(PostBase):
    """
    📌 게시글 응답 스키마

    서버가 클라이언트에게 응답으로 보내는 데이터 형식입니다.
    DB에서 자동 생성되는 id, created_at, updated_at이 추가됩니다.

    model_config의 from_attributes = True:
        SQLAlchemy 모델 객체를 Pydantic 스키마로 자동 변환해줍니다.
        예: Post 모델 객체 → PostResponse 스키마로 변환
        이전 Pydantic v1에서는 orm_mode = True 였습니다.
    """

    id: int = Field(description="게시글 고유 ID")
    created_at: datetime = Field(description="생성일시")
    updated_at: datetime = Field(description="수정일시")

    # Pydantic v2 설정: SQLAlchemy 모델 → Pydantic 스키마 자동 변환 허용
    model_config = {"from_attributes": True}
