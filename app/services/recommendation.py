import re
from datetime import datetime
from typing import List

from fastapi import HTTPException
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

        # 7. 지역 스코어링: exact id match → 1.0, same province → 0.5, else → 0.0
        job_loc = db.execute(
            select(location_tbl)
            .where(location_tbl.c.locationCode == jp["locationCode"])
        ).mappings().first()

        if job_loc:
            # (1) 프로필이 원하는 location.id와 정확히 일치
            if job_loc["id"] == desired_loc_id:
                local_score = 1.0
            # (2) id는 다르지만 province(도/광역시)만 일치
            elif job_loc["province"] == desired_province:
                local_score = 0.5
            else:
                local_score = 0.0
        else:
            # location 테이블에 없는 코드면 0점
            local_score = 0.0

        # 8. 연봉 스코어링: 희망 연봉 대비 공고 연봉 비교
        salary_code = jp["salaryCode"]
        desired_code = desired_salary_code

        # 1) 연단위 연봉코드를 만원 단위 숫자로 매핑
        annual_map = {
            9: 2600,  10: 2800, 11: 3000, 12: 3200,
            13: 3400, 14: 3600, 15: 3800, 16: 4000,
            17: 5000, 18: 6000, 19: 7000, 20: 8000,
            21: 9000, 22:10000
        }

        salary_score = 0

        # 연단위(9~22)끼리 비교
        if salary_code in annual_map and desired_code in annual_map:
            if annual_map[salary_code] >= annual_map[desired_code]:
                salary_score = 1

        # 월급(101), 주급(102), 일급(103), 시급(104)
        elif salary_code in (101, 102, 103, 104) and desired_code in annual_map:
            # salaryRange 예: '월급 230만원'
            m = re.search(r'(\d+(?:\.\d+)?)', jp["salaryRange"] or "")
            if m:
                actual = float(m.group(1))  # 공고에서 제시한 단위당 금액 (만원)
                # 희망 연봉 → 해당 단위로 환산
                desired_annual = annual_map[desired_code]
                converted = {
                    101: desired_annual / 12,        # 월
                    102: desired_annual / 52,        # 주
                    103: desired_annual / 365,       # 일
                    104: (desired_annual * 10000) / (365 * 24) / 10000  # 시급 (만원 단위 유지)
                }[salary_code]
                if actual >= converted:
                    salary_score = 1

        # 면접후결정(99) / 회사내규(0)는 낮은 점수(0) 유지

        # 건당(105)
        elif salary_code == 105:
            # 희망 연봉 코드도 105여야 최고 점수
            if desired_code == 105:
                salary_score = 1

        # 9. raw score 계산 (최대: cos_sim + 1 + 1 + 1)
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
