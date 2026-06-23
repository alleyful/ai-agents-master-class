import dotenv

dotenv.load_dotenv()

import asyncio

import streamlit as st
from agents import InputGuardrailTripwireTriggered, Runner, SQLiteSession

from models import CustomerContext
from my_agents.triage_agent import triage_agent

st.title("🍝 레스토랑 봇")

customer_ctx = CustomerContext(name="고객님")

# handoff 시 채팅창에 보여줄 한국어 안내 문구
HANDOFF_MESSAGES = {
    "Menu Agent": "🍽️ 메뉴 전문가에게 연결합니다...",
    "Order Agent": "📝 주문 담당에게 연결합니다...",
    "Reservation Agent": "📅 예약 담당에게 연결합니다...",
    "Triage Agent": "🧭 안내 담당으로 돌아갑니다...",
}


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
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


async def run_agent(message):
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

        except InputGuardrailTripwireTriggered:
            st.write("죄송해요, 저는 메뉴·주문·예약만 도와드릴 수 있어요. 🙇")


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
