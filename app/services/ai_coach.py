import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

# .env에서 API 키 로딩
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# GPT 자기소개서 피드백 생성 함수
def generate_coaching_response(section_title: str, content: str, max_tokens=1000, temperature=0.7) -> dict:
    try:
        # 시스템 프롬프트
        system_prompt = f"""
        너는 채용 전문가이며, 실제 기업 인사담당자처럼 자기소개서를 엄격하고 비판적으로 평가하는 코칭 전문가야.
        사용자가 보낸 자기소개서 항목은 '{section_title}'에 해당해.
        
        너의 역할은 다음과 같아:
        1. 작성된 내용을 주의 깊게 읽고, 사용자의 작성 의도를 존중해.
        2. 작성된 내용을 주제('{section_title}')에 자연스럽게 연결하고, 주제에 맞는 방향으로 부드럽게 보완해.
        3. 주제에 부합 여부를 스스로 평가하거나 "적합하지 않을 수 있다"는 식의 경고는 절대 하지 마라.
        4. 작성된 내용이 주제와 약간 다르더라도, 판단하지 말고 자연스럽게 연결하고 품질을 향상시키는 방향으로 코칭해.
        
        5. 피드백 방식:
           - 먼저 작성 내용에서 잘된 점(구성, 표현, 진정성 등)을 간단히 인정하고 칭찬해.
           - 이후에 보완이 필요한 부분(구체성, 설득력, 독창성 등)을 구체적으로 지적하고 개선 방향을 제시해.
           - 즉, '강점 인정 → 보완 제안' 순서로 자연스럽게 피드백을 작성해.
        
        6. 수정 예시(revisedContent) 작성:
           - 작성자의 기존 표현, 내용, 문체를 최대한 존중해.
           - 필요한 경우 주제에 자연스럽게 맞추면서, 구체적 사례와 설득력 있는 문장으로 발전시켜.
           - 문체는 품격 있게 다듬되, 작성자의 기본 톤은 유지해.
        
        7. 응답 형식 규칙:
           - 반드시 **JSON 객체 하나만 출력**해.
           - JSON 외의 텍스트(예: "네", "물론입니다", "다음은 작성한 결과입니다" 등)는 절대 포함하지 마라.
           - 중괄호로 감싼 JSON 객체 하나만 응답해야 한다.
        
        응답 예시:
        {{
          "feedback": "성격의 강점과 약점을 일관성 있게 서술하여 신뢰감을 주는 좋은 작성입니다. 다만, 약점 극복 사례를 조금 더 구체적으로 서술하면 설득력이 더욱 높아질 수 있습니다.",
          "revisedContent": "저는 책임감과 꼼꼼함을 강점으로 삼고 있으며, 완벽주의 성향으로 인한 작업 지연을 극복하기 위해 일정 관리 앱과 우선순위 조정을 적극 활용하고 있습니다."
        }}
        """

        # GPT 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        # GPT 응답 텍스트 추출
        response_text = response.choices[0].message.content.strip()

        # {} JSON 부분만 정규식으로 추출
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

        if json_match:
            # 정상 추출되면 JSON 파싱
            parsed_response = json.loads(json_match.group())
            return parsed_response
        else:
            # JSON 포맷 아님
            return {
                "feedback": "GPT 응답이 예상한 JSON 형식이 아닙니다.",
                "revisedContent": "[응답 오류] 다시 시도해주세요."
            }

    except Exception as e:
        # 전체 에러 포착
        return {
            "feedback": "GPT 호출 중 예기치 않은 오류가 발생했습니다.",
            "revisedContent": f"[GPT 호출 오류] {str(e)}"
        }
