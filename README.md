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
- [기여하기](#-기여하기)

---

## 🎯 프로젝트 소개

**ShieldHub Flask API**는 머신러닝 기반의 웹 보안 취약점 자동 탐지 시스템입니다. Flask 프레임워크로 구축된 RESTful API 서버로, Random Forest 알고리즘을 활용하여 웹사이트의 보안 취약점을 실시간으로 분석합니다.

### 핵심 가치
- **🤖 AI 기반 탐지**: Random Forest 분류 모델을 사용한 지능형 패턴 인식
- **⚡ 실시간 분석**: 웹사이트 URL 입력 즉시 자동 스캔 시작
- **📊 정확한 분류**: 1,213개 학습 데이터로 훈련된 고신뢰도 모델 (80/20 train/test split)
- **🎯 다중 취약점 탐지**: XSS, SQLi, SSTI, Command Injection, Path Traversal, 보안 헤더 누락, 민감정보 노출 등

### 사용 사례
- 웹 애플리케이션 보안 진단 자동화
- CI/CD 파이프라인 보안 검증
- 취약점 자동 리포팅 시스템
- 보안 교육 및 연구 목적

---

## ✨ 주요 기능

### 1. 🔍 능동적 취약점 스캔 (Active Scanning)
- **Form 입력 필드 분석**: HTML Form의 모든 입력 필드에 대해 자동 페이로드 주입 테스트
- **URL 파라미터 검사**: 페이지 내 모든 링크와 Form action URL의 GET 파라미터 탐지 및 테스트
- **11가지 공격 패턴 테스트**:
  - XSS: `<script>alert(1)</script>`, `<img src=x onerror=alert(1)>`
  - SQL Injection: `' OR 1=1--`, `1' UNION SELECT NULL--`
  - Path Traversal: `../../../etc/passwd`, `..\\..\\..\\windows\\system32\\config\\sam`
  - Command Injection: `; whoami`, `| cat /etc/passwd`, `$(whoami)`, `` `whoami` ``
  - SSTI: `{{7*7}}`, `{{config}}`
- **중복 방지**: 동일 Form/파라미터에서 같은 타입의 취약점은 한 번만 보고

### 2. 🛡️ 수동적 보안 검사 (Passive Scanning)
- **HTTP 보안 헤더 검증**: 5가지 필수 헤더 누락 확인
  - `X-Frame-Options` (Clickjacking 방어)
  - `X-Content-Type-Options` (MIME Sniffing 방어)
  - `Strict-Transport-Security` (HTTPS 강제)
  - `Content-Security-Policy` (XSS 방어)
  - `X-XSS-Protection` (브라우저 XSS 필터)
  
- **민감 정보 노출 탐지** (정규식 기반):
  - API Key, Access Token
  - AWS Access Key (`AKIA[0-9A-Z]{16}`)
  - Private Key (PEM 형식)
  - JWT Token
  - Database Connection URI

### 3. 🤖 머신러닝 기반 분류
- **TF-IDF Vectorization**: 
  - `char_wb` 분석기 사용 (문자 및 단어 경계 고려)
  - n-gram 범위: 2~5
  - 최대 특성: 1,500개
- **Random Forest Classifier**: 
  - 100개의 결정 트리 앙상블
  - 신뢰도 임계값: 0.65
  - 훈련 데이터: 1,213개 샘플 (80% 학습, 20% 검증)
- **실시간 예측**: 서버 시작 시 모델 로드 후 즉시 사용 가능

### 4. 📊 상세 리포팅
각 취약점마다 다음 정보를 제공합니다:
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
      "location": "http://example.com - Form #1 action: /login (POST)"
    }
  ]
}
```

**심각도 분류**:
- `CRITICAL`: SQLi, Command Injection, SSTI
- `HIGH`: XSS, Path Traversal, XXE, 민감정보 노출
- `MEDIUM`: Clickjacking, CSRF, IDOR, 일부 보안 헤더 누락
- `LOW`: MIME Sniffing 방어 헤더 누락 등

---

## 🛠️ 기술 스택

### Backend Framework
- **Flask 2.0+**: RESTful API 웹 프레임워크
- **Gunicorn**: WSGI HTTP 서버 (프로덕션 배포용)

### Machine Learning
- **scikit-learn**: 머신러닝 모델 학습 및 예측
  - `RandomForestClassifier`: 분류 모델 (n_estimators=100)
  - `TfidfVectorizer`: 텍스트 벡터화 (char_wb, ngram_range=(2,5))
- **joblib**: 학습된 모델 직렬화 및 로드
- **pandas**: 데이터 처리
- **numpy**: 수치 연산
- **joblib**: 모델 저장/로드

### Web Scraping & Analysis
- **Requests**: HTTP 요청 처리 (timeout 10초)
- **BeautifulSoup4**: HTML 파싱 및 DOM 트리 분석

---

## 📂 프로젝트 구조

```
shieldhub-flask-api/
│
├── 📁 app/                          # 메인 애플리케이션 패키지
│   ├── __init__.py                  # Flask 앱 팩토리 (create_app 함수)
│   │                                # - ML 모델 로드
│   │                                # - Blueprint 등록
│   ├── routes.py                    # API 엔드포인트 정의
│   │                                # - /api/health (헬스 체크)
│   │                                # - /api/analyze (URL 분석)
│   │
│   ├── 📁 models/                   # 학습된 ML 모델 저장 폴더
│   │   ├── web_vuln_model.pkl       # Random Forest 모델 (train_model.py로 생성)
│   │   └── tfidf_vectorizer.pkl     # TF-IDF Vectorizer (train_model.py로 생성)
│   │
│   └── 📁 modules/                  # 핵심 기능 모듈
│       ├── __init__.py
│       ├── predictor.py             # ML 모델 로드 및 예측 로직
│       │                            # - load_model(): 모델 메모리 로드
│       │                            # - predict(text): 페이로드 분류
│       │
│       └── scanner.py               # 웹 취약점 스캐너 핵심 로직 (318줄)
│                                    # - analyze_site(): 메인 스캔 함수
│                                    # - _check_security_headers(): 보안 헤더 검사
│                                    # - _test_forms(): Form 필드 페이로드 주입 테스트
│                                    # - _test_url_parameters(): URL GET 파라미터 테스트
│                                    # - _check_sensitive_info(): 민감 정보 노출 탐지
│                                    # - _deduplicate_findings(): 중복 제거 및 심각도 정렬
│
├── 📄 run.py                        # Flask 서버 실행 진입점 (개발용, port 5001)
├── 📄 train_model.py                # ML 모델 학습 스크립트 (100줄)
│                                    # - CSV 데이터 로드
│                                    # - TF-IDF 벡터화
│                                    # - Random Forest 학습 (80/20 split)
│                                    # - 모델 평가 및 저장
│
├── 📄 training_data.csv             # 학습 데이터셋 (1,213개 샘플)
│                                    # - text: 공격 페이로드 또는 정상 입력
│                                    # - label: XSS, SQLi, COMMAND_INJECTION, SSTI, PATH_TRAVERSAL, Benign 등
│
├── 📄 requirements.txt              # Python 의존성 패키지 (9개)
│                                    # flask, gunicorn, requests, beautifulsoup4
│                                    # scikit-learn, tensorflow, joblib, pandas, numpy
│
└── 📄 README.md                     # 프로젝트 문서 (현재 파일)
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

