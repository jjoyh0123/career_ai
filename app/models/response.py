from pydantic import BaseModel

class CoachingResponse(BaseModel):
    contentId: int
    feedback: str
    revisedContent: str
