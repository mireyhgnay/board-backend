"""
📌 repositories/__init__.py - 데이터 접근 레이어 (Repository Pattern)

【 Repository Pattern이란? 】
    DB와 직접 통신하는 코드를 별도 레이어로 분리하는 패턴입니다.
    모든 DB 쿼리(CRUD)는 여기서만 작성합니다.

    CRUD = Create(생성), Read(조회), Update(수정), Delete(삭제)

【 왜 Repository를 분리하나요? 】
    1. DB 관련 코드를 한 곳에 모아 관리
    2. Service 레이어에서 DB 세부사항을 몰라도 됨
    3. 테스트 시 Repository만 Mock으로 교체하면 DB 없이 테스트 가능
    4. SQL 쿼리 최적화를 Repository 안에서만 처리

【 일반적인 Repository 메서드 패턴 】
    - get_by_id(db, id)           : ID로 단건 조회
    - get_all(db, skip, limit)    : 목록 조회 (페이지네이션)
    - get_by_email(db, email)     : 이메일로 조회
    - create(db, schema)          : 생성
    - update(db, id, schema)      : 수정
    - delete(db, id)              : 삭제

【 파일 추가 예시 】
    repositories/
    ├── user_repository.py    # User 테이블 CRUD
    ├── post_repository.py    # Post 테이블 CRUD
    └── comment_repository.py # Comment 테이블 CRUD
"""