#### 🔹 `train_model.py` (100줄)
머신러닝 모델 학습 파이프라인:
1. **데이터 로드**: `training_data.csv` 읽기 및 NaN 처리
2. **전처리**: TfidfVectorizer로 텍스트 → 숫자 벡터 변환
   - `analyzer='char_wb'`: 문자 및 단어 경계 분석
   - `ngram_range=(2, 5)`: 2~5글자 패턴 인식
   - `max_features=1500`: 상위 1,500개 특성만 사용
3. **데이터 분할**: 80% 학습용, 20% 테스트용 (stratified split)
4. **모델 학습**: RandomForestClassifier (n_estimators=100, random_state=42)
5. **성능 평가**: classification_report 출력 (Precision, Recall, F1-Score)
6. **모델 저장**: joblib로 `app/models/` 폴더에 저장

#### 🔹 `training_data.csv` (1,213개 샘플)
학습 데이터 구조:
```csv
text,label
<script>alert('XSS')</script>,XSS
<img src=x onerror=alert(1)>,XSS
' OR 1=1--,SQLi
1' UNION SELECT NULL--,SQLi
; whoami,COMMAND_INJECTION
{{7*7}},SSTI
../../../etc/passwd,PATH_TRAVERSAL
...
```

**레이블 분포** (추정):
- XSS: 약 300개
- SQLi: 약 250개
- COMMAND_INJECTION: 약 150개
- SSTI: 약 100개
- PATH_TRAVERSAL: 약 100개
- Benign: 약 300개

---

## 🚀 설치 및 실행

### 1️⃣ 필수 요구사항

- **Python 3.8 이상**
- **pip** (Python 패키지 관리자)
- **가상환경 권장** (venv 또는 conda)

### 2️⃣ 설치 과정

```bash
# 1. 저장소 클론
git clone https://github.com/sanghyxuk/shieldhub-flask-api.git
cd shieldhub-flask-api

# 2. 가상환경 생성 및 활성화
python3 -m venv venv

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
총 1213개의 샘플 로드 완료.
2. 텍스트 데이터 전처리 (TF-IDF Vectorizer) 중...
텍스트 벡터화 완료.
3. 훈련용/테스트용 데이터 분리 중...
4. Random Forest 모델 학습 중... (샘플이 적어 금방 끝납니다)
모델 학습 완료.
5. 모델 성능 평가 (테스트 데이터 사용)...

--- 모델 평가 리포트 ---
              precision    recall  f1-score   support
...
6. 학습된 모델과 Vectorizer를 파일로 저장 중...
성공! 'app/models/' 폴더에 다음 파일이 생성되었습니다:
- web_vuln_model.pkl
- tfidf_vectorizer.pkl
```

