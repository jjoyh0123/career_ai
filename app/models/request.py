from typing import Optional
from pydantic import BaseModel

class CoachingRequest(BaseModel):
    sectionTitle: str
    content: str
    contentId: Optional[int] = None  # 필수 아님으로 변경


class FitAnalysisRequest(BaseModel):
    contentId: int
    content: str
    jobTitle: str
    jobPostingText: str | None = None  # Python 3.10 이상

class JobRecommendationRequest(BaseModel):
    profileId: int
