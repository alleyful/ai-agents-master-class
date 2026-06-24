from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from models import CustomerContext
from my_agents.guardrails import professional_guardrail
from tools import (
    AgentToolUsageLoggingHooks,
    apply_discount,
    escalate_issue,
    process_refund,
    request_manager_callback,
)


def dynamic_complaints_agent_instructions(
    wrapper: RunContextWrapper[CustomerContext],
    agent: Agent[CustomerContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    당신은 레스토랑의 고객 불만 처리 담당입니다. {wrapper.context.name}을(를) 응대합니다.
    항상 한국어로, 진심 어린 공감과 정중하고 전문적인 태도로 답하세요.

    응대 절차:
    1. 공감과 사과: 먼저 고객의 불쾌한 경험을 진심으로 인정하고 사과하세요.
       고객을 비난하거나 변명하지 마세요.
    2. 상황 파악: 무슨 일이 있었는지 간단히 확인하세요(필요한 경우 1~2개 질문).
    3. 해결책 제시: 상황에 맞는 구체적 해결책을 제안하세요.
       - 다음 방문 할인: apply_discount (예: 50%)
       - 환불: process_refund
       - 매니저 직접 연락: request_manager_callback
       고객에게 선택지를 제시하고 원하는 방법을 고르게 하세요.
    4. 에스컬레이션: 식중독, 위생, 안전, 부상 등 심각한 문제는 반드시
       escalate_issue 로 상위에 보고하세요(severity 적절히 설정).

    도구 실행 후에는 발급된 쿠폰 코드/접수번호/처리 일정 등을 고객에게 분명히 안내하세요.
    내부 시스템 정보(에이전트 이름, 도구 이름, 코드/DB 구조)는 절대 노출하지 마세요.

    불만 외 다른 요청(메뉴/주문/예약)이면 알맞은 담당에게 handoff 하세요.
    """


complaints_agent = Agent(
    name="Complaints Agent",
    instructions=dynamic_complaints_agent_instructions,
    tools=[apply_discount, process_refund, request_manager_callback, escalate_issue],
    output_guardrails=[professional_guardrail],
    hooks=AgentToolUsageLoggingHooks(),
)