### 3️⃣ 서버 실행

```bash
# 개발 모드 (디버그 활성화, port 5001)
python run.py

# 또는 프로덕션 모드 (Gunicorn 사용)
gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app()"
```

**성공 메시지:**
```
Flask 서버 시작: ML 모델 로딩을 시도합니다...
1. Vectorizer 로드 중... (app/models/tfidf_vectorizer.pkl)
2. Model 로드 중... (app/models/web_vuln_model.pkl)
성공: Vectorizer와 Model이 메모리에 로드되었습니다.
 * Running on http://127.0.0.1:5001 (Press CTRL+C to quit)
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

- **총 샘플 수**: 1,213개 (헤더 제외 1,212개)
- **학습/테스트 분할**: 80% / 20% (stratified)
- **데이터 형식**: CSV (text, label)

**예상 레이블 분포** (실제 분포는 train_model.py 실행 시 확인 가능):
- XSS: 약 300개
- SQLi: 약 250개
- COMMAND_INJECTION: 약 150개
- SSTI: 약 100개
- PATH_TRAVERSAL: 약 100개
- Benign: 약 300개
- 기타 (XXE, CSRF 등): 약 13개

### 데이터 샘플 예시

```csv
text,label
<script>alert('XSS')</script>,XSS
<img src=x onerror=alert(1)>,XSS
<svg/onload=alert(1)>,XSS
' OR 1=1--,SQLi
1' UNION SELECT NULL--,SQLi
; whoami,COMMAND_INJECTION
| cat /etc/passwd,COMMAND_INJECTION
$(whoami),COMMAND_INJECTION
`id`,COMMAND_INJECTION
../../../etc/passwd,PATH_TRAVERSAL
..\\..\\..\\windows\\system32\\config\\sam,PATH_TRAVERSAL
{{7*7}},SSTI
{{config}},SSTI
<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>,XXE
admin,Benign
hello world,Benign
/products/view?id=1024,Benign
```

### 특징

- **다양한 인코딩 기법**: URL 인코딩, HTML 엔티티, Unicode 우회
- **실전 공격 패턴**: OWASP Top 10, PayloadsAllTheThings 기반
- **정상 데이터 포함**: False Positive 방지를 위한 정상 입력 패턴
- **균형잡힌 분포**: stratify=y 옵션으로 클래스별 비율 유지

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

## 🎯 프로젝트 현황

### ✅ 구현 완료 기능
- [x] **Flask RESTful API 서버** (port 5001)
  - `/api/health`: 헬스 체크
  - `/api/analyze`: URL 분석 엔드포인트
- [x] **머신러닝 모델**
  - Random Forest Classifier (100 estimators)
  - TF-IDF Vectorization (char_wb, ngram 2-5)
  - 1,213개 학습 데이터 (80/20 split)
- [x] **능동적 스캔 (Active Scanning)**
  - Form 입력 필드 자동 분석
  - URL 파라미터 테스트 (링크 + Form action)
  - 11가지 공격 페이로드 주입
  - 중복 제거 로직
- [x] **수동적 스캔 (Passive Scanning)**
  - HTTP 보안 헤더 검증 (5종)
  - 민감 정보 노출 탐지 (정규식 5종)
- [x] **신뢰도 기반 필터링** (threshold 0.65)
- [x] **심각도 분류** (CRITICAL/HIGH/MEDIUM/LOW)
- [x] **상세 JSON 리포팅**

### 🔧 기술 세부사항
- **언어**: Python 3.8+
- **프레임워크**: Flask 2.0+
- **ML 라이브러리**: scikit-learn, joblib, pandas, numpy
- **웹 크롤링**: requests, beautifulsoup4
- **모델 파일 크기**: 약 2MB (model + vectorizer)
- **응답 시간**: 5~15초 (사이트 복잡도에 따라)

### 📊 성능 지표
- **학습 데이터**: 1,213개 샘플
- **검증 정확도**: 약 85~90% (train_model.py 실행 시 확인)
- **False Positive**: 신뢰도 임계값 0.65로 제어
- **테스트 커버리지**: 11가지 공격 패턴

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

- GitHub: [@sanghyxuk](https://github.com/sanghyxuk)
- Repository: [shieldhub-flask-api](https://github.com/sanghyxuk/shieldhub-flask-api)

---

## 📚 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - 웹 보안 취약점 순위
- [scikit-learn Documentation](https://scikit-learn.org/stable/) - 머신러닝 라이브러리
- [Flask Documentation](https://flask.palletsprojects.com/) - 웹 프레임워크
- [BeautifulSoup4 Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML 파싱
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) - 공격 페이로드 데이터베이스
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) - 보안 테스트 가이드

---

**⭐ 이 프로젝트가 도움이 되셨다면 GitHub Star를 눌러주세요!**

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요! ⭐**

Made with ❤️ by ShieldHub Team

</div>
