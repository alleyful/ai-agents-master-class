import streamlit as st
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    handoff,
    input_guardrail,
)
from agents.extensions import handoff_filters
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from models import CustomerContext, HandoffData, OffTopicGuardrailOutput
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent


# ---------------------------------------------------------------------------
# 입력 가드레일: 레스토랑과 무관한 요청 차단
# ---------------------------------------------------------------------------

input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
    사용자의 요청이 레스토랑(메뉴/재료/알레르기, 주문, 테이블 예약)과 관련 있는지 판단하세요.
    가벼운 인사나 대화 시작은 허용합니다. 그러나 날씨, 코딩, 일반 상식 등 레스토랑과
    전혀 무관한 요청이면 off-topic 으로 표시하고 이유를 적으세요.
    """,
    output_type=OffTopicGuardrailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[CustomerContext],
    agent: Agent[CustomerContext],
    input: str,
):
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


# ---------------------------------------------------------------------------
# Triage 에이전트
# ---------------------------------------------------------------------------

def dynamic_triage_instructions(
    wrapper: RunContextWrapper[CustomerContext],
    agent: Agent[CustomerContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    당신은 레스토랑의 안내 담당(Triage)입니다. 고객을 이름으로 부르며 한국어로 응대하세요.
    고객의 이름은 {wrapper.context.name} 입니다.

    당신의 핵심 역할: 고객이 무엇을 원하는지 파악하고 알맞은 전문가에게 연결합니다.

    분류 가이드:
    🍽️ 메뉴 전문가(Menu Agent) — 메뉴 구성, 가격, 재료, 알레르기, 채식/비건 등
       예: "메뉴 뭐 있어?", "이 요리에 견과류 들어가?", "채식 메뉴 있어?"
    📝 주문 담당(Order Agent) — 음식 주문 접수, 주문 상태 확인
       예: "피자 2판 주문할게", "내 주문 어떻게 됐어?"
    📅 예약 담당(Reservation Agent) — 테이블 예약, 예약 확인
       예: "예약하고 싶어", "주말 저녁 4명 자리 있어?"

    진행 방법:
    1. 고객의 요청을 듣고 위 세 가지 중 하나로 분류하세요.
    2. 모호하면 1개의 짧은 질문으로 확인하세요.
    3. 연결 전에 한 문장으로 안내하세요. 예: "예약 담당에게 연결해 드릴게요..."
    4. 알맞은 전문 에이전트로 handoff 하세요.
    """


def handle_handoff(
    wrapper: RunContextWrapper[CustomerContext],
    input_data: HandoffData,
):
    with st.sidebar:
        st.write(
            f"""
            🔀 **{input_data.to_agent_name}** (으)로 연결
            - 요청: {input_data.intent}
            - 설명: {input_data.description}
            - 사유: {input_data.reason}
            """
        )


def make_handoff(agent):
    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_instructions,
    input_guardrails=[off_topic_guardrail],
    handoffs=[
        make_handoff(menu_agent),
        make_handoff(order_agent),
        make_handoff(reservation_agent),
    ],
)


# ---------------------------------------------------------------------------
# 전문 에이전트 간 재라우팅 배선 (순환 import 방지를 위해 여기서 일괄 설정)
# 예: 예약 진행 중 메뉴 질문이 오면 Reservation → Menu 로 직접 handoff
# ---------------------------------------------------------------------------

menu_agent.handoffs = [
    make_handoff(order_agent),
    make_handoff(reservation_agent),
    make_handoff(triage_agent),
]
order_agent.handoffs = [
    make_handoff(menu_agent),
    make_handoff(reservation_agent),
    make_handoff(triage_agent),
]
reservation_agent.handoffs = [
    make_handoff(menu_agent),
    make_handoff(order_agent),
    make_handoff(triage_agent),
]
