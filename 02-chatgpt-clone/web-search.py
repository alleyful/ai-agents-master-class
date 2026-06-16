import dotenv

dotenv.load_dotenv()

import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool

st.title("🌱 Life Coach")
st.caption("동기부여 · 자기계발 · 습관 형성을 함께 고민하는 AI 코치")

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="Life Coach",
        instructions="""
        너는 따뜻하고 격려를 잘하는 라이프 코치다. 사용자의 목표 달성, 동기부여,
        자기계발, 습관 형성을 돕는다.

        행동 원칙:
        - 동기부여, 자기계발 팁, 습관 형성처럼 "검증된 방법"이 중요한 질문에는
          먼저 Web Search Tool로 최신/신뢰할 만한 정보를 찾아본 뒤 답한다.
        - 사용자를 절대 비난하지 않고 공감과 격려로 시작한다.
        - 추상적인 응원에 그치지 말고, 오늘 바로 실천할 수 있는 구체적이고
          단계적인 행동을 제안한다.
        - 검색으로 찾은 정보는 사용자의 상황에 맞게 풀어서 설명한다.
        - 한국어로, 친근한 코치의 말투로 답한다.

        사용할 수 있는 도구:
            - Web Search Tool: 동기부여 콘텐츠, 자기계발 팁, 습관 형성 기법 등
              최신 정보나 검증된 방법을 찾을 때 사용한다.
        """,
        tools=[
            WebSearchTool(),
        ],
    )
agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "life-coach-history",
        "life-coach-memory.db",
    )
session = st.session_state["session"]


async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"])
        if "type" in message and message["type"] == "web_search_call":
            with st.chat_message("ai"):
                st.write("🔍 웹을 검색했어요...")


def update_status(status_container, event):

    status_messages = {
        "response.web_search_call.completed": ("✅ 웹 검색 완료", "complete"),
        "response.web_search_call.in_progress": (
            "🔍 웹 검색을 시작할게요...",
            "running",
        ),
        "response.web_search_call.searching": (
            "🔍 웹에서 검색 중...",
            "running",
        ),
        "response.completed": (" ", "complete"),
    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)


asyncio.run(paint_history())


async def run_agent(message):
    with st.chat_message("ai"):
        status_container = st.status("⏳", expanded=False)
        text_placeholder = st.empty()
        response = ""

        stream = Runner.run_streamed(
            agent,
            message,
            session=session,
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)


prompt = st.chat_input("고민을 이야기해 보세요")

if prompt:
    with st.chat_message("human"):
        st.write(prompt)
    asyncio.run(run_agent(prompt))


with st.sidebar:
    reset = st.button("Reset")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
