from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.recommendation import recommend_jobs
from app.models.response import RecommendationResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/recommendations/{profile_id}",
    response_model=RecommendationResponse,
    summary="프로필 기반 채용공고 추천",
    description="profile_id를 받아 Python 기반 코사인 유사도 + 직무 매칭 + 연봉 페널티 + 지역 계층 매칭을 계산하여 내림차순 정렬 후 반환합니다."
)
def recommendation_endpoint(
        profile_id: int,
        db: Session = Depends(get_db),
):
    resp = recommend_jobs(profile_id, db)
    return resp
