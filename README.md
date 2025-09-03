# 🚀 Meet U, Career - AI Service

FastAPI 기반의 커리어 매칭 플랫폼 'Meet U, Career'의 AI 서비스입니다.

---

## 📌 프로젝트 내 역할 및 개요

이 AI 서비스는 'Meet U, Career' 프로젝트의 핵심 기능 중 하나로, **다른 팀원들이 전담하여 개발했습니다.**

자기소개서 AI 코칭, 맞춤형 채용공고 추천, 이력서 키워드 추출 등 AI 기반 기능을 제공하는 독립 API 서버입니다. 저는 이 AI 서비스와 연동하는 **백엔드 API 및 프론트엔드 화면 개발을 담당**했으며, 전체 프로젝트 아키텍처의 이해를 돕기 위해 이 저장소를 함께 첨부합니다.

---

## ⚙️ 주요 기술 스택

- **Framework**: FastAPI
- **Language**: Python
- **AI/ML**: OpenAI GPT API
- **Deployment**: Docker, AWS EC2, GitHub Actions

---

## 🧩 아키텍처
Spring Boot 기반의 메인 백엔드 서버가 필요에 따라 AI 서비스의 API를 호출하여, 자기소개서 코칭 및 공고 추천 등의 결과를 받아 사용자에게 제공하는 구조입니다.

`[Backend (Spring Boot)] ↔ [AI Service (FastAPI)] ↔ [OpenAI API]`

---

## 🔗 관련 레포지토리

- **Backend Repository (담당)**: [meet-u-career-backend](https://github.com/dpdlcl01/meet-u-career-backend)
- **Frontend Repository (담당)**: [meet-u-career-frontend](https://github.com/dpdlcl01/meet-u-career-frontend)