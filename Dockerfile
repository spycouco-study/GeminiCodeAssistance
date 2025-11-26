# Python 3.11 베이스 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 도구 설치
# ffmpeg: 비디오/오디오 처리를 위해 필요
# nodejs, npm: TypeScript 컴파일을 위해 필요
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g typescript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정 (기본값)
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행(배포용)
#CMD ["uvicorn", "gemini:app", "--host", "0.0.0.0", "--port", "8000"]
# 애플리케이션 실행(개발용)
CMD ["uvicorn", "gemini:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
