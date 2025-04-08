from pydantic import BaseModel

class CoachingResponse(BaseModel):
    contentId: int
    feedback: str
    revisedContent: str

class FitAnalysisResponse(BaseModel):
    fitScore: float
    comment: str