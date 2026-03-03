"""
📌 alembic/env.py - Alembic 환경 설정

【 역할 】
    Alembic이 마이그레이션을 실행할 때 사용하는 환경을 설정합니다.
    - DB 연결 URL 설정
    - 어떤 모델들을 감지할지 설정 (autogenerate 기능용)

【 중요: 모델을 추가할 때마다 여기에 import 해야 합니다 】
    Alembic의 autogenerate가 동작하려면 모든 모델이 메모리에 로드되어야 합니다.
    새 모델 파일을 만들면 아래 "모델 import 섹션"에 추가하세요.

【 두 가지 실행 모드 】
    1. offline mode: DB 연결 없이 SQL 스크립트만 생성
    2. online mode:  실제 DB에 연결해서 마이그레이션 실행 (일반적인 사용)
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 프로젝트 루트를 Python 경로에 추가 (app 패키지를 import 할 수 있도록)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ────────────────────────────────────────────────────────────────
# 📦 모델 import (중요!)
# 새로운 모델을 만들면 반드시 여기에 추가하세요!
# Alembic이 테이블 변경사항을 자동으로 감지하려면 모든 모델이 로드되어야 합니다.
# ────────────────────────────────────────────────────────────────
from app.core.database import Base  # Base는 반드시 import
from app.models import *            # 모든 모델 import

# 아래에 개별 모델을 명시적으로 import할 수도 있습니다:
# from app.models.user import User
# from app.models.post import Post
# from app.models.comment import Comment

# ────────────────────────────────────────────────────────────────
# ⚙️ 설정 로드
# ────────────────────────────────────────────────────────────────
from app.core.config import settings

# alembic.ini 설정 객체
config = context.config

# alembic.ini의 로깅 설정 적용
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ⚠️ alembic.ini의 sqlalchemy.url 대신 .env에서 읽어온 URL을 사용합니다
# 이렇게 하면 DB 비밀번호를 alembic.ini에 노출하지 않아도 됩니다
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# autogenerate를 위한 메타데이터 설정
# Base.metadata를 전달해야 모델 변경사항을 감지할 수 있습니다
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    📌 오프라인 모드로 마이그레이션 실행

    실제 DB 연결 없이 SQL 스크립트를 생성합니다.
    DB에 직접 접근하지 못하는 상황(CI/CD, 검토 등)에서 사용합니다.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # MySQL은 비교 시 charset 고려 필요
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    📌 온라인 모드로 마이그레이션 실행 (일반적인 사용 방법)

    실제 DB에 연결해서 마이그레이션을 실행합니다.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # 마이그레이션에는 커넥션 풀 불필요
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 컬럼 타입 변경도 감지
        )

        with context.begin_transaction():
            context.run_migrations()


# 실행 모드에 따라 적절한 함수 호출
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
