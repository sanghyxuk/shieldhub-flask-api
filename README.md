# 🛡️ ShieldHub Flask API

AI 기반 웹 취약점 스캐너 - 머신러닝을 활용한 자동화된 보안 분석 시스템

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0+-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [API 사용법](#-api-사용법)
- [데이터셋](#-데이터셋)
- [아키텍처](#-아키텍처)
- [개발 로드맵](#-개발-로드맵)
- [기여하기](#-기여하기)

---

## 🎯 프로젝트 소개

**ShieldHub Flask API**는 머신러닝 기반의 웹 보안 취약점 자동 탐지 시스템입니다. 

### 핵심 가치
- **🤖 AI 기반 탐지**: Random Forest 분류 모델을 사용한 지능형 패턴 인식
- **⚡ 실시간 분석**: 웹사이트 URL 입력 즉시 자동 스캔 시작
- **📊 정확한 분류**: 599개 학습 데이터로 훈련된 고신뢰도 모델
- **🎯 7가지 취약점 탐지**: XSS, SQLi, SSTI, Command Injection, Path Traversal, XXE, 보안 헤더 누락

### 사용 사례
- 웹 애플리케이션 보안 진단
- CI/CD 파이프라인 보안 검증
- 취약점 자동 리포팅 시스템
- 보안 교육 및 연구 목적

---

## ✨ 주요 기능

### 1. 🔍 능동적 취약점 스캔
- **Form 입력 필드 분석**: 자동으로 페이로드 주입 테스트
- **URL 파라미터 검사**: GET 파라미터에 대한 취약점 탐지
- **11가지 공격 패턴**: 실전 공격 시나리오 기반 테스트

### 2. 🛡️ 수동적 보안 검사
- **HTTP 보안 헤더 검증**: 5가지 필수 헤더 누락 확인
  - X-Frame-Options (Clickjacking 방어)
  - X-Content-Type-Options (MIME Sniffing 방어)
  - Strict-Transport-Security (HTTPS 강제)
  - Content-Security-Policy (XSS 방어)
  - X-XSS-Protection (브라우저 XSS 필터)
  
- **민감 정보 노출 탐지**
  - API Key, AWS Key, Private Key
  - JWT Token, Database URI
  - 정규식 기반 패턴 매칭

### 3. 🤖 머신러닝 기반 분류
- **TF-IDF Vectorization**: 텍스트를 수치 벡터로 변환
- **Random Forest Classifier**: 85%+ 정확도
- **실시간 예측**: 서버 시작 시 모델 로드 후 즉시 사용

### 4. 📊 상세 리포팅
```json
{
  "success": true,
  "url": "http://example.com",
  "vulnerability_count": 5,
  "vulnerabilities": [
    {
      "type": "SQLi",
      "severity": "CRITICAL",
      "confidence": 0.96,
      "pattern": "' OR 1=1--",
      "details": "Form input 'username' (type: text)에서 SQLi 취약점 가능성",
      "location": "http://example.com - Form #1"
    }
  ]
}
```

---

## 🛠️ 기술 스택

### Backend Framework
- **Flask 2.0+**: 경량 웹 프레임워크
- **Gunicorn**: WSGI HTTP 서버 (프로덕션 배포용)

### Machine Learning
- **scikit-learn**: 머신러닝 모델 학습 및 예측
  - `RandomForestClassifier`: 분류 모델
  - `TfidfVectorizer`: 텍스트 전처리
- **pandas**: 데이터 처리
- **numpy**: 수치 연산
- **joblib**: 모델 저장/로드

### Web Scraping & Analysis
- **Requests**: HTTP 요청 처리
- **BeautifulSoup4**: HTML 파싱 및 분석

### Additional
- **TensorFlow**: (향후 딥러닝 모델 확장용)

---

## 📂 프로젝트 구조

```
shieldhub-flask-api/
│
├── 📁 app/                          # 메인 애플리케이션 패키지
│   ├── __init__.py                  # Flask 앱 팩토리 (create_app)
│   ├── routes.py                    # API 엔드포인트 정의
│   │
│   ├── 📁 models/                   # 학습된 ML 모델 저장 폴더
│   │   ├── web_vuln_model.pkl       # Random Forest 모델 (학습 후 생성)
│   │   └── tfidf_vectorizer.pkl     # TF-IDF Vectorizer (학습 후 생성)
│   │
│   └── 📁 modules/                  # 핵심 기능 모듈
│       ├── __init__.py
│       ├── predictor.py             # ML 모델 로드 및 예측
│       └── scanner.py               # 웹 취약점 스캐너 로직
│
├── 📄 run.py                        # Flask 서버 진입점 (개발용)
├── 📄 train_model.py                # ML 모델 학습 스크립트
├── 📄 training_data.csv             # 학습 데이터셋 (599개 샘플)
├── 📄 requirements.txt              # Python 의존성 패키지
├── 📄 README.md                     # 프로젝트 문서 (현재 파일)
└── 📁 venv/                         # 가상환경 (Git 제외)
```

### 주요 파일 설명

#### 🔹 `run.py`
```python
# Flask 서버 실행 진입점
# 개발 환경에서 사용 (python run.py)
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

#### 🔹 `app/__init__.py`
- Flask 애플리케이션 팩토리 패턴 구현
- 서버 시작 시 ML 모델 자동 로드
- Blueprint 등록 (API 라우트)

#### 🔹 `app/routes.py`
- `/api/health`: 헬스 체크 (GET)
- `/api/analyze`: URL 분석 메인 엔드포인트 (POST)

#### 🔹 `app/modules/predictor.py`
- `load_model()`: 모델 메모리 로드
- `predict(text)`: 페이로드 분류 및 신뢰도 반환

#### 🔹 `app/modules/scanner.py`
- `analyze_site(url)`: 메인 스캔 함수
- `_check_security_headers()`: 보안 헤더 검사
- `_test_forms()`: Form 필드 테스트
- `_test_url_parameters()`: URL 파라미터 테스트
- `_check_sensitive_info()`: 민감 정보 탐지
- `_deduplicate_findings()`: 중복 제거 및 정렬

#### 🔹 `train_model.py`
- 학습 데이터 로드 (`training_data.csv`)
- TF-IDF 벡터화 (char_wb, ngram 2-5)
- Random Forest 모델 학습 (100 estimators)
- 모델 저장 (`app/models/*.pkl`)
- 성능 평가 (classification report)

#### 🔹 `training_data.csv`
```csv
text,label
"<script>alert('XSS')</script>",XSS
"' OR 1=1--",SQLi
"; whoami",COMMAND_INJECTION
...
```

---

## 🚀 설치 및 실행

### 1️⃣ 필수 요구사항

- **Python 3.8 이상**
- **pip** (Python 패키지 관리자)
- **가상환경 권장** (venv 또는 conda)

### 2️⃣ 설치 과정

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/shieldhub-flask-api.git
cd shieldhub-flask-api

# 2. 가상환경 생성 및 활성화
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. ML 모델 학습 (최초 1회 필수)
python train_model.py
```

**출력 예시:**
```
1. training_data.csv 파일 로드 중...
총 599개의 샘플 로드 완료.
2. 텍스트 데이터 전처리 (TF-IDF Vectorizer) 중...
텍스트 벡터화 완료.
3. 훈련용/테스트용 데이터 분리 중...
4. Random Forest 모델 학습 중...
모델 학습 완료!

=== 테스트 데이터 성능 평가 ===
              precision    recall  f1-score   support

      Benign       0.92      0.88      0.90        26
COMMAND_INJECTION  0.88      0.94      0.91        16
...

✅ 모델 및 Vectorizer 저장 완료!
```

### 3️⃣ 서버 실행

```bash
# 개발 모드 (디버그 활성화)
python run.py

# 또는 프로덕션 모드 (Gunicorn 사용)
gunicorn -w 4 -b 0.0.0.0:5001 run:app
```

**성공 메시지:**
```
Flask 서버 시작: ML 모델 로딩을 시도합니다...
✅ 모델 로드 성공!
✅ Vectorizer 로드 성공!
 * Running on http://127.0.0.1:5001
```

---

## 📡 API 사용법

### Base URL
```
http://localhost:5001/api
```

### 1️⃣ 헬스 체크

**요청:**
```bash
curl -X GET http://localhost:5001/api/health
```

**응답:**
```json
{
  "status": "Flask AI Server is healthy and running"
}
```

### 2️⃣ URL 분석 (메인 기능)

**요청:**
```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://testphp.vulnweb.com/"
  }'
```

**응답:**
```json
{
  "success": true,
  "url": "http://testphp.vulnweb.com/",
  "vulnerability_count": 14,
  "vulnerabilities": [
    {
      "type": "COMMAND_INJECTION",
      "severity": "CRITICAL",
      "confidence": 1.0,
      "pattern": "; whoami",
      "details": "Form input 'searchFor' (type: text)에서 COMMAND_INJECTION 취약점 가능성",
      "location": "http://testphp.vulnweb.com/ - Form #1 action: search.php?test=query (POST)"
    },
    {
      "type": "SQLi",
      "severity": "CRITICAL",
      "confidence": 0.98,
      "pattern": "' OR 1=1--",
      "details": "Form input 'searchFor' (type: text)에서 SQLi 취약점 가능성",
      "location": "http://testphp.vulnweb.com/ - Form #1 action: search.php?test=query (POST)"
    },
    {
      "type": "XSS",
      "severity": "HIGH",
      "confidence": 0.98,
      "pattern": "<script>alert('xss')</script>",
      "details": "Form input 'searchFor' (type: text)에서 XSS 취약점 가능성",
      "location": "http://testphp.vulnweb.com/ - Form #1 action: search.php?test=query (POST)"
    },
    {
      "type": "HSTS_MISSING",
      "severity": "HIGH",
      "confidence": 0.95,
      "pattern": "Strict-Transport-Security 헤더 없음",
      "details": "HTTPS 강제 헤더 누락 (HTTPS 사이트인 경우 중요)",
      "location": "http://testphp.vulnweb.com/"
    },
    {
      "type": "CLICKJACKING",
      "severity": "MEDIUM",
      "confidence": 0.95,
      "pattern": "X-Frame-Options 헤더 없음",
      "details": "Clickjacking 방어 헤더 누락",
      "location": "http://testphp.vulnweb.com/"
    }
  ]
}
```

### 오류 응답

**1. URL 누락:**
```json
{
  "success": false,
  "message": "URL이 필요합니다"
}
```

**2. 연결 실패:**
```json
{
  "success": false,
  "message": "사이트에 연결할 수 없습니다: http://invalid-url.com"
}
```

---

## 📊 데이터셋

### 데이터 통계

| 카테고리 | 샘플 수 | 비율 |
|---------|--------|-----|
| **XSS** | 63개 | 10.5% |
| **SQLi** | 86개 | 14.4% |
| **COMMAND_INJECTION** | 80개 | 13.4% |
| **PATH_TRAVERSAL** | 79개 | 13.2% |
| **SSTI** | 82개 | 13.7% |
| **XXE** | 79개 | 13.2% |
| **Benign** | 130개 | 21.7% |
| **총계** | **599개** | 100% |

### 데이터 형식

```csv
text,label
"<script>alert('XSS')</script>",XSS
"<img src=x onerror=alert(1)>",XSS
"' OR 1=1--",SQLi
"1' UNION SELECT NULL--",SQLi
"; whoami",COMMAND_INJECTION
"| cat /etc/passwd",COMMAND_INJECTION
"../../../etc/passwd",PATH_TRAVERSAL
"{{7*7}}",SSTI
"<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",XXE
"admin",Benign
"/products/view?id=1024",Benign
```

### 데이터 수집 출처

- **공개 보안 데이터베이스**: OWASP Top 10, PayloadsAllTheThings
- **실전 공격 패턴**: 실제 침투 테스트 시나리오
- **인코딩 우회 기법**: URL 인코딩, 이중 인코딩, Unicode
- **정상 패턴**: 실제 웹 애플리케이션 입력값

---

## 🏗️ 아키텍처

### 시스템 흐름도

```
┌──────────────┐
│   Client     │ (Spring Boot / Frontend)
│  (HTTP POST) │
└──────┬───────┘
       │
       │ POST /api/analyze
       │ {"url": "http://example.com"}
       ▼
┌──────────────────────────────────────────┐
│         Flask Application                │
│  ┌────────────────────────────────────┐  │
│  │      routes.py (Blueprint)         │  │
│  │  - /api/health (GET)               │  │
│  │  - /api/analyze (POST)             │  │
│  └────────────┬───────────────────────┘  │
│               │                           │
│               ▼                           │
│  ┌────────────────────────────────────┐  │
│  │     scanner.py (스캔 로직)         │  │
│  │  1. HTTP 요청                      │  │
│  │  2. 보안 헤더 검사                 │  │
│  │  3. Form 필드 추출                 │  │
│  │  4. URL 파라미터 추출              │  │
│  │  5. 페이로드 주입                  │  │
│  └────────────┬───────────────────────┘  │
│               │                           │
│               ▼                           │
│  ┌────────────────────────────────────┐  │
│  │   predictor.py (ML 예측)          │  │
│  │  - TF-IDF 벡터화                   │  │
│  │  - Random Forest 분류              │  │
│  │  - 신뢰도 계산                     │  │
│  └────────────┬───────────────────────┘  │
│               │                           │
└───────────────┼───────────────────────────┘
                │
                ▼
         ┌──────────────┐
         │  JSON 응답    │
         │ (취약점 목록) │
         └──────────────┘
```

### ML 파이프라인

```
training_data.csv
       │
       ▼
┌─────────────────┐
│ Data Loading    │ (pandas)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Preprocessing   │ (TF-IDF)
│ - Tokenization  │
│ - Vectorization │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Training  │ (Random Forest)
│ - 80/20 Split   │
│ - Stratified    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Export    │ (joblib)
│ - model.pkl     │
│ - vectorizer.pkl│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Server Runtime  │
│ - Load Models   │
│ - Predict       │
└─────────────────┘
```

---

## 📈 개발 로드맵

### ✅ 완료 (v1.0)
- [x] Flask API 서버 구축
- [x] Random Forest 모델 학습
- [x] 7가지 취약점 탐지 (XSS, SQLi, SSTI, Command Injection, Path Traversal, XXE, 보안 헤더)
- [x] Form 입력 필드 분석
- [x] URL 파라미터 분석
- [x] 599개 균형 잡힌 학습 데이터
- [x] RESTful API 설계

### 🚧 진행 중 (v1.1)
- [ ] 응답 기반 검증 (False Positive 감소)
- [ ] 화이트리스트 기능 (안전한 사이트 제외)
- [ ] 로깅 시스템 구축
- [ ] 단위 테스트 작성

### 🔮 계획 (v2.0)
- [ ] 딥러닝 모델 (LSTM, BERT) 적용
- [ ] 학습 데이터 1000개 이상 확장
- [ ] 실시간 페이로드 전송 및 응답 분석
- [ ] Rate Limiting 구현
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인 구축

### 🌟 향후 확장 (v3.0)
- [ ] 대시보드 UI (React/Vue)
- [ ] 스케줄러 (주기적 스캔)
- [ ] 이메일 알림 기능
- [ ] PDF 리포트 생성
- [ ] 다국어 지원 (영어, 한국어)
- [ ] 클라우드 배포 (AWS, GCP)

---

## 🤝 기여하기

기여는 언제나 환영입니다! 다음 절차를 따라주세요:

### 1️⃣ Fork 및 Clone

```bash
# 1. GitHub에서 Fork 클릭
# 2. 본인의 저장소에서 Clone
git clone https://github.com/yourusername/shieldhub-flask-api.git
cd shieldhub-flask-api
```

### 2️⃣ 브랜치 생성

```bash
git checkout -b feature/new-vulnerability-detector
```

### 3️⃣ 개발 및 커밋

```bash
# 코드 수정 후
git add .
git commit -m "feat: Add CSRF vulnerability detection"
```

### 4️⃣ Pull Request

```bash
git push origin feature/new-vulnerability-detector
```

### 기여 가이드라인

- **코드 스타일**: PEP 8 준수
- **커밋 메시지**: Conventional Commits 형식
  - `feat:` 새로운 기능
  - `fix:` 버그 수정
  - `docs:` 문서 업데이트
  - `refactor:` 코드 리팩토링
  - `test:` 테스트 추가
- **테스트**: 새로운 기능 추가 시 테스트 코드 포함
- **문서화**: README 업데이트 필수

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---

## 👥 제작자

**ShieldHub Team**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: contact@shieldhub.com

---

## 🙏 감사의 말

- **OWASP Foundation**: 보안 지식 및 공개 데이터
- **scikit-learn Community**: 강력한 ML 라이브러리
- **Flask Team**: 간결한 웹 프레임워크
- **모든 기여자 및 스타를 준 분들**: 프로젝트 발전에 큰 힘이 됩니다!

---

## 📚 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [BeautifulSoup4 Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요! ⭐**

Made with ❤️ by ShieldHub Team

</div>
