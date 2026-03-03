"""
📌 models/__init__.py - 모델 패키지 초기화

【 역할 】
    이 파일이 있으면 Python이 models 폴더를 '패키지'로 인식합니다.
    또한 모든 모델을 한 곳에서 import할 수 있게 합니다.

【 중요: Alembic 마이그레이션을 위해 】
    새로운 모델 파일을 만들면 반드시 여기에 import 해야 합니다.
    Alembic이 테이블 변경사항을 감지하려면 모든 모델이 로드되어 있어야 합니다.

    예시:
    from app.models.user import User
    from app.models.post import Post
    from app.models.comment import Comment
"""

# 현재는 base 모델만 있습니다.
# 새 모델을 만들면 아래에 추가하세요.
from app.models.base import BaseModel, TimestampMixin

# ⚠️ 모델을 추가할 때마다 아래에 import를 추가하세요!
# from app.models.user import User
# from app.models.post import Post
# from app.models.comment import Comment
