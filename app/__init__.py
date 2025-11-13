from flask import Flask
from .modules import predictor # 1. 방금 만든 predictor 모듈 임포트
from . import routes           # 2. 방금 만든 routes 모듈 임포트

def create_app():
    """
    Flask 애플리케이션 팩토리 함수
    run.py가 이 함수를 호출하여 앱을 생성합니다.
    """
    app = Flask(__name__)
    
    # --- 1. ML 모델 로드 ---
    # 서버가 시작될 때 모델을 메모리에 '단 한 번'만 로드합니다.
    # 요청이 올 때마다 로드하면 매우 느려집니다.
    print("Flask 서버 시작: ML 모델 로딩을 시도합니다...")
    predictor.load_model()
    
    # --- 2. API 라우트(Blueprint) 등록 ---
    # routes.py에 정의된 /api/health 같은 엔드포인트들을 
    # 실제 Flask 앱에 등록합니다.
    app.register_blueprint(routes.api_bp)
    
    @app.route('/')
    def index():
        # 루트 URL 접속 시 간단한 환영 메시지
        return "ShieldHub Flask AI Server"

    return app