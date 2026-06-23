import dotenv
import base64

dotenv.load_dotenv()

import asyncio
import streamlit as st
from openai import OpenAI
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool, ImageGenerationTool

client = OpenAI()

VECTOR_STORE_ID = "vs_6a37e329a8a48191bde605a48b3ec1fc"

st.title("🌱 Life Coach")
st.caption("웹 검색 · 파일 검색 · 이미지 생성으로 목표를 시각화하는 AI 코치")

class CleanSession(SQLiteSession):
    async def get_items(self, limit=None):
        items = await super().get_items(limit)
        for item in items:
            content = item.get("content") if isinstance(item, dict) else None
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        part.pop("annotations", None)
        return items

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="Life Coach",
        model="gpt-4.1",
        instructions="""
        너는 따뜻하고 격려를 잘하는 라이프 코치이자 비주얼 디자이너다.
        사용자의 목표 달성·동기부여·습관 형성을 돕고, 필요할 때 이미지로 동기를 시각화한다.

        사용할 수 있는 도구:
            - File Search Tool: 사용자의 개인 목표와 일기가 담긴 문서를 검색한다.
              운동, 공부, 습관, 목표 진행 상황과 관련된 질문에는 반드시 먼저 이
              도구로 사용자의 목표 수치와 과거 기록을 확인한다.
            - Web Search Tool: 동기부여 콘텐츠, 자기계발 팁, 습관 형성 기법 등
              최신 정보나 검증된 방법을 찾을 때 사용한다.
            - Image Generation Tool: 비전 보드, 축하·동기부여 포스터, 진행 상황
              시각화 이미지를 생성한다.

        행동 원칙:
            - 운동/공부/습관/목표 이야기에는 답하기 전에 먼저 File Search로 네 기록을 확인한다.
            - Web Search는 매번 쓰지 말고, 최신 정보·검증된 기법·외부 근거가 실제로 도움이 될 때만 사용한다. 이미 기록과 일반적인 코칭 지식으로 충분히 답할 수 있으면 웹 검색은 생략한다.
            - "네 기록(파일)"을 중심으로, 필요할 때 더한 "검증된 방법(웹)"을 자연스럽게 엮어 개인화된 조언으로 이어준다.
            [이미지 생성 규칙 — 매우 중요. 순서를 반드시 지킨다]
            이미지(비전 보드·축하 포스터·진행 시각화)가 필요한 요청이면 아래 1→2→3 순서를 그대로 따른다.
            1) 먼저 File Search로 사용자의 실제 목표·기록을 확인한다. (절대 생략하지 않는다)
            2) 확인한 내용을 바탕으로 짧게 공감·피드백을 전한다. 어떤 목표를 어디까지 달성했는지, 어떤 테마(운동/언어/여행/독서 등)를 이미지에 담을지 사용자의 실제 기록을 언급한다.
            3) 그 피드백 "직후 같은 턴 안에서" Image Generation Tool을 반드시 호출해 실제 이미지를 만든다.
            - 문서 확인과 피드백 없이 곧바로 이미지부터 그리지 않는다. 문서에서 확인한 사용자의 실제 목표가 이미지에 반영되어야 한다.
            - "만들어 드릴게요", "이미지를 생성할게요" 같은 말만 하고 도구 호출 없이 턴을 끝내는 것은 절대 금지다. 말했으면 그 턴에서 무조건 이미지를 생성해 보여준다.
            - 이미지 안에 넣는 글자는 짧은 영어 단어 위주로 한다(한국어 텍스트는 깨질 수 있음).
            - 비난하지 않고 공감과 격려로 시작하며, 추상적인 응원보다 오늘 바로 실천할 수 있는 구체적인 행동을 제안한다.
            - 한국어로, 친근한 코치의 말투로 답한다.
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
            ImageGenerationTool(
                 tool_config={
                     "type": "image_generation",
                     "quality": "medium",
                     "size": "1024x1024",
                     "output_format": "jpeg",
                     "partial_images": 1,
                 },
             ),
        ],
    )
agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = CleanSession(
        "life-coach-vision",
        "life-coach-vision.db",
    )
session = st.session_state["session"]

def show_image(b64, caption=None):
    st.image(base64.b64decode(b64), caption=caption, use_container_width=True)


def upload_file(file):
    uploaded_file = client.files.create(
        file=(file.name, file.getvalue()),
        purpose="user_data",
    )
    client.vector_stores.files.create(
        vector_store_id=VECTOR_STORE_ID,
        file_id=uploaded_file.id,
    )
    return uploaded_file


def load_existing_files():
    """벡터 스토어에 이미 올라가 있는 파일 목록을 불러온다 (토큰 비용 없는 관리 API)."""
    items = []
    try:
        for vsf in client.vector_stores.files.list(vector_store_id=VECTOR_STORE_ID).data:
            info = client.files.retrieve(vsf.id)
            items.append({"key": vsf.id, "name": info.filename, "size": info.bytes})
    except Exception as e:
        st.warning(f"기존 파일 목록을 불러오지 못했어요: {e}")
    return items


def delete_file(file_id):
    """벡터 스토어에서 연결을 끊고 파일 저장소에서도 삭제한다."""
    try:
        client.vector_stores.files.delete(
            vector_store_id=VECTOR_STORE_ID,
            file_id=file_id,
        )
    except Exception as e:
        st.warning(f"벡터 스토어에서 제거 실패: {e}")
    try:
        client.files.delete(file_id)
    except Exception as e:
        st.warning(f"파일 삭제 실패: {e}")


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
        mtype = message.get("type")
        if mtype == "file_search_call":
            with st.chat_message("ai"):
                st.write("📄 목표 문서를 찾아봤어요...")
        elif mtype == "web_search_call":
            with st.chat_message("ai"):
                 st.write("🔍 웹을 검색했어요...")
        elif mtype == "image_generation_call":
            result = message.get("result")
            if result:
                with st.chat_message("ai"):
                    show_image(result, "🎨 생성한 이미지")

def update_status(status_container, event):
    status_messages = {
         "response.file_search_call.in_progress": ("📄 목표 문서를 찾는 중...", "running"),
         "response.file_search_call.searching": ("📄 목표 문서 검색 중...", "running"),
         "response.file_search_call.completed": ("✅ 목표 문서 확인 완료", "complete"),
         "response.web_search_call.in_progress": ("🔍 웹 검색을 시작할게요...", "running"),
         "response.web_search_call.searching": ("🔍 웹에서 검색 중...", "running"),
         "response.web_search_call.completed": ("✅ 웹 검색 완료", "complete"),
         "response.image_generation_call.in_progress": ("🎨 이미지를 준비하는 중...", "running"),
         "response.image_generation_call.generating": ("🎨 이미지를 그리는 중...", "running"),
         "response.image_generation_call.completed": ("✅ 이미지 생성 완료", "complete"),
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
        image_placeholder = st.empty()
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

                elif event.data.type == "response.image_generation_call.partial_image":
                     image_placeholder.image(base64.b64decode(event.data.partial_image_b64))

        # 스트림이 끝났는데 완료 이벤트를 놓쳤더라도 상태가 'running'으로 남지 않게 고정한다.
        status_container.update(label="✅ 완료", state="complete")


prompt = st.chat_input("목표를 이야기하거나 비전 보드를 요청해 보세요")

if prompt:
    with st.chat_message("human"):
        st.write(prompt)
    asyncio.run(run_agent(prompt))
    # 스트리밍이 끝나면 전체를 다시 그려 최종 상태로 고정한다.
    # → 임시 placeholder(st.empty)가 사라지고 최종 이미지/텍스트는 paint_history가
    #   세션에서 안정 요소로 렌더 → 다음 생성 때 이전 이미지 잔상이 남지 않는다.
    st.rerun()


with st.sidebar:
    st.header("📁 목표·일기 파일")
    st.caption("txt 파일을 올리면 코치가 참고해서 답해요")

    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = load_existing_files()
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0

    files = st.file_uploader(
        "파일 업로드",
        type=["txt"],
        accept_multiple_files=True,
        key=f"uploader-{st.session_state['uploader_key']}",
    )

    if files:
        for file in files:
            # 같은 파일(이름+크기)이 이미 목록에 있으면 재업로드하지 않는다.
            if any(f["name"] == file.name and f["size"] == file.size
                   for f in st.session_state["uploaded_files"]):
                continue
            with st.status(f"⏳ {file.name} 업로드 중...") as status:
                uploaded = upload_file(file)
                status.update(label=f"✅ {file.name} 업로드 완료", state="complete")
            st.session_state["uploaded_files"].append(
                {"key": uploaded.id, "name": file.name, "size": file.size}
            )

    st.subheader("업로드된 파일")
    if st.session_state["uploaded_files"]:
        for f in st.session_state["uploaded_files"]:
            col1, col2 = st.columns([4, 1])
            col1.write(f"📄 {f['name']} · {f['size'] / 1024:.1f} KB")
            if col2.button("🗑️", key=f"del-{f['key']}"):
                delete_file(f["key"])
                st.session_state["uploaded_files"] = [
                    x for x in st.session_state["uploaded_files"] if x["key"] != f["key"]
                ]
                # 업로더를 리셋해 방금 지운 파일이 자동으로 다시 올라가지 않게 한다.
                st.session_state["uploader_key"] += 1
                st.rerun()
    else:
        st.caption("아직 업로드된 파일이 없어요")

    st.divider()
    if st.button("Reset"):
        asyncio.run(session.clear_session())
        st.rerun()  # 비운 직후 화면을 다시 그려 옛 기록이 남지 않게 한다

    st.write(asyncio.run(session.get_items()))
