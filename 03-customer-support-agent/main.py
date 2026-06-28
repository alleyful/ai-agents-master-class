import dotenv

dotenv.load_dotenv()

import asyncio
import os
import uuid

import streamlit as st

# 로컬은 .env(dotenv), 배포(Streamlit Cloud)는 st.secrets 에서 키를 읽어 환경변수로 노출한다.
# OpenAI / Agents SDK 는 OPENAI_API_KEY 환경변수를 자동 사용한다.
if not os.getenv("OPENAI_API_KEY"):
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

from agents import OutputGuardrailTripwireTriggered, Runner, SQLiteSession

from models import CustomerContext
from my_agents.guardrails import check_input
from my_agents.triage_agent import triage_agent

st.title("🍝 레스토랑 봇")

customer_ctx = CustomerContext(name="고객님")

# handoff 시 채팅창에 보여줄 한국어 안내 문구
HANDOFF_MESSAGES = {
    "Menu Agent": "🍽️ 메뉴 전문가에게 연결합니다...",
    "Order Agent": "📝 주문 담당에게 연결합니다...",
    "Reservation Agent": "📅 예약 담당에게 연결합니다...",
    "Complaints Agent": "🙏 불만 처리 담당자에게 연결합니다...",
    "Triage Agent": "🧭 안내 담당으로 돌아갑니다...",
}


# 접속자(브라우저 세션)마다 고유 ID를 부여해 대화 메모리가 서로 섞이지 않게 한다.
if "session_id" not in st.session_state:
    st.session_state["session_id"] = uuid.uuid4().hex

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        st.session_state["session_id"],
        "customer-support-memory.db",
    )
session = st.session_state["session"]

if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message.get("type") == "message":
                        st.write(message["content"][0]["text"].replace("$", "\\$"))


asyncio.run(paint_history())


def show_input_block_message(info):
    if getattr(info, "is_inappropriate", False):
        st.warning("정중한 표현으로 다시 말씀해 주시면 기꺼이 도와드리겠습니다. 🙏")
    else:
        st.warning(
            "저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요. "
            "메뉴를 확인하거나, 예약하거나, 음식을 주문할 수 있어요. 🍽️"
        )


async def run_agent(message):
    # 1) input guardrail 사전 검사 — 통과하지 못하면 메인 에이전트를 시작조차 하지 않는다.
    #    덕분에 off-topic/부적절 답변이 화면에 잠깐도 노출되지 않는다.
    verdict = await check_input(message, customer_ctx)
    if verdict.is_off_topic or verdict.is_inappropriate:
        with st.chat_message("ai"):
            show_input_block_message(verdict)
        return

    # 2) 통과한 경우에만 메인 에이전트를 스트리밍 실행한다.
    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""

        try:
            stream = Runner.run_streamed(
                st.session_state["agent"],
                message,
                session=session,
                context=customer_ctx,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":
                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\\$"))

                elif event.type == "agent_updated_stream_event":
                    if st.session_state["agent"].name != event.new_agent.name:
                        notice = HANDOFF_MESSAGES.get(
                            event.new_agent.name,
                            f"🔀 {event.new_agent.name}에게 연결합니다...",
                        )
                        st.info(notice)

                        st.session_state["agent"] = event.new_agent

                        # 새 에이전트의 응답을 위한 새 placeholder
                        text_placeholder = st.empty()
                        response = ""

        except OutputGuardrailTripwireTriggered:
            text_placeholder.empty()
            st.warning(
                "죄송합니다, 답변을 다시 정리하고 있어요. 다시 한 번 말씀해 주시겠어요? 🙇"
            )


message = st.chat_input("무엇을 도와드릴까요? (메뉴 / 주문 / 예약)")

if message:
    with st.chat_message("human"):
        st.write(message)
    asyncio.run(run_agent(message))


with st.sidebar:
    st.header("세션")
    if st.button("대화 초기화"):
        asyncio.run(session.clear_session())
        st.session_state["agent"] = triage_agent
        st.rerun()
