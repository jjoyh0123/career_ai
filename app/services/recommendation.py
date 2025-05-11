from datetime import datetime
from fastapi import HTTPException
from typing import List

from sqlalchemy import Table, MetaData, select, and_
from sqlalchemy.orm import Session

from app.database import engine
from app.models.response import JobRecommendation, RecommendationResponse

# 메타데이터에 테이블 반영
metadata = MetaData()
profile_tbl = Table("profile", metadata, autoload_with=engine)
jobposting_tbl = Table("jobPosting", metadata, autoload_with=engine)
jobposting_jobcat_tbl = Table("jobPostingJobCategory", metadata, autoload_with=engine)
company_tbl = Table("company", metadata, autoload_with=engine)
location_tbl = Table("location", metadata, autoload_with=engine)


def recommend_jobs(profile_id: int, db: Session) -> RecommendationResponse:
    # 0. Profile 조회
    prof_row = db.execute(
        select(profile_tbl).where(profile_tbl.c.id == profile_id)
    ).mappings().first()
    if not prof_row:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    # 프로필 정보
    experience_level    = prof_row["experienceLevel"]
    education_level     = prof_row["educationLevel"]
    raw_skills          = prof_row["skills"] or ""
    desired_cat_id      = prof_row["desiredJobCategoryId"]
    desired_loc_id      = prof_row["desiredLocationId"]
    desired_salary_code = prof_row["desiredSalaryCode"] or 0

    # 7. desiredLocationId → locationCode
    loc_row = db.execute(
        select(location_tbl).where(location_tbl.c.id == desired_loc_id)
    ).mappings().first()
    if not loc_row:
        # 위치 정보가 없으면 빈 결과 반환
        return RecommendationResponse(total=0, recommendations=[])
    desired_loc_code = loc_row["locationCode"]

    # 1~2. 만료되지 않고(status=2) 활성 공고
    now = datetime.utcnow()
    postings = db.execute(
        select(jobposting_tbl).where(
            and_(
                jobposting_tbl.c.expirationDate > now,
                jobposting_tbl.c.status == 2
            )
        )
    ).mappings().all()

    # 프로필 스킬 셋
    profile_skills = {
        s.strip() for s in raw_skills.split(",") if s.strip()
    }

    results: List[JobRecommendation] = []
    # 최대 가능 점수 (스킬 매칭 최대 + 직무 매칭 1)
    max_raw_score = len(profile_skills) + 1

    for jp in postings:
        # 3~4. 경험·학력 완전 일치
        if jp["experienceLevel"] != experience_level \
                or jp["educationLevel"] != education_level:
            continue

        # 5. 스킬 매칭
        job_keywords = {
            k.strip() for k in (jp["keyword"] or "").split(",") if k.strip()
        }
        skill_matches = profile_skills & job_keywords
        if not skill_matches:
            continue
        skill_score = len(skill_matches)  # 1개당 1점

        # 6. 직무 카테고리 매칭 (jobPostingJobCategory 테이블 조회)
        cat_rows = db.execute(
            select(jobposting_jobcat_tbl.c.jobCategoryId)
            .where(jobposting_jobcat_tbl.c.jobPostingId == jp["id"])
        ).scalars().all()
        if desired_cat_id not in cat_rows:
            continue
        cat_score = 1  # 일치 1점

        # 7. 지역 코드 일치
        if jp["locationCode"] != desired_loc_code:
            continue

        # 8. 연봉 조건
        #     - 요청 연봉 코드가 공고 연봉보다 크면 penalty 1점
        penalty = 1 if desired_salary_code > jp["salaryCode"] else 0

        # raw score 계산
        raw_score = skill_score + cat_score - penalty
        # 9. 100점 만점으로 스케일링
        scaled = (raw_score / max_raw_score) * 100
        final_score = max(0, round(scaled))

        # 10. 회사 정보 조회
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
            company=company_info,
            score=final_score,
            industry=jp["industry"],
            salaryRange=jp["salaryRange"],
            expirationDate=jp["expirationDate"],
        ))

    # 점수 내림차순 정렬
    results.sort(key=lambda x: x.score, reverse=True)

    return RecommendationResponse(
        total=len(results),
        recommendations=results
    )
