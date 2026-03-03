"""
📌 common.py - 공통으로 사용하는 스키마 정의

【 역할 】
    여러 API에서 공통으로 사용하는 응답 형식을 정의합니다.
    일관된 API 응답 구조를 만들어 프론트엔드 개발을 편리하게 합니다.

【 Pydantic이란? 】
    Python 데이터 검증 라이브러리입니다.
    - 타입 힌트를 기반으로 자동 유효성 검사
    - 잘못된 데이터 타입이 들어오면 자동으로 에러 발생
    - JSON 직렬화/역직렬화 자동 처리

    예시:
        class UserCreate(BaseModel):
            email: str          # 필수 필드
            age: Optional[int]  # 선택적 필드

        # 이렇게 사용하면 email이 없으면 자동으로 422 에러 반환
"""

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

# TypeVar: 제네릭 타입을 위한 변수 (어떤 타입이든 올 수 있다는 의미)
# 리스트 API의 data 필드에 User가 올 수도, Post가 올 수도 있습니다
DataT = TypeVar("DataT")


class BaseResponse(BaseModel):
    """
    📌 기본 API 응답 구조

    모든 API 응답이 동일한 구조를 갖도록 합니다.
    프론트엔드에서 response.success, response.message로 일관되게 처리 가능합니다.

    예시 응답:
    {
        "success": true,
        "message": "요청이 성공적으로 처리되었습니다."
    }
    """
    success: bool = True
    message: str = "요청이 성공적으로 처리되었습니다."


class DataResponse(BaseResponse, Generic[DataT]):
    """
    📌 데이터를 포함하는 API 응답 구조

    Generic[DataT]를 사용해서 data 필드의 타입을 유연하게 합니다.

    사용 예시:
        return DataResponse[UserResponse](data=user)

    예시 응답:
    {
        "success": true,
        "message": "조회 성공",
        "data": {
            "id": 1,
            "email": "user@example.com"
        }
    }
    """
    data: Optional[DataT] = None


class PaginatedResponse(BaseResponse, Generic[DataT]):
    """
    📌 페이지네이션이 있는 목록 API 응답 구조

    게시글 목록처럼 많은 데이터를 페이지로 나눠서 보여줄 때 사용합니다.

    예시 응답:
    {
        "success": true,
        "message": "조회 성공",
        "data": [...],
        "total": 100,
        "page": 1,
        "size": 10,
        "total_pages": 10
    }
    """
    data: list[DataT] = []
    total: int = 0          # 전체 데이터 수
    page: int = 1           # 현재 페이지 번호
    size: int = 10          # 페이지 당 데이터 수
    total_pages: int = 0    # 전체 페이지 수


class ErrorResponse(BaseModel):
    """
    📌 에러 응답 구조

    예시 응답:
    {
        "success": false,
        "message": "이미 사용 중인 이메일입니다.",
        "error_code": "EMAIL_ALREADY_EXISTS"
    }
    """
    success: bool = False
    message: str
    error_code: Optional[str] = None  # 프론트엔드에서 에러 타입 구분용
