from pydantic import BaseModel

class CoachingRequest(BaseModel):
    sectionTitle: str
    content: str

class FitAnalysisRequest(BaseModel):
    contentId: int
    content: str
    jobTitle: str
    jobPostingText: str | None = None  # Python 3.10 이상