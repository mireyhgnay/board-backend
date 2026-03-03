"""
📌 database.py - SQLAlchemy DB 연결 설정

【 역할 】
    Supabase(PostgreSQL) 데이터베이스와의 연결을 설정하고 관리합니다.
    API 요청마다 DB 세션을 생성하고 요청이 끝나면 자동으로 닫아줍니다.

【 SQLAlchemy 핵심 개념 】
    ┌────────────────────────────────────────────────────────────┐
    │  Engine      → DB 연결 자체 (Supabase 서버와의 통로)          │
    │  Session     → 실제 DB 작업을 하는 단위 (트랜잭션 관리)        │
    │  Base        → 모든 모델 클래스의 부모 (테이블 정의의 기준점)   │
    └────────────────────────────────────────────────────────────┘

【 ORM(Object Relational Mapping)이란? 】
    DB 테이블을 Python 클래스로 표현하고,
    SQL 쿼리를 Python 코드로 작성할 수 있게 해줍니다.

    SQL:    SELECT * FROM users WHERE id = 1;
    ORM:    db.query(User).filter(User.id == 1).first()

    SQL을 직접 안 써도 되니 편리하고, DB 변경 시 코드 수정이 최소화됩니다.

【 커넥션 풀(Connection Pool)이란? 】
    매 요청마다 DB 연결을 새로 만들면 느립니다.
    커넥션 풀은 미리 여러 연결을 만들어 두고 재사용합니다.
    레스토랑으로 비유하면: 손님이 올 때마다 주방을 짓는 게 아니라
    미리 주방(연결)을 만들어두고 손님(요청)이 오면 바로 사용하는 방식입니다.

【 Supabase Connection Pooler 안내 】
    Supabase는 "Transaction Mode" 풀러(포트 6543)를 제공합니다.
    서버리스 환경(Vercel Functions 등)에서는 풀러 사용이 권장됩니다.
    로컬 FastAPI 서버에서는 Direct Connection(포트 5432)이 더 안정적입니다.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# ────────────────────────────────────────────────────────────────
# 🔌 Engine 생성 - DB 연결의 핵심
# ────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,

    # 커넥션 풀 설정
    pool_size=5,            # 기본으로 유지할 연결 수 (Supabase 무료 플랜은 연결 수 제한 있음)
    max_overflow=10,        # pool_size 초과 시 추가로 만들 수 있는 연결 수
    pool_timeout=30,        # 연결을 기다리는 최대 시간 (초)
    pool_pre_ping=True,     # 연결 사용 전 유효성 확인 (끊긴 연결 자동 감지)
                            # Supabase는 일정 시간 후 유휴 연결을 끊으므로 이 옵션이 중요합니다

    # 개발 시 True로 설정하면 실행되는 SQL 쿼리를 터미널에서 볼 수 있습니다
    # 운영 환경(production)에서는 반드시 False로 설정하세요 (성능 저하, 보안 위험)
    echo=settings.DEBUG,
)


# ────────────────────────────────────────────────────────────────
# 🏭 SessionLocal - DB 세션 팩토리
# ────────────────────────────────────────────────────────────────
# sessionmaker는 Session 클래스를 만드는 팩토리(공장)입니다.
# SessionLocal()을 호출하면 새로운 DB 세션이 생성됩니다.
SessionLocal = sessionmaker(
    bind=engine,            # 위에서 만든 engine에 연결
    autocommit=False,       # 자동 커밋 비활성화 (명시적으로 commit() 호출 필요)
                            # → 에러 발생 시 자동 rollback 가능
    autoflush=False,        # 자동 flush 비활성화 (쿼리 실행 전 자동 DB 반영 끄기)
                            # → 성능 향상, 명시적 제어 가능
)


# ────────────────────────────────────────────────────────────────
# 🏛️ Base - 모든 SQLAlchemy 모델의 기반 클래스
# ────────────────────────────────────────────────────────────────
# declarative_base()로 만든 Base를 상속받아 모델(테이블)을 정의합니다.
# 모든 모델이 Base를 상속받아야 SQLAlchemy가 테이블로 인식합니다.
#
# 사용 예시 (app/models/user.py):
#   from app.core.database import Base
#   class User(Base):
#       __tablename__ = "users"
#       id = Column(Integer, primary_key=True)
Base = declarative_base()


# ────────────────────────────────────────────────────────────────
# 🔄 get_db - DB 세션 의존성 주입 함수
# ────────────────────────────────────────────────────────────────
def get_db():
    """
    📌 FastAPI 의존성 주입(Dependency Injection)용 DB 세션 생성기

    【 yield 란? 】
        일반 함수는 return으로 값을 반환하고 종료됩니다.
        yield를 쓰면 값을 반환하고 '일시정지' 상태가 됩니다.
        API 요청 처리가 끝나면 yield 이후 코드(finally)가 실행됩니다.

    【 동작 흐름 】
        1. API 요청 들어옴
        2. SessionLocal()로 DB 세션 생성
        3. yield db → API 함수에 세션 전달
        4. API 함수 실행 (Supabase DB 작업)
        5. API 응답 후 finally 블록 실행 → db.close()로 세션 반납

    【 사용 방법 】
        from fastapi import Depends
        from app.core.database import get_db
        from sqlalchemy.orm import Session

        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            # 여기서 db를 사용해 Supabase DB 작업을 합니다
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db        # API 함수에 세션을 넘겨줌
    except Exception:
        db.rollback()   # 에러 발생 시 변경사항 되돌리기
        raise           # 에러를 다시 위로 전파
    finally:
        db.close()      # 요청 완료 후 반드시 세션 닫기 (메모리 누수 방지)


def check_db_connection() -> bool:
    """
    📌 DB 연결 상태를 확인합니다.

    서버 시작 시 Supabase 연결이 정상인지 검사하는 용도입니다.

    Returns:
        bool: 연결 성공 시 True, 실패 시 False
    """
    try:
        with engine.connect() as conn:
            # SELECT 1: DB 연결이 살아있는지 확인하는 가장 가벼운 쿼리
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        return False
