from pydantic import BaseModel


class CustomerContext(BaseModel):
    """대화 전반에서 공유되는 고객 정보 (인사 개인화 등에 사용)."""

    name: str = "고객님"


class HandoffData(BaseModel):
    """전문 에이전트로 handoff 할 때 LLM 이 채워주는 정보."""

    to_agent_name: str
    intent: str
    description: str
    reason: str


class OffTopicGuardrailOutput(BaseModel):
    """입력 가드레일이 레스토랑과 무관한 요청인지 판정한 결과."""

    is_off_topic: bool
    reason: str
