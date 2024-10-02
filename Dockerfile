# 베이스 이미지 설정
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential file && rm -rf /var/lib/apt/lists/*


# 종속성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# 애플리케이션 코드 복사

COPY . /app

#RUN chmod +x /app/app/services/lib/compile.sh
RUN chmod +x /app/app/services/lib/seed_128_cbc/compile.sh && \
    sh /app/app/services/lib/seed_128_cbc/compile.sh && \
    ls -la /app/app/services/lib/seed_128_cbc/

# FastAPI 애플리케이션 실행
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["./entrypoint.sh"]
