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


class InputGuardrailOutput(BaseModel):
    """입력 가드레일 판정 결과: 주제 이탈 또는 부적절한 언어 여부."""

    is_off_topic: bool
    is_inappropriate: bool
    reason: str


class OutputGuardrailOutput(BaseModel):
    """출력 가드레일 판정 결과: 비전문적/무례 또는 내부 정보 노출 여부."""

    is_unprofessional: bool
    reveals_internal_info: bool
    reason: str
