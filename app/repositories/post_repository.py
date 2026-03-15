"""
📌 post_repository.py - 게시글 데이터 접근 레이어 (Repository)

【 역할 】
    DB와 직접 대화하는 레이어입니다.
    게시글 테이블에 대한 CRUD(생성, 조회, 수정, 삭제) 쿼리를 담당합니다.

【 왜 Repository 레이어를 분리하나요? 】
    Service 레이어에서 직접 DB 쿼리를 쓰면:
    - 비즈니스 로직과 DB 코드가 섞여 복잡해집니다
    - DB를 변경하면(예: PostgreSQL → MongoDB) Service 코드도 전부 수정해야 합니다

    Repository를 분리하면:
    - DB 관련 코드가 한 곳에 모여 관리가 쉽습니다
    - DB를 변경해도 Repository만 수정하면 됩니다
    - 테스트 시 Repository를 가짜(Mock)로 교체하기 쉽습니다

【 SQLAlchemy 세션(Session) 사용법 】
    db.add(객체)   → 새 레코드를 세션에 추가 (아직 DB에 저장 안 됨)
    db.commit()    → 세션의 변경사항을 실제 DB에 반영
    db.refresh(객체) → DB에서 최신 데이터를 다시 읽어옴 (자동 생성된 id 등 확인)
"""

from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate


def create_post(db: Session, post_data: PostCreate) -> Post:
    """
    📌 새 게시글을 DB에 저장합니다.

    【 동작 흐름 】
        1. PostCreate 스키마 데이터를 Post 모델 객체로 변환
        2. db.add() → 세션에 추가 (INSERT 준비)
        3. db.commit() → 실제 DB에 INSERT 실행
        4. db.refresh() → DB가 자동 생성한 id, created_at 등을 객체에 반영

    Args:
        db: DB 세션 (FastAPI의 Depends(get_db)로 주입받음)
        post_data: 클라이언트가 보낸 게시글 데이터 (title, content)

    Returns:
        Post: 생성된 게시글 모델 객체 (id, created_at 등 포함)
    """

    # model_dump(): Pydantic 스키마를 딕셔너리로 변환
    # **딕셔너리: 딕셔너리를 키워드 인자로 풀어서 전달
    # 예: Post(title="제목", content="내용") 과 동일
    db_post = Post(**post_data.model_dump())

    # 세션에 새 객체 추가 (아직 DB에 저장되지 않은 상태)
    db.add(db_post)

    # 트랜잭션 커밋: 실제로 DB에 INSERT 쿼리가 실행됩니다
    db.commit()

    # DB가 자동 생성한 값(id, created_at, updated_at)을 객체에 반영
    # refresh하지 않으면 db_post.id가 None일 수 있습니다
    db.refresh(db_post)

    return db_post
