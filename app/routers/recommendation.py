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
    description="profile_id를 받아 조건에 맞춰 점수를 계산한 뒤, 내림차순 정렬하여 반환합니다."
)
def recommendation_endpoint(
        profile_id: int,
        db: Session = Depends(get_db),
):
    resp = recommend_jobs(profile_id, db)
    if resp.total == 0:
        # 공고가 하나도 없을 때도 200 으로 빈 리스트 반환
        return resp
    return resp
