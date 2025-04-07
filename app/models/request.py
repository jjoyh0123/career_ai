from pydantic import BaseModel

class CoachingRequest(BaseModel):
    contentId: int
    sectionTitle: str
    content: str
