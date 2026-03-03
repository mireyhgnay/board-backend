"""
📌 security.py - 보안 관련 유틸리티

【 역할 】
    비밀번호 해싱(암호화)과 JWT 토큰 생성/검증을 담당합니다.

【 비밀번호 해싱이란? 】
    "password123" → "$2b$12$..." (복잡한 해시값)

    - 해싱은 단방향 암호화입니다. 원래 값을 복원할 수 없습니다.
    - DB에 비밀번호를 그대로 저장하면 DB가 해킹될 때 위험합니다.
    - 해시값만 저장하고 로그인 시 입력한 비밀번호를 다시 해싱해서 비교합니다.
    - bcrypt 알고리즘 사용: 같은 값도 매번 다른 해시가 나옴 (salt 적용)

【 JWT(JSON Web Token)란? 】
    로그인 성공 후 발급하는 인증 토큰입니다.

    구조: header.payload.signature
    - header:    토큰 타입과 알고리즘 정보
    - payload:   사용자 ID 등 데이터 (암호화는 아님! 인코딩만)
    - signature: 위변조 방지 서명 (SECRET_KEY로 서명)

    【 동작 흐름 】
    1. 로그인 → 서버가 JWT 발급
    2. 프론트엔드가 토큰을 저장 (localStorage, cookie 등)
    3. 이후 API 요청 시 헤더에 토큰 포함
       Authorization: Bearer eyJhbGciOiJI...
    4. 서버가 토큰 검증 후 사용자 식별
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ────────────────────────────────────────────────────────────────
# 🔒 비밀번호 해싱 설정
# ────────────────────────────────────────────────────────────────
# CryptContext: 비밀번호 해싱 방식을 설정하는 객체
# schemes=["bcrypt"]: bcrypt 알고리즘 사용 (현재 가장 안전한 방식 중 하나)
# deprecated="auto": 구 버전 알고리즘 자동 처리
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    📌 비밀번호를 bcrypt 해시로 변환합니다.

    Args:
        plain_password: 사용자가 입력한 평문 비밀번호

    Returns:
        str: bcrypt 해시값 (DB에 이 값을 저장)

    사용 예시:
        hashed = hash_password("mypassword123")
        # "$2b$12$abcdefghijklmnopqrstuuABCDEFGHIJKLMNOPQRSTUVWXYZ123"
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    📌 입력한 비밀번호가 해시값과 일치하는지 확인합니다.

    Args:
        plain_password:  사용자가 로그인 시 입력한 비밀번호
        hashed_password: DB에 저장된 해시값

    Returns:
        bool: 일치하면 True, 불일치하면 False

    사용 예시:
        is_valid = verify_password("mypassword123", hashed_from_db)
    """
    return pwd_context.verify(plain_password, hashed_password)


# ────────────────────────────────────────────────────────────────
# 🎫 JWT 토큰 생성 & 검증
# ────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    📌 액세스 토큰을 생성합니다. (단기 토큰)

    액세스 토큰은 API 요청 시 인증에 사용합니다.
    만료 시간이 짧아서 (기본 60분) 탈취되어도 피해를 최소화합니다.

    Args:
        data:          토큰에 담을 데이터 (예: {"sub": "user_id_123"})
                       sub = subject, JWT 표준에서 사용자 식별자를 담는 필드
        expires_delta: 커스텀 만료 시간 (없으면 설정 파일의 기본값 사용)

    Returns:
        str: JWT 토큰 문자열

    사용 예시:
        token = create_access_token(data={"sub": str(user.id)})
    """
    to_encode = data.copy()  # 원본 data 변경 방지

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})  # 만료 시간을 payload에 추가

    # jwt.encode: payload를 SECRET_KEY로 서명해서 토큰 생성
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    📌 리프레시 토큰을 생성합니다. (장기 토큰)

    액세스 토큰이 만료되면 리프레시 토큰으로 새 액세스 토큰을 발급합니다.
    만료 시간이 길어서 (기본 7일) 자주 로그인하지 않아도 됩니다.

    Args:
        data: 토큰에 담을 데이터

    Returns:
        str: JWT 리프레시 토큰 문자열
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(data=data, expires_delta=expires_delta)


def decode_token(token: str) -> Optional[dict]:
    """
    📌 JWT 토큰을 디코딩해서 페이로드(담긴 데이터)를 반환합니다.

    Args:
        token: JWT 토큰 문자열

    Returns:
        dict: 토큰의 payload (예: {"sub": "user_id", "exp": 1234567890})
        None: 토큰이 유효하지 않거나 만료된 경우

    사용 예시:
        payload = decode_token(token)
        if payload:
            user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # 토큰이 변조되었거나, 만료되었거나, 형식이 잘못된 경우
        return None
