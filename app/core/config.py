"""
📌 config.py - 환경 변수 & 애플리케이션 설정 관리

【 역할 】
    .env 파일에 있는 환경 변수들을 읽어서 앱 전체에서 사용할 수 있는
    설정 객체(Settings)로 만들어주는 파일입니다.

【 왜 환경 변수를 사용하나요? 】
    DB 비밀번호, JWT 시크릿 키 같은 민감한 정보를 코드에 직접 쓰면
    GitHub에 올렸을 때 유출될 수 있습니다.
    그래서 .env 파일에 따로 저장하고 .gitignore로 git에서 제외시킵니다.

【 pydantic-settings 란? 】
    pydantic은 Python에서 데이터 검증을 위한 라이브러리입니다.
    pydantic-settings는 환경 변수를 자동으로 읽고 타입 검증까지 해줍니다.

【 Supabase란? 】
    Firebase의 오픈소스 대안으로, PostgreSQL 기반의 클라우드 DB 서비스입니다.
    - 무료 플랜 제공 (개발/학습용으로 충분)
    - PostgreSQL DB를 클라우드에서 바로 사용 가능
    - 대시보드에서 테이블, 데이터를 시각적으로 확인 가능
    - 별도 서버 설치 없이 바로 사용 가능!
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    📌 애플리케이션 전체 설정을 담는 클래스

    BaseSettings를 상속받으면 .env 파일의 값을 자동으로 읽어옵니다.
    변수명이 대소문자 구분 없이 매칭됩니다.
    """

    # ────────────────────────────────────────────────
    # 🔧 앱 기본 설정
    # ────────────────────────────────────────────────
    APP_NAME: str = "Board Backend"         # 앱 이름 (기본값 설정 가능)
    APP_VERSION: str = "0.1.0"             # API 버전
    DEBUG: bool = False                     # True면 SQL 쿼리 등 자세한 로그 출력 (개발 시에만 True)

    # ────────────────────────────────────────────────
    # 🗄️ Supabase(PostgreSQL) 데이터베이스 설정
    #
    # Supabase 접속 URL 가져오는 방법:
    #   1. https://supabase.com 에서 프로젝트 생성
    #   2. 프로젝트 대시보드 → Settings → Database
    #   3. "Connection string" 탭 → "URI" 복사
    #
    # 두 가지 연결 방식:
    #   ① Direct connection (포트 5432): 로컬 개발 환경에서 사용
    #      postgresql://postgres:[비밀번호]@db.[프로젝트ID].supabase.co:5432/postgres
    #
    #   ② Connection Pooler (포트 6543): 서버리스/배포 환경에서 권장
    #      postgresql://postgres.[프로젝트ID]:[비밀번호]@aws-0-[리전].pooler.supabase.com:6543/postgres
    #
    # 로컬 개발 중에는 ①번을, Railway/Render 등에 배포할 때는 ②번을 사용하세요.
    # ────────────────────────────────────────────────
    DATABASE_URL: str = ""  # .env 파일에서 반드시 설정해야 합니다!

    # ────────────────────────────────────────────────
    # 🌐 CORS 설정
    # CORS = Cross-Origin Resource Sharing
    #
    # 프론트엔드(Vercel)에서 백엔드(Railway 등)로 요청할 때
    # 브라우저가 보안상 차단하는데, 이걸 허용해주는 설정입니다.
    #
    # 예시:
    #   - 프론트: https://my-board.vercel.app
    #   - 백엔드: https://board-api.railway.app
    #   → 다른 도메인이므로 CORS 허용 필요!
    # ────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",            # React 기본 포트 (로컬 개발)
        "http://localhost:5173",            # Vite 기본 포트 (로컬 개발)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # ⚠️ Vercel 배포 URL을 여기에 추가하세요!
        # "https://your-project.vercel.app",
    ]

    class Config:
        """
        📌 pydantic-settings 설정

        env_file: .env 파일 경로를 지정합니다
        env_file_encoding: .env 파일의 인코딩 (한글 깨짐 방지)
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    📌 Settings 인스턴스를 반환하는 함수

    @lru_cache() 데코레이터가 붙어 있어서 처음 호출될 때만 Settings를 생성하고
    그 이후에는 캐시된 값을 반환합니다. (성능 최적화)

    사용 예시:
        from app.core.config import get_settings
        settings = get_settings()
        print(settings.DATABASE_URL)
    """
    return Settings()


# 편의를 위해 settings 인스턴스를 바로 import할 수 있게 제공
# 사용: from app.core.config import settings
settings = get_settings()
