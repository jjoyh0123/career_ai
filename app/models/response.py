from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from typing import List

class CoachingResponse(BaseModel):
    contentId: Optional[int] = None  # 선택적 필드로 변경
    feedback: str
    revisedContent: str

class FitAnalysisResponse(BaseModel):
    fitScore: float
    comment: str

class CompanyInfo(BaseModel):
    id: int
    name: str
    address: str

class JobRecommendation(BaseModel):
    jobPostingId: int
    title: str
    score: int
    industry: str
    salaryRange: str
    expirationDate: datetime
    company: CompanyInfo

class RecommendationResponse(BaseModel):
    total: int
    recommendations: List[JobRecommendation]
