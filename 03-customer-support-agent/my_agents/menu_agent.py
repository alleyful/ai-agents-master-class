from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from models import CustomerContext
from tools import (
    AgentToolUsageLoggingHooks,
    get_dish_details,
    get_menu,
    list_dietary_options,
)


def dynamic_menu_agent_instructions(
    wrapper: RunContextWrapper[CustomerContext],
    agent: Agent[CustomerContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    당신은 레스토랑의 메뉴 전문가입니다. {wrapper.context.name}을(를) 도와드립니다.
    항상 한국어로, 친절하고 간결하게 답변하세요.

    역할:
    - 메뉴 구성과 가격 안내
    - 특정 요리의 재료 설명
    - 알레르기 유발 성분(글루텐, 우유, 계란 등) 안내
    - 채식/비건/글루텐프리 등 식이 옵션 추천

    진행 방법:
    1. 전체 메뉴 질문에는 get_menu 를 사용하세요.
    2. 특정 요리의 재료/알레르겐 질문에는 get_dish_details 를 사용하세요.
    3. "채식 메뉴 있어?" 같은 식이 질문에는 list_dietary_options 를 사용하세요.
    4. 알레르기 정보는 추측하지 말고 반드시 도구 결과에 근거해 안내하세요.

    고객이 주문을 원하면 주문 담당에게, 예약을 원하면 예약 담당에게 handoff 하세요.
    """


menu_agent = Agent(
    name="Menu Agent",
    instructions=dynamic_menu_agent_instructions,
    tools=[get_menu, get_dish_details, list_dietary_options],
    hooks=AgentToolUsageLoggingHooks(),
)
