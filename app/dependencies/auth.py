"""
📌 auth.py - 인증 관련 의존성

【 역할 】
    JWT 토큰을 검증하고 현재 로그인한 사용자를 반환합니다.
    인증이 필요한 모든 API 엔드포인트에서 Depends()로 사용합니다.

【 HTTP Bearer 토큰이란? 】
    클라이언트가 API 요청 시 헤더에 토큰을 담아 보내는 방식입니다.
    헤더 형식: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5...

    프론트엔드에서 axios 사용 예시:
        axios.get('/api/v1/posts', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        })
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token

# HTTPBearer: Authorization 헤더에서 Bearer 토큰을 자동으로 추출하는 FastAPI 도구
# auto_error=False: 토큰이 없어도 에러를 자동 발생시키지 않음 (직접 처리)
oauth2_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> int:
    """
    📌 현재 요청에서 JWT 토큰을 검증하고 사용자 ID를 반환합니다.

    【 동작 흐름 】
    1. 요청 헤더에서 Bearer 토큰 추출
    2. 토큰 디코딩 및 유효성 검사
    3. payload에서 사용자 ID(sub) 추출
    4. 사용자 ID 반환

    Args:
        credentials: HTTPBearer가 자동으로 주입하는 인증 정보

    Returns:
        int: 현재 로그인한 사용자의 ID

    Raises:
        HTTPException 401: 토큰이 없거나 유효하지 않은 경우
    """
    # 토큰이 없는 경우
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},  # 표준 인증 에러 헤더
        )

    # 토큰 디코딩
    payload = decode_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # payload에서 사용자 ID 추출
    # JWT 표준에서 subject(사용자 식별자)는 "sub" 키에 저장
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에서 사용자 정보를 찾을 수 없습니다.",
        )

    return int(user_id)


def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> int | None:
    """
    📌 선택적 인증: 토큰이 있으면 사용자 ID를, 없으면 None을 반환합니다.

    로그인하지 않아도 볼 수 있지만, 로그인하면 더 많은 기능을 제공하는
    API 엔드포인트에서 사용합니다.

    예: 게시글 목록 (비로그인도 조회 가능, 로그인하면 좋아요 여부도 표시)
    """
    if not credentials:
        return None

    payload = decode_token(credentials.credentials)
    if payload is None:
        return None

    user_id = payload.get("sub")
    return int(user_id) if user_id else None
