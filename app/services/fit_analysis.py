from app.services.embedding_service import get_embedding, cosine_similarity

async def analyze_fit_score(content: str, job_title: str, job_posting_text: str = None):
    try:
        content_embedding = await get_embedding(content)
        job_text = job_posting_text if job_posting_text else f"{job_title} 직무를 수행하는 데 필요한 역량 및 주요 업무"
        job_embedding = await get_embedding(job_text)

        similarity = cosine_similarity(content_embedding, job_embedding)
        fit_score = round(similarity * 100, 2)

        # 점수대별 comment 생성
        if fit_score >= 85:
            comment_detail = "매우 높은 적합도를 보입니다. 지원 시 강점이 될 수 있습니다."
        elif fit_score >= 70:
            comment_detail = "적합도가 양호합니다. 추가적인 역량 강조가 도움이 될 수 있습니다."
        elif fit_score >= 50:
            comment_detail = "보통 수준의 적합도입니다. 더 구체적인 경험과 성과를 강조해 보세요."
        else:
            comment_detail = "적합도가 낮습니다. 직무 관련 경험을 보강하거나 방향 재설정이 필요할 수 있습니다."

        comment = f"'{job_title}' 직무와의 적합도가 {fit_score}%로 판단됩니다. {comment_detail}"

        return fit_score, comment
    except Exception as e:
        return 0.0, f"[적합도 분석 오류] {str(e)}"


