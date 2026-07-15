"""Tutor chat page: ask about a stuck spot with an optional photo."""

import uuid
from pathlib import Path

import streamlit as st

from common import get_agent, initialize_session, temporary_image, debug_metadata
from knitcoach import DEBUG_MODE, invoke_turn


def reset_chat() -> None:
    st.session_state.thread_id = uuid.uuid4().hex
    st.session_state.chat_history = []


def render() -> None:
    initialize_session()
    header, action = st.columns([4, 1])
    with header:
        st.markdown("## 튜터 상담")
        st.caption("질문 입력창의 첨부 버튼으로 작품 사진을 함께 보내세요.")
    with action:
        st.button("새 대화", on_click=reset_chat, use_container_width=True)

    if not st.session_state.chat_history:
        st.markdown(
            '<div class="empty-hint">막힌 부분을 입력하고, 필요하면 사진을 첨부해 보세요.<br>'
            "예: “원형뜨기 늘림 위치가 헷갈려요” + 작품 사진</div>",
            unsafe_allow_html=True,
        )

    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            if item.get("image"):
                st.image(item["image"], caption=item.get("image_name"), width=320)
            st.markdown(item["content"])
            if DEBUG_MODE and item.get("debug"):
                with st.expander("개발자 정보"):
                    st.json(item["debug"])

    submission = st.chat_input(
        "막힌 부분을 적고 필요하면 사진을 첨부하세요",
        accept_file=True,
        file_type=["png", "jpg", "jpeg", "webp"],
        max_upload_size=10,
    )
    if not submission:
        return
    prompt = submission if isinstance(submission, str) else submission.text
    files = [] if isinstance(submission, str) else list(submission.files)
    if not prompt.strip():
        st.warning("사진과 함께 궁금한 점도 적어 주세요.")
        return
    image = files[0] if files else None
    image_bytes = image.getvalue() if image else None
    st.session_state.chat_history.append({"role": "user", "content": prompt, "image": image_bytes, "image_name": image.name if image else None})
    temp_path = temporary_image(image_bytes, Path(image.name).suffix.lower()) if image else None
    try:
        with st.spinner("작품을 살펴보는 중이에요..."):
            result = invoke_turn(
                get_agent(), prompt, st.session_state.thread_id,
                str(temp_path) if temp_path else None,
                original_image_name=image.name if image else "",
            )
        response = result.get("user_response") or str(result["messages"][-1].content)
        st.session_state.chat_history.append({"role": "assistant", "content": response, "debug": debug_metadata(result)})
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
    st.rerun()
