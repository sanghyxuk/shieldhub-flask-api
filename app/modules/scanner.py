import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from . import predictor

def analyze_site(target_url):
    """
    주어진 URL을 분석하여 취약점 목록을 반환합니다.
    """
    print(f"[{target_url}] 분석 시작...")
    findings = []

    try:
        # 1. 초기 GET 요청 (수동적 분석)
        response = requests.get(target_url, timeout=10, headers={'User-Agent': 'ShieldHubScanner/1.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. 수동적 분석: 보안 헤더 검사
        findings.extend(_check_security_headers(response, target_url))

        # 3. 능동적 분석: 폼(Form) 데이터 수집 및 테스트
        findings.extend(_test_forms(soup, target_url))

        # 4. 능동적 분석: URL 파라미터 테스트 (개선)
        findings.extend(_test_url_parameters(soup, target_url))

        # 5. 수동적 분석: 민감 정보 노출 검사
        findings.extend(_check_sensitive_info(response, target_url))

        # 6. 중복 제거 및 우선순위 정렬
        findings = _deduplicate_findings(findings)

        print(f"[{target_url}] 분석 완료. {len(findings)}개 항목 발견.")
        return findings

    except requests.RequestException as e:
        print(f"[{target_url}] 사이트 연결 실패: {e}")
        raise ConnectionError(f"사이트에 연결할 수 없습니다: {target_url}")
    except Exception as e:
        print(f"[{target_url}] 분석 중 알 수 없는 오류: {e}")
        raise

# ========================================
# 보안 헤더 검사
# ========================================
def _check_security_headers(response, target_url):
    """HTTP 보안 헤더 누락 여부 확인"""
    findings = []
    security_headers = {
        'X-Frame-Options': {
            'severity': 'MEDIUM',
            'type': 'CLICKJACKING',
            'description': 'Clickjacking 방어 헤더 누락'
        },
        'X-Content-Type-Options': {
            'severity': 'LOW',
            'type': 'MIME_SNIFFING',
            'description': 'MIME 타입 스니핑 방어 헤더 누락'
        },
        'Strict-Transport-Security': {
            'severity': 'HIGH',
            'type': 'HSTS_MISSING',
            'description': 'HTTPS 강제 헤더 누락 (HTTPS 사이트인 경우 중요)'
        },
        'Content-Security-Policy': {
            'severity': 'MEDIUM',
            'type': 'CSP_MISSING',
            'description': 'XSS 방어를 위한 CSP 헤더 누락'
        },
        'X-XSS-Protection': {
            'severity': 'LOW',
            'type': 'XSS_PROTECTION_MISSING',
            'description': '브라우저 XSS 필터 헤더 누락 (구형 브라우저용)'
        }
    }

    for header, info in security_headers.items():
        if header not in response.headers:
            findings.append({
                "type": info['type'],
                "severity": info['severity'],
                "pattern": f"{header} 헤더 없음",
                "confidence": 0.95,
                "details": info['description'],
                "location": target_url
            })
    
    return findings

# ========================================
# Form 입력 필드 테스트
# ========================================
def _test_forms(soup, target_url):
    """폼 입력 필드에 페이로드 주입 테스트"""
    findings = []
    forms = soup.find_all('form')
    
    # 테스트할 페이로드 (카테고리별로 대표 2개씩)
    payloads = [
        ("<script>alert('xss')</script>", "XSS"),
        ("<img src=x onerror=alert(1)>", "XSS"),
        ("' OR 1=1--", "SQLi"),
        ("1' UNION SELECT NULL--", "SQLi"),
        ("../../../etc/passwd", "PATH_TRAVERSAL"),
        ("..\\..\\..\\windows\\system32\\config\\sam", "PATH_TRAVERSAL"),
        ("; whoami", "COMMAND_INJECTION"),
        ("| cat /etc/passwd", "COMMAND_INJECTION"),
        ("$(whoami)", "COMMAND_INJECTION"),
        ("{{7*7}}", "SSTI"),
        ("{{config}}", "SSTI")
    ]

    for form_idx, form in enumerate(forms):
        action = form.get('action', '')
        method = form.get('method', 'get').lower()
        inputs = form.find_all(['input', 'textarea', 'select'])
        
        # Form별로 발견된 취약점 타입 추적 (중복 방지)
        form_vulns = set()
        
        for input_tag in inputs:
            input_name = input_tag.get('name')
            input_type = input_tag.get('type', 'text')
            
            if not input_name or input_type in ['submit', 'button', 'reset', 'hidden']:
                continue

            # 입력 필드별로 발견된 취약점 타입 추적
            field_vulns = set()
            
            # 각 페이로드 테스트
            for payload, expected_type in payloads:
                # 이미 이 필드에서 같은 타입의 취약점을 찾았으면 스킵
                if expected_type in field_vulns:
                    continue
                
                # ML 모델로 페이로드 분류
                predicted_type, confidence = predictor.predict(payload)
                
                # 신뢰도 임계값 낮춤 (0.7 → 0.65)
                if predicted_type != "Benign" and confidence > 0.65:
                    # 같은 Form에서 같은 타입의 취약점은 한 번만 보고
                    vuln_key = f"{form_idx}_{predicted_type}"
                    if vuln_key not in form_vulns:
                        findings.append({
                            "type": predicted_type,
                            "severity": _get_severity(predicted_type),
                            "pattern": payload,
                            "confidence": round(float(confidence), 2),
                            "details": f"Form input '{input_name}' (type: {input_type})에서 {predicted_type} 취약점 가능성",
                            "location": f"{target_url} - Form #{form_idx+1} action: {action or '(동일 페이지)'} ({method.upper()})"
                        })
                        field_vulns.add(predicted_type)
                        form_vulns.add(vuln_key)
    
    return findings

# ========================================
# URL 파라미터 테스트 (대폭 개선)
# ========================================
def _test_url_parameters(soup, target_url):
    """페이지 내 링크 + Form action URL의 파라미터를 수집하고 테스트"""
    findings = []
    
    # 1. 페이지 내 모든 링크 수집
    links = soup.find_all('a', href=True)
    
    # 2. Form의 action URL도 추가 (★ 신규)
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action')
        if action:
            links.append({'href': action})
    
    tested_params = {}  # {(url_base, param_name): set(tested_types)}
    
    # 테스트할 페이로드 (더 다양하게)
    payloads = [
        ("<script>alert(1)</script>", "XSS"),
        ("<img src=x onerror=alert(1)>", "XSS"),
        ("' OR '1'='1", "SQLi"),
        ("1' UNION SELECT NULL--", "SQLi"),
        ("../../../etc/passwd", "PATH_TRAVERSAL"),
        ("; whoami", "COMMAND_INJECTION"),
        ("| cat /etc/passwd", "COMMAND_INJECTION"),
        ("$(id)", "COMMAND_INJECTION"),
        ("`whoami`", "COMMAND_INJECTION")
    ]
    
    print(f"  → URL 파라미터 분석: {len(links)}개 URL 발견 (링크 + Form action)")
    param_count = 0
    
    for link in links[:100]:  # 최대 100개까지 확장
        href = link.get('href') if isinstance(link, dict) else link.get('href')
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
            
        absolute_url = urljoin(target_url, href)
        
        # URL 파싱
        parsed = urlparse(absolute_url)
        url_base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # GET 파라미터가 없으면 스킵
        if not parsed.query:
            continue
        
        # 쿼리 파라미터 추출
        params = parse_qs(parsed.query, keep_blank_values=True)
        param_count += len(params)
        
        print(f"    - {url_base} : {list(params.keys())}")
        
        for param_name, param_values in params.items():
            # 파라미터별로 테스트한 취약점 타입 추적
            param_key = (url_base, param_name)
            if param_key not in tested_params:
                tested_params[param_key] = set()
            
            # 각 페이로드로 테스트
            for payload, expected_type in payloads:
                # 이미 이 파라미터에서 같은 타입을 테스트했으면 스킵
                if expected_type in tested_params[param_key]:
                    continue
                
                # ML 모델로 페이로드 분류
                predicted_type, confidence = predictor.predict(payload)
                
                # 신뢰도 임계값 낮춤 (0.7 → 0.65)
                if predicted_type != "Benign" and confidence > 0.65:
                    findings.append({
                        "type": predicted_type,
                        "severity": _get_severity(predicted_type),
                        "pattern": payload,
                        "confidence": round(float(confidence), 2),
                        "details": f"URL 파라미터 '{param_name}'에서 {predicted_type} 취약점 가능성",
                        "location": f"{url_base}?{param_name}=..."
                    })
                    tested_params[param_key].add(predicted_type)
    
    print(f"  → URL 파라미터 분석 완료: {param_count}개 파라미터 검사, {len(findings)}개 취약점 발견")
    return findings

# ========================================
# 민감 정보 노출 검사
# ========================================
def _check_sensitive_info(response, target_url):
    """응답 내용에서 민감 정보 노출 여부 확인"""
    findings = []
    content = response.text
    
    # 민감 정보 패턴
    sensitive_patterns = {
        'API_KEY': r'(api[_-]?key|apikey|access[_-]?token)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        'AWS_KEY': r'AKIA[0-9A-Z]{16}',
        'PRIVATE_KEY': r'-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----',
        'JWT_TOKEN': r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}',
        'DATABASE_URI': r'(mysql|postgresql|mongodb)://[^\s\'"<>]+',
    }
    
    import re
    for info_type, pattern in sensitive_patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            sample = str(matches[0])[:50]
            findings.append({
                "type": f"SENSITIVE_INFO_{info_type}",
                "severity": "HIGH",
                "pattern": f"{info_type} 패턴 발견",
                "confidence": 0.9,
                "details": f"민감 정보({info_type}) 노출 가능성 - 샘플: {sample}...",
                "location": target_url
            })
    
    return findings

# ========================================
# 중복 제거
# ========================================
def _deduplicate_findings(findings):
    """동일한 location과 type을 가진 취약점 중복 제거"""
    seen = set()
    unique_findings = []
    
    for finding in findings:
        key = (finding['location'], finding['type'])
        if key not in seen:
            seen.add(key)
            unique_findings.append(finding)
    
    # 심각도 순으로 정렬
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    unique_findings.sort(key=lambda x: (severity_order.get(x['severity'], 4), -x['confidence']))
    
    return unique_findings

# ========================================
# 심각도 결정 헬퍼 함수
# ========================================
def _get_severity(vuln_type):
    """취약점 타입에 따른 심각도 반환"""
    severity_map = {
        'XSS': 'HIGH',
        'SQLi': 'CRITICAL',
        'SQL_INJECTION': 'CRITICAL',
        'COMMAND_INJECTION': 'CRITICAL',
        'PATH_TRAVERSAL': 'HIGH',
        'XXE': 'HIGH',
        'SSTI': 'CRITICAL',
        'CLICKJACKING': 'MEDIUM',
        'CSRF': 'MEDIUM',
        'IDOR': 'HIGH',
        'MIME_SNIFFING': 'LOW',
        'HSTS_MISSING': 'MEDIUM',
        'CSP_MISSING': 'MEDIUM',
        'XSS_PROTECTION_MISSING': 'LOW'
    }
    return severity_map.get(vuln_type, 'MEDIUM')