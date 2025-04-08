from fastapi import APIRouter
from app.models.request import FitAnalysisRequest
from app.models.response import FitAnalysisResponse
from app.services.fit_analysis import analyze_fit_score


router = APIRouter()

@router.post("/fit-analysis", response_model=FitAnalysisResponse)
async def fit_analysis(request: FitAnalysisRequest):
    score, comment = await analyze_fit_score(
        content=request.content,
        job_title=request.jobTitle,
        job_posting_text=request.jobPostingText
    )

    return FitAnalysisResponse(
        fitScore=score,
        comment=comment
    )
