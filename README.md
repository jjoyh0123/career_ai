# 🚀 Meet U, Career - AI Service

FastAPI 기반의 커리어 매칭 플랫폼 'Meet U, Career'의 AI 서비스입니다.

이 프로젝트는 자기소개서 작성 지원 및 코칭, 공고 추천 등 AI 기반 기능을 제공하는 독립적인 서비스로 개발되었습니다.


## 📌 서비스 개요

| 항목    | 설명                                       |
| ----- | ---------------------------------------- |
| 서비스명  | Meet U, Career AI Service                |
| 개발 기간 | 2025.03 ~ 2025.04                        |
| 주요 기능 | 자기소개서 AI 코칭, 맞춤형 채용공고 추천, 이력서 키워드 추출     |
| 기술 스택 | FastAPI, Python, OpenAI API, Docker, AWS |


## ⚙️ 기술 스택 및 아키텍처

### 🔧 사용 기술

- **Backend Framework**: FastAPI
- **Language**: Python 3.11
- **AI/ML**: OpenAI GPT API
- **Container**: Docker
- **CI/CD**: GitHub Actions
- **Deployment**: AWS EC2

| 분류    | 기술 스택                           |
| ----- | ------------------------------- |
| 백엔드   | FastAPI, Uvicorn                |
| AI/ML | OpenAI API                      |
| 배포    | Docker, GitHub Actions, AWS EC2 |
| 개발 환경 | Python 3.11, Poetry             |
| 연동    | Spring Boot API 연동              |


### 🧩 아키텍처 개요

```
[Backend (Spring Boot)] → [AI Service (FastAPI)]
                             ↳ OpenAI API 연동
                             ↳ ML 모델 서빙
                             ↳ Docker 컨테이너화
                             ↳ 배포: AWS EC2
```


## 💬 기술적 의사결정 사유

| 사용 기술      | 선택 사유 및 기술 설명                                                          |
| ---------- | ---------------------------------------------------------------------- |
| FastAPI    | 비동기 지원, 높은 성능, Python 기반으로 AI/ML 통합 용이, 자동 API 문서화 기능이 강점입니다.          |
| OpenAI API | 자기소개서 피드백에 필요한 자연어 처리 및 텍스트 생성 기능을 제공합니다. 기존 대비 더 정교한 피드백을 생성할 수 있습니다. |


## 📂 폴더 구조

```

```


## 🧪 실행 방법

1. 환경 변수 설정:
    `.env` 파일을 다음과 같이 설정합니다:
    ```
    # OpenAI API 설정
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    AI_MODEL=gpt-4
    ```
    
2. Poetry로 의존성 설치:
    ```bash
    poetry install
    ```
    
3. 서버 실행:
    ```bash
    poetry run uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    
4. Docker로 실행:
    ```bash
    docker-compose up -d
    ```
    

## 🚀 배포 방식

GitHub Actions를 통해 main 브랜치에 푸시 시 자동으로 Docker 이미지 빌드 및 EC2 배포가 이루어집니다.


## 🔄 Spring Boot 백엔드와의 연동

Spring Boot 백엔드에서 WebClient를 통해 AI 서비스 API를 호출하여 자기소개서 코칭 및 공고 추천 기능을 제공합니다.


## 📎 관련 레포지토리

- [meet-u-career-backend](https://github.com/dpdlcl01/meet-u-career-backend)
- [meet-u-career-frontend](https://github.com/dpdlcl01/meet-u-career-frontend)