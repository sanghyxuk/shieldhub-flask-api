import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib # 모델 저장을 위해 joblib 사용

# --- 1. 데이터 로드 ---
print("1. training_data.csv 파일 로드 중...")
try:
    data = pd.read_csv('training_data.csv')
    # 비어있는 데이터(NaN)가 있다면 'Benign'으로 간주하여 채움
    data.fillna("Benign", inplace=True) 
except FileNotFoundError:
    print("오류: 'training_data.csv' 파일을 찾을 수 없습니다.")
    print("스크립트를 종료합니다.")
    exit()

# X (입력 텍스트), y (정답 레이블) 분리
X = data['text']
y = data['label']

print(f"총 {len(data)}개의 샘플 로드 완료.")

# --- 2. 데이터 전처리 (텍스트 -> 숫자 벡터) ---
print("2. 텍스트 데이터 전처리 (TF-IDF Vectorizer) 중...")

# TfidfVectorizer 객체 생성
# analyzer='char_wb': 단어(word)와 글자(char) 경계(wb)를 모두 고려하여
# <script> 같은 패턴을 더 잘 잡아내도록 설정
vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), max_features=1500)

# 훈련 데이터(X)를 기반으로 Vectorizer를 학습(fit)시키고 변환(transform)
X_vectorized = vectorizer.fit_transform(X)

print("텍스트 벡터화 완료.")

# --- 3. 훈련 / 테스트 데이터 분리 ---
print("3. 훈련용/테스트용 데이터 분리 중...")
# 80%는 훈련용, 20%는 테스트용으로 분리
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized, 
    y, 
    test_size=0.2, 
    random_state=42, # 결과를 동일하게 유지하기 위한 시드값
    stratify=y # 레이블 비율을 유지하며 분리 (중요!)
)

# --- 4. 머신러닝 모델 학습 (Random Forest) ---
print("4. Random Forest 모델 학습 중... (샘플이 적어 금방 끝납니다)")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("모델 학습 완료.")

# --- 5. 모델 성능 평가 ---
print("5. 모델 성능 평가 (테스트 데이터 사용)...")
y_pred = model.predict(X_test)

# 정밀도(Precision), 재현율(Recall), F1-점수(F1-Score) 출력
# (Benign이 아닌 XSS, SQLi를 얼마나 잘 맞추는지 확인)
report = classification_report(y_test, y_pred)
print("\n--- 모델 평가 리포트 ---")
print(report)
print("------------------------\n")

# --- 6. 모델 및 Vectorizer 저장 ---
print("6. 학습된 모델과 Vectorizer를 파일로 저장 중...")

# app/models/ 폴더가 없다면 생성 (선택적)
import os
if not os.path.exists('app/models'):
    os.makedirs('app/models')

# 1. 학습된 AI 모델 저장
joblib.dump(model, 'app/models/web_vuln_model.pkl')
# 2. 텍스트 변환기(Vectorizer) 저장 (★중요★)
# (새로운 요청이 왔을 때 훈련 때와 '똑같은' 방식으로 숫자로 바꿔야 함)
joblib.dump(vectorizer, 'app/models/tfidf_vectorizer.pkl')

print("성공! 'app/models/' 폴더에 다음 파일이 생성되었습니다:")
print("- web_vuln_model.pkl")
print("- tfidf_vectorizer.pkl")
print("\n이제 predictor.py 파일을 수정하여 이 모델들을 사용하세요.")