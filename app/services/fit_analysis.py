import random

async def analyze_fit_score(content: str, job_title: str, job_posting_text: str = None):
    # TODO: 실제 임베딩 + 유사도 계산 로직 대체
    score = round(random.uniform(65, 95), 2)
    comment = f"'{job_title}' 직무와의 적합도가 {score}%로 판단됩니다."

    return score, comment
