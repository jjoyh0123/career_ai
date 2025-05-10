from fastapi import APIRouter
from app.models.request import CoachingRequest
from app.models.response import CoachingResponse
from app.services.ai_coach import generate_coaching_response
import json

router = APIRouter()

# API 엔드포인트
@router.post("/coaching", response_model=CoachingResponse)
async def get_coaching(request: CoachingRequest):
    result = generate_coaching_response(
        section_title=request.sectionTitle,
        content=request.content
    )

    try:
        return CoachingResponse(
            feedback=result.get("feedback", ""),
            revisedContent=result.get("revisedContent", "")
        )
    except json.JSONDecodeError:
        # 혹시 GPT 응답이 JSON이 아닐 경우 대비
        return CoachingResponse(
            feedback="[GPT 응답 오류] 형식을 인식할 수 없습니다.",
            revisedContent=""
        )
