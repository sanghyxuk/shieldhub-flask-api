from flask import Blueprint, jsonify, request
from .modules import scanner # (1) 방금 만든 스캐너 모듈 임포트

# 'api'라는 이름의 Blueprint 객체 생성
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Spring 서버가 AI 서버의 상태를 확인할 수 있는 헬스 체크 엔드포인트
    """
    return jsonify({
        "status": "Flask AI Server is healthy and running"
    })

# --- (2) 신규 엔드포인트 추가 ---
@api_bp.route('/analyze', methods=['POST'])
def analyze_url():
    """
    Spring 서버로부터 URL을 받아 분석을 시작하는 메인 엔드포인트
    """
    # Spring이 보낸 JSON 데이터에서 'url' 추출
    data = request.json
    target_url = data.get('url')

    if not target_url:
        return jsonify({"success": False, "message": "URL이 필요합니다"}), 400
    
    try:
        # (3) 스캐너 모듈의 메인 함수 호출
        vulnerabilities = scanner.analyze_site(target_url)
        
        # (4) 기획서 포맷에 맞춰 JSON 결과 반환
        return jsonify({
            "success": True,
            "url": target_url,
            "vulnerability_count": len(vulnerabilities),
            "vulnerabilities": vulnerabilities
        })

    except ConnectionError as e:
        # (5) 사이트 연결 실패 시 (scanner.py에서 발생)
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        # (6) 그 외 모든 알 수 없는 오류
        print(f"심각한 오류 발생: {e}")
        return jsonify({"success": False, "message": f"분석 중 서버 오류 발생: {e}"}), 500