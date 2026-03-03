"""
📌 tests/__init__.py - 테스트 패키지

【 테스트를 작성해야 하는 이유 】
    - 기능 추가/수정 후 기존 기능이 망가지지 않았는지 자동으로 확인
    - API 스펙을 코드로 문서화하는 효과
    - 리팩토링 시 자신감 있게 코드 변경 가능

【 테스트 파일 구조 】
    tests/
    ├── __init__.py
    ├── conftest.py          # 공통 설정 및 픽스처
    ├── test_auth.py         # 인증 API 테스트
    ├── test_users.py        # 유저 API 테스트
    └── test_posts.py        # 게시글 API 테스트

【 테스트 실행 방법 】
    pytest tests/            # 전체 테스트 실행
    pytest tests/ -v         # 상세 출력
    pytest tests/test_auth.py  # 특정 파일만
"""
