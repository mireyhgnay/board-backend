"""
📌 post_service.py - 게시글 비즈니스 로직 레이어 (Service)

【 역할 】
    게시글과 관련된 비즈니스 로직(규칙, 검증, 계산)을 처리합니다.
    Router에서 요청을 받아 Repository를 호출하고 결과를 반환합니다.

【 왜 Service 레이어가 필요한가요? 】
    지금은 단순히 Repository를 호출만 하지만, 실제 서비스에서는:
    - 입력 데이터 검증 (욕설 필터링, 스팸 방지 등)
    - 권한 확인 (작성자만 수정 가능 등)
    - 여러 Repository 조합 (게시글 생성 + 알림 발송 등)
    같은 비즈니스 규칙이 들어갑니다.

    Router에 이런 로직을 넣으면:
    - Router가 비대해지고
    - 같은 로직을 여러 곳에서 중복 작성하게 됩니다

【 계층 흐름 】
    Router → Service → Repository → DB
    각 계층은 바로 아래 계층만 호출합니다.
"""

from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate
from app.repositories import post_repository


def create_post(db: Session, post_data: PostCreate) -> Post:
    """
    📌 새 게시글을 생성합니다.

    현재는 단순히 Repository를 호출하지만,
    나중에 비즈니스 로직(검증, 알림 등)을 추가할 수 있습니다.

    예시 (향후 추가 가능한 로직):
        - 제목에 금지 단어가 포함되어 있는지 검사
        - 같은 사용자가 1분 내 연속 작성 방지
        - 게시글 생성 후 관리자에게 알림 발송

    Args:
        db: DB 세션
        post_data: 게시글 생성 데이터 (title, content)

    Returns:
        Post: 생성된 게시글 객체
    """
    return post_repository.create_post(db=db, post_data=post_data)
