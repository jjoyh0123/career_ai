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
           - 다른 모든 텍스트(예: "다음은 결과입니다", "안녕하세요" 등)는 절대 추가하지 않는다.
        형식은 다음과 같다:
        {{
          "feedback": "작성자의 강점을 인정하고, 개선 방향을 제안하는 구체적인 피드백",
          "revisedContent": "기존 작성 내용을 다듬고 구체적인 사례를 추가하여 자연스럽게 수정한 문장"
        }}
        규칙을 어기면 시스템 오류로 간주된다.
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

        try:
            parsed = json.loads(response_text)
            return parsed
        except json.JSONDecodeError:
            # 바로 실패 처리
            return {
                "feedback": "현재 작성 내용을 기반으로 개선 중입니다. 잠시 후 다시 시도해 주세요.",
                "revisedContent": content
            }
    except Exception as e:
        # 전체 예외 포착
        print(f"[ERROR] GPT 호출 중 예외 발생: {str(e)}")  # 서버 로그용
        return {
            "feedback": "현재 시스템 처리 중 오류가 발생했습니다. 다시 시도해 주세요.",
            "revisedContent": content
        }