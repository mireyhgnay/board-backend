"""
📌 api/v1/__init__.py - API v1 패키지

【 라우터 등록 위치 】
    새로운 API 엔드포인트를 만들면 router.py에 등록하세요.
    각 기능별로 파일을 분리해서 관리합니다.

    예시 구조:
    api/v1/
    ├── __init__.py
    ├── router.py       ← 모든 라우터를 모으는 파일
    ├── auth.py         ← 로그인/회원가입 API
    ├── users.py        ← 유저 관련 API
    ├── posts.py        ← 게시글 API
    └── comments.py     ← 댓글 API
"""
