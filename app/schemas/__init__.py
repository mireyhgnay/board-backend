"""
📌 schemas/__init__.py - 스키마 패키지 초기화

【 스키마(Schema)란? 】
    API 요청/응답 데이터의 형식(구조)을 정의하는 곳입니다.
    Pydantic 모델을 사용합니다.

【 모델(Model) vs 스키마(Schema) 차이 】
    ┌──────────────────────────────────────────────────────────┐
    │  Model (SQLAlchemy)                                      │
    │  - DB 테이블 구조를 정의                                    │
    │  - app/models/ 에 위치                                   │
    │                                                          │
    │  Schema (Pydantic)                                       │
    │  - API 입출력 데이터 구조를 정의                            │
    │  - app/schemas/ 에 위치                                  │
    │  - 데이터 유효성 검사 (타입, 필수값 등)                      │
    └──────────────────────────────────────────────────────────┘

【 스키마 네이밍 컨벤션 】
    보통 하나의 리소스(예: User)에 대해 여러 스키마를 만듭니다:
    - UserBase:   공통 필드
    - UserCreate: 생성 시 요청 데이터 (비밀번호 포함)
    - UserUpdate: 수정 시 요청 데이터 (선택적 필드)
    - UserResponse: 응답 데이터 (비밀번호 제외)

【 사용 예시 】
    # 스키마 추가 후 여기에 import
    from app.schemas.user import UserCreate, UserResponse
    from app.schemas.post import PostCreate, PostResponse
"""

# 스키마를 추가할 때마다 여기에 import를 추가하세요
# from app.schemas.user import UserCreate, UserResponse
# from app.schemas.post import PostCreate, PostResponse
