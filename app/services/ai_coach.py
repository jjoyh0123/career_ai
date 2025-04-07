import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# .env에서 API 키 로딩
load_dotenv()

# OpenAI 클라이언트 초기화 (신버전 방식)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# GPT 자기소개서 피드백 생성 함수
def generate_coaching_response(section_title: str, content: str) -> dict:
    try:
        system_prompt = f"""
        너는 채용 전문가이며, 자기소개서 코칭 전문가야.
        사용자가 보낸 자기소개서 항목은 '{section_title}'에 해당해.

        너의 역할은 다음과 같아:
        1. 작성한 내용을 꼼꼼히 읽고, 주제에 적합한지 분석해.
        2. 어휘, 표현, 문장 흐름, 논리, 구조, 구체성, 설득력을 평가해.
        3. 수정이 필요한 부분은 어떤 점이 부족하고 어떻게 보완하면 좋을지 간단히 설명해줘. (피드백)
        4. 피드백을 바탕으로 훨씬 더 완성도 높고, 자연스럽고, 구체적인 자기소개서 문장으로 다시 작성해줘. (수정 버전)
        5. 단순히 맞춤법이나 문법만 고치는 것이 아니라, 내용을 보완하거나 강조해야 할 부분을 능동적으로 찾아서 보완해줘.
        6. 작성자의 톤이나 개성을 최대한 유지해줘. 단, 품격 있는 표현으로 다듬어줘.

        피드백은 간단명료하게 1~2문장으로 먼저 주고, 이어서 수정한 자기소개서 문장을 함께 줘.
        JSON 형식으로 응답해줘.

        형식 예시:
        {{
          "feedback": "‘협업 경험’이 모호하게 표현되어 구체적인 사례와 성과를 추가하면 더 설득력 있습니다.",
          "revisedContent": "저는 프로젝트에서 팀원들과 역할을 나누고 협업하며, 마감 기한 내에 문제를 해결해낸 경험이 있습니다..."
        }}
        """

        # GPT 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        # 응답 content는 string이므로 JSON 파싱
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {
            "feedback": "GPT 호출 중 오류가 발생했습니다.",
            "revisedContent": f"[GPT 호출 오류] {str(e)}"
        }
