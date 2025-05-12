from datetime import datetime
from typing import List

from sqlalchemy import Table, MetaData, select, and_, or_
from sqlalchemy.orm import Session

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.database import engine
from app.models.response import JobRecommendation, RecommendationResponse

# 메타데이터에 테이블 반영
metadata               = MetaData()
profile_tbl            = Table("profile", metadata, autoload_with=engine)
jobposting_tbl         = Table("jobPosting", metadata, autoload_with=engine)
jobposting_jobcat_tbl  = Table("jobPostingJobCategory", metadata, autoload_with=engine)
company_tbl            = Table("company", metadata, autoload_with=engine)
location_tbl           = Table("location", metadata, autoload_with=engine)

def recommend_jobs(profile_id: int, db: Session) -> RecommendationResponse:
    # 0. Profile 조회
    prof = db.execute(
        select(profile_tbl).where(profile_tbl.c.id == profile_id)
    ).mappings().first()
    if not prof:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    # 프로필 정보
    experience_level    = prof["experienceLevel"]
    education_level     = prof["educationLevel"]
    raw_skills          = prof["skills"] or ""
    desired_cat_id      = prof["desiredJobCategoryId"]
    desired_loc_id      = prof["desiredLocationId"]
    desired_salary_code = prof["desiredSalaryCode"] or 0

    # 1. 프로필의 지역 정보 가져오기
    loc = db.execute(
        select(location_tbl).where(location_tbl.c.id == desired_loc_id)
    ).mappings().first()
    if not loc:
        return RecommendationResponse(total=0, recommendations=[])
    desired_loc_code = loc["locationCode"]     # ex: '101010'
    desired_province = loc["province"]         # ex: '서울특별시'

    # province_prefix: locationCode 앞 세 글자(ex '101')
    province_prefix = desired_loc_code[:3]

    # 2. 만료되지 않고(status=2) 활성 + 지역(같은 구 or 같은 도/광역시) 필터
    now = datetime.utcnow()
    postings = db.execute(
        select(jobposting_tbl).where(
            and_(
                jobposting_tbl.c.status == 2,
                jobposting_tbl.c.expirationDate > now,
                or_(
                    jobposting_tbl.c.locationCode == desired_loc_code,
                    jobposting_tbl.c.locationCode.like(f"{province_prefix}%")
                )
            )
        )
    ).mappings().all()

    # 프로필 스킬 셋
    profile_skills = { s.strip() for s in raw_skills.split(",") if s.strip() }

    results: List[JobRecommendation] = []

    for jp in postings:
        # 3~4. 경험·학력 완전 일치
        if jp["experienceLevel"] != experience_level \
                or jp["educationLevel"] != education_level:
            continue

        # 5. 스킬 유사도 → 코사인 유사도 계산
        job_keywords = { k.strip() for k in (jp["keyword"] or "").split(",") if k.strip() }
        if not job_keywords or not profile_skills:
            continue

        profile_text = " ".join(profile_skills)
        job_text     = " ".join(job_keywords)

        vectorizer = CountVectorizer().fit([profile_text, job_text])
        vecs       = vectorizer.transform([profile_text, job_text])
        cos_sim    = cosine_similarity(vecs[0:1], vecs[1:])[0][0]
        if cos_sim == 0:
            continue  # 스킬 유사도 전혀 없으면 제외

        # 6. 직무 카테고리 매칭
        cat_ids   = db.execute(
            select(jobposting_jobcat_tbl.c.jobCategoryId)
            .where(jobposting_jobcat_tbl.c.jobPostingId == jp["id"])
        ).scalars().all()
        cat_score = 1 if desired_cat_id in cat_ids else 0
        if cat_score == 0:
            continue  # 직무 불일치 시 제외

        # 7. 지역 스코어링: same 구=1.0, same 도/광역시=0.5
        if jp["locationCode"] == desired_loc_code:
            local_score = 1.0
        else:
            local_score = 0.5

        # 8. 연봉 조건 만족 여부
        salary_score = 1 if jp["salaryCode"] >= desired_salary_code else 0

        # 9. raw score 계산 (최대: 1.0 + 1 + 1 + 1 = 4.0)
        raw_score = cos_sim + cat_score + salary_score + local_score

        # 10. 100점 만점으로 스케일링
        scaled = max(0, round((raw_score / 4) * 100))

        # 11. 회사 정보 조회
        comp = db.execute(
            select(company_tbl).where(company_tbl.c.id == jp["companyId"])
        ).mappings().first()
        company_info = {
            "id":      comp["id"],
            "name":    comp["name"],
            "address": comp["address"],
        }

        results.append(JobRecommendation(
            jobPostingId=jp["id"],
            title=jp["title"],
            score=scaled,
            industry=jp["industry"],
            salaryRange=jp["salaryRange"],
            expirationDate=jp["expirationDate"],
            company=company_info
        ))

    # 점수 내림차순 정렬
    results.sort(key=lambda x: x.score, reverse=True)

    return RecommendationResponse(
        total=len(results),
        recommendations=results
    )
