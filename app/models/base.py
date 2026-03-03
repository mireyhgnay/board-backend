"""
📌 base.py - 모든 모델이 공통으로 가지는 기본 필드 정의

【 역할 】
    모든 테이블에 공통적으로 필요한 필드(id, 생성일, 수정일)를
    BaseModel 클래스로 만들어서 재사용합니다.

【 왜 공통 BaseModel을 만드나요? 】
    User 테이블, Post 테이블, Comment 테이블 등 모든 테이블에
    id, created_at, updated_at 이 필요합니다.
    BaseModel을 상속받으면 이 필드들을 자동으로 갖게 됩니다.
    코드 중복을 줄이고 일관성을 유지하는 좋은 패턴입니다.

【 Mixin 패턴이란? 】
    특정 기능을 여러 클래스에 추가하기 위해 사용하는 작은 클래스입니다.
    상속을 통해 기능을 "섞어서(mix-in)" 사용합니다.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class TimestampMixin:
    """
    📌 생성일/수정일 자동 관리 Mixin

    이 클래스를 상속받으면 created_at과 updated_at이 자동으로 관리됩니다.
    - created_at: 레코드 생성 시 자동으로 현재 시간 입력
    - updated_at: 레코드 수정 시 자동으로 현재 시간 업데이트

    server_default=func.now(): DB 서버 시간 기준으로 기본값 설정
    onupdate=func.now():       UPDATE 쿼리 시 자동으로 현재 시간 업데이트
    """

    # 생성일시: 레코드가 INSERT될 때 자동으로 현재 시간이 들어갑니다
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # DB 서버의 현재 시간을 기본값으로
        nullable=False,
        comment="생성일시"
    )

    # 수정일시: 레코드가 UPDATE될 때 자동으로 현재 시간으로 갱신됩니다
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),        # UPDATE 시 자동 갱신
        nullable=False,
        comment="수정일시"
    )


class BaseModel(Base, TimestampMixin):
    """
    📌 모든 모델의 기본 클래스

    __abstract__ = True: 이 클래스 자체는 테이블을 만들지 않습니다.
    상속받은 자식 클래스만 실제 테이블이 됩니다.

    상속 예시:
        class User(BaseModel):
            __tablename__ = "users"
            # id, created_at, updated_at은 자동으로 포함됨
            email = Column(String(255))
    """
    __abstract__ = True  # 추상 클래스: 이 클래스 자체는 DB 테이블이 되지 않음

    # 모든 테이블의 기본 키 (Primary Key)
    # autoincrement=True: 새 레코드 삽입 시 자동으로 1씩 증가
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,         # 자주 검색하는 컬럼은 index를 걸어 성능 향상
        comment="기본키"
    )
