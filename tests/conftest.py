"""
📌 conftest.py - pytest 공통 설정 및 픽스처

【 conftest.py란? 】
    pytest가 자동으로 인식하는 특별한 파일입니다.
    모든 테스트 파일에서 공통으로 사용하는 설정과 픽스처를 정의합니다.

【 픽스처(Fixture)란? 】
    테스트 실행 전에 준비해야 할 것들을 설정하는 함수입니다.
    @pytest.fixture 데코레이터를 사용합니다.

    예: 테스트용 DB 연결, 테스트용 사용자 생성, HTTP 클라이언트 초기화

【 테스트 DB 전략 】
    실제 DB 대신 SQLite 인메모리 DB를 사용합니다.
    - 빠릅니다 (디스크 접근 없음)
    - 각 테스트마다 깨끗한 DB로 시작
    - 별도 MySQL 서버 없이도 테스트 가능
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# ────────────────────────────────────────────────────────────────
# 🧪 테스트용 DB 설정 (SQLite 인메모리)
# ────────────────────────────────────────────────────────────────
# 실제 MySQL 대신 메모리 안에서만 사용하는 임시 SQLite DB를 사용합니다
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 멀티스레드 허용
    poolclass=StaticPool,  # 같은 연결을 재사용 (인메모리 DB 유지를 위해)
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="function")
def db():
    """
    📌 각 테스트 함수마다 깨끗한 DB 세션을 제공합니다.

    scope="function": 각 테스트 함수 실행 전후로 setup/teardown 실행
    - 테스트 시작: 테이블 생성
    - 테스트 종료: 테이블 삭제 (다음 테스트는 깨끗한 상태에서 시작)
    """
    # 테이블 생성
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 테이블 삭제 (다음 테스트를 위해 초기화)
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """
    📌 테스트용 HTTP 클라이언트를 제공합니다.

    FastAPI의 TestClient를 사용해서 실제 서버 없이 API를 호출할 수 있습니다.
    get_db 의존성을 테스트용 DB 세션으로 교체합니다.

    사용 예시:
        def test_health_check(client):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
    """
    def override_get_db():
        """실제 DB 대신 테스트 DB를 주입합니다"""
        try:
            yield db
        finally:
            pass

    # 의존성 교체 (Dependency Override)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 테스트 후 의존성 복원
    app.dependency_overrides.clear()
