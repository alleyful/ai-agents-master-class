from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from models import CustomerContext
from my_agents.guardrails import professional_guardrail
from tools import AgentToolUsageLoggingHooks, get_order_status, place_order


def dynamic_order_agent_instructions(
    wrapper: RunContextWrapper[CustomerContext],
    agent: Agent[CustomerContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    당신은 레스토랑의 주문 담당입니다. {wrapper.context.name}의 주문을 받습니다.
    항상 한국어로, 친절하게 응대하세요.

    역할:
    - 고객이 주문하려는 메뉴를 정확히 파악
    - 주문 접수 및 합계 안내
    - 주문 상태 조회

    진행 방법:
    1. 주문할 메뉴와 수량을 확인하세요. 모호하면 다시 물어보세요.
    2. place_order 로 주문을 접수하세요.
    3. 접수 후 반드시 주문 항목과 합계 금액을 복창하여 확인받으세요.
       예: "마르게리타 피자 1개, 합계 17,000원으로 주문 접수되었습니다. 주문번호는 ORD-1001 입니다."
    4. 주문 상태 문의에는 get_order_status 를 사용하세요.

    메뉴 재료/알레르기 질문이 오면 메뉴 전문가에게, 예약 관련이면 예약 담당에게 handoff 하세요.
    """


order_agent = Agent(
    name="Order Agent",
    instructions=dynamic_order_agent_instructions,
    tools=[place_order, get_order_status],
    output_guardrails=[professional_guardrail],
    hooks=AgentToolUsageLoggingHooks(),
)
