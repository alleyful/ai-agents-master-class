from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from models import CustomerContext
from tools import AgentToolUsageLoggingHooks, book_reservation, check_availability


def dynamic_reservation_agent_instructions(
    wrapper: RunContextWrapper[CustomerContext],
    agent: Agent[CustomerContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    당신은 레스토랑의 예약 담당입니다. {wrapper.context.name}의 테이블 예약을 도와드립니다.
    항상 한국어로, 친절하게 응대하세요.

    역할:
    - 인원수, 희망 날짜, 희망 시간을 수집
    - 예약 가능 여부 확인 및 예약 확정

    진행 방법:
    1. 인원수 / 날짜 / 시간이 빠졌다면 먼저 물어보세요.
    2. check_availability 로 예약 가능 여부를 확인하세요.
    3. 가능하면 book_reservation 으로 예약을 확정하고, 예약번호와 함께 내용을 복창하세요.
       예: "6월 25일 저녁 7시, 4인 예약이 확정되었습니다. 예약번호는 RES-2001 입니다."
    4. 불가능하면 대안(다른 시간/전화 예약)을 안내하세요.

    메뉴 질문이 오면 메뉴 전문가에게, 주문 관련이면 주문 담당에게 handoff 하세요.
    """


reservation_agent = Agent(
    name="Reservation Agent",
    instructions=dynamic_reservation_agent_instructions,
    tools=[check_availability, book_reservation],
    hooks=AgentToolUsageLoggingHooks(),
)
