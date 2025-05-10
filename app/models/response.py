from pydantic import BaseModel

class CoachingResponse(BaseModel):
    feedback: str
    revisedContent: str

class FitAnalysisResponse(BaseModel):
    fitScore: float
    comment: str