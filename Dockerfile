# [1] Python 베이스 이미지
FROM python:3.11-slim

# [2] 작업 디렉토리 설정
WORKDIR /app

# [3] requirements 설치
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# [4] 전체 앱 복사
COPY . .

# [5] 포트 열기
EXPOSE 8000

# [6] 실행 (compose에 이미 있으므로 생략 가능)
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
