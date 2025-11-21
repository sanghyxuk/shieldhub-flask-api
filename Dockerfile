FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# requirements 먼저 복사 (캐싱 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# gunicorn 설치
RUN pip install --no-cache-dir gunicorn

# 애플리케이션 코드 전체 복사 (app 디렉토리 안에 models 포함)
COPY app/ ./app/
COPY run.py .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PORT=5001

# 포트 노출
EXPOSE $PORT

# gunicorn으로 실행 (JSON 형식 권장)
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120"]