import joblib
import os

# --- 1. 모델 및 Vectorizer 파일 경로 정의 ---
# train_model.py가 생성하는 파일 경로와 동일해야 합니다.
MODEL_PATH = 'app/models/web_vuln_model.pkl'
VECTORIZER_PATH = 'app/models/tfidf_vectorizer.pkl'

# --- 2. 학습된 모델/Vectorizer를 저장할 전역 변수 ---
model = None
vectorizer = None

def load_model():
    """
    서버 시작 시(app/__init__.py에서 호출)
    app/models/ 폴더에서 실제 훈련된 모델과 Vectorizer를 로드합니다.
    """
    global model, vectorizer
    
    try:
        # 파일 존재 여부 확인
        if not os.path.exists(VECTORIZER_PATH) or not os.path.exists(MODEL_PATH):
            print("="*50)
            print("경고: 훈련된 모델 파일을 찾을 수 없습니다.")
            print(f"'{VECTORIZER_PATH}' 또는 '{MODEL_PATH}' 파일이 필요합니다.")
            print("먼저 프로젝트 루트에서 'python train_model.py'를 실행하세요.")
            print("="*50)
            # 파일이 없으면 서버는 실행되지만 예측은 비활성화됩니다.
            model = None
            vectorizer = None
            return

        print("Flask 서버 시작: ML 모델 로딩을 시도합니다...")
        
        # 1. 텍스트 변환기(Vectorizer) 로드
        print(f"1. Vectorizer 로드 중... ({VECTORIZER_PATH})")
        vectorizer = joblib.load(VECTORIZER_PATH)
        
        # 2. AI 모델(RandomForest) 로드
        print(f"2. Model 로드 중... ({MODEL_PATH})")
        model = joblib.load(MODEL_PATH)
        
        print("성공: Vectorizer와 Model이 메모리에 로드되었습니다.")

    except Exception as e:
        print(f"모델 로드 중 심각한 오류 발생: {e}")
        model = None
        vectorizer = None

def predict(text_data):
    """
    로드된 모델을 사용하여 텍스트 데이터의 취약점을 예측합니다.
    (scanner.py에서 이 함수를 호출합니다)
    """
    # 1. 모델 로드 실패 시, 안전하게 '정상'으로 응답
    if model is None or vectorizer is None:
        print("오류: 모델이 로드되지 않아 예측을 수행할 수 없습니다.")
        return "Benign", 0.0 

    try:
        # 2. 입력된 텍스트(str)를 리스트로 감싸기
        # (TfidfVectorizer.transform은 iterable(리스트 등)을 입력으로 받음)
        text_list = [str(text_data)]
        
        # 3. (중요) 훈련 때 사용한 '그 Vectorizer'로 텍스트를 숫자 벡터로 변환
        X_vectorized = vectorizer.transform(text_list)
        
        # 4. (중요) 모델을 사용하여 각 클래스('Benign', 'XSS' 등)의 확률 예측
        # model.predict() -> 클래스 이름만 반환
        # model.predict_proba() -> 각 클래스일 확률을 반환
        probabilities = model.predict_proba(X_vectorized)[0]
        
        # 5. 가장 높은 확률과 해당 클래스 이름 찾기
        max_probability = probabilities.max()
        predicted_class_index = probabilities.argmax()
        predicted_class = model.classes_[predicted_class_index]
        
        # 6. 예측된 클래스와 신뢰도(확률) 반환
        return predicted_class, float(max_probability)

    except Exception as e:
        print(f"예측 중 오류 발생: {e}")
        # 예측 실패 시, 안전하게 '정상'으로 응답
        return "Benign", 0.0