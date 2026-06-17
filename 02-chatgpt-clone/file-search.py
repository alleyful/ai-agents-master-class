import dotenv

dotenv.load_dotenv()
import asyncio
import streamlit as st
from openai import OpenAI
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool

client = OpenAI()

VECTOR_STORE_ID = "vs_6a3263a08b3c8191b166c1387acce487"

st.title("🌱 Life Coach")
st.caption("개인 목표·일기 문서와 웹 검색을 함께 활용해 함께 고민하는 AI 코치")

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="Life Coach",
        model="gpt-4o-mini",
        instructions="""
        너는 따뜻하고 격려를 잘하는 라이프 코치다. 사용자의 목표 달성, 동기부여,
        자기계발, 습관 형성을 돕는다.

        사용할 수 있는 도구:
            - File Search Tool: 사용자의 개인 목표와 일기가 담긴 문서를 검색한다.
              운동, 공부, 습관, 목표 진행 상황과 관련된 질문에는 반드시 먼저 이
              도구로 사용자의 목표 수치와 과거 기록을 확인한다.
            - Web Search Tool: 동기부여 콘텐츠, 자기계발 팁, 습관 형성 기법 등
              최신 정보나 검증된 방법을 찾을 때 사용한다.

        행동 원칙:
            - 운동/공부/습관/목표 이야기에는 답하기 전에 먼저 File Search로 네 기록을 확인하고, Web Search로 검증된 최신 방법을 한 번 찾아본다. 이미 답을 알 것 같아도, 최신 근거를 더하기 위해 Web Search는 매번 한 번은 거친다.
            - 그렇게 찾은 "네 기록(파일) + 검증된 방법(웹)"을 자연스럽게 엮어 개인화된 조언으로 이어준다.
            - 비난하지 않고 공감과 격려로 시작하며, 추상적인 응원보다 오늘 바로 실천할 수 있는 구체적인 행동을 제안한다.
            - 한국어로, 친근한 코치의 말투로 답한다.
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),

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
        if "type" in message and message["type"] == "file_search_call":
            with st.chat_message("ai"):
                st.write("📄 목표 문서를 찾아봤어요...")
        if "type" in message and message["type"] == "web_search_call":
            with st.chat_message("ai"):
                st.write("🔍 웹을 검색했어요...")

asyncio.run(paint_history())

def update_status(status_container, event):

    status_messages = {
        "response.file_search_call.in_progress": (
            "📄 목표 문서를 찾는 중...",
            "running",
        ),
        "response.file_search_call.searching": (
            "📄 목표 문서 검색 중...",
            "running",
        ),
        "response.file_search_call.completed": (
            "✅ 목표 문서 확인 완료",
            "complete",
        ),
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


prompt = st.chat_input(
    "고민이나 목표 진행 상황을 물어보세요",
    accept_file=True,
    file_type=["txt"],
)

if prompt:

    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message("ai"):
                with st.status("⏳ 파일 업로드 중...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data",
                    )
                    status.update(label="⏳ 파일 연결 중...")
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id,
                    )
                    status.update(label="✅ 파일 업로드 완료", state="complete")

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))


with st.sidebar:
    if st.button("Reset"):
        asyncio.run(session.clear_session())

    st.write(asyncio.run(session.get_items()))
