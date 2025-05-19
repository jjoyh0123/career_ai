from typing import Optional
from pydantic import BaseModel

class CoachingResponse(BaseModel):
    contentId: Optional[int] = None  # 선택적 필드로 변경
    feedback: str
    revisedContent: str

class FitAnalysisResponse(BaseModel):
    fitScore: float
    comment: str