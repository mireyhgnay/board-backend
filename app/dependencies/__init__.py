"""
📌 dependencies/__init__.py - 의존성 주입 패키지

【 FastAPI 의존성 주입(Dependency Injection)이란? 】
    특정 기능(DB 세션 등)을 API 함수에
    자동으로 주입해주는 FastAPI의 핵심 기능입니다.

    Depends()를 사용해서 API 함수가 호출될 때 자동으로 실행됩니다.

【 장점 】
    - 코드 재사용성 향상
    - 공통 로직을 한 곳에서 관리
    - 테스트 시 쉽게 교체 가능 (mock 처리)

【 사용 예시 】
    @router.get("/posts")
    def get_posts(
        db: Session = Depends(get_db),  # DB 세션 자동 주입
    ):
        ...
"""
