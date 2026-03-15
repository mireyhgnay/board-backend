"""
📌 post.py - 게시글(Post) 모델 정의

【 역할 】
    게시판의 핵심인 '게시글' 테이블을 정의합니다.
    이 파일이 DB의 posts 테이블 구조를 결정합니다.

【 BaseModel 상속 】
    BaseModel을 상속받으면 id, created_at, updated_at 필드가 자동으로 포함됩니다.
    게시글 고유의 필드(title, content)만 추가하면 됩니다.

【 DB 테이블 구조 】
    posts 테이블:
    ┌─────────────┬──────────────┬─────────────────────┐
    │ 컬럼명       │ 타입          │ 설명                 │
    ├─────────────┼──────────────┼─────────────────────┤
    │ id          │ Integer (PK) │ 자동 증가 고유 ID     │
    │ title       │ String(200)  │ 게시글 제목           │
    │ content     │ Text         │ 게시글 내용           │
    │ created_at  │ DateTime     │ 생성일시 (자동)       │
    │ updated_at  │ DateTime     │ 수정일시 (자동)       │
    └─────────────┴──────────────┴─────────────────────┘
"""

from sqlalchemy import Column, String, Text

from app.models.base import BaseModel


class Post(BaseModel):
    """
    📌 게시글 모델

    BaseModel을 상속받아 id, created_at, updated_at은 자동으로 포함됩니다.
    __tablename__으로 실제 DB에 생성될 테이블 이름을 지정합니다.
    """

    # 테이블 이름: DB에 'posts'라는 이름으로 테이블이 생성됩니다
    __tablename__ = "posts"

    # 게시글 제목: 최대 200자, 필수 입력(nullable=False)
    # index=True: 제목으로 검색할 일이 많으므로 인덱스를 걸어 검색 성능을 높입니다
    title = Column(
        String(200),
        nullable=False,
        index=True,
        comment="게시글 제목"
    )

    # 게시글 내용: Text 타입은 길이 제한이 없습니다 (긴 글 저장 가능)
    # String(255)는 최대 255자이지만, Text는 무제한입니다
    content = Column(
        Text,
        nullable=False,
        comment="게시글 내용"
    )
