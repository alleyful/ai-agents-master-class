"""Chat-first KnitCoach workspace with a work LNB and inspectable result cards."""

from pathlib import Path

import streamlit as st

import ui
from nav import WORKSHOP_TOOLS
from common import (
    activate_thread,
    active_thread,
    append_message,
    attach_work_cards,
    create_thread,
    debug_metadata,
    find_work_card,
    get_agent,
    initialize_session,
    recent_threads,
    temporary_image,
)
from content.presets import DEFAULT_PRESET, PRESET_NAMES, PROJECT_PRESETS
from knitcoach import DEBUG_MODE, ENABLE_VISION, HAS_OPENAI_KEY, invoke_turn

_SAMPLE_IMAGE = Path(__file__).resolve().parent.parent / "samples" / "crochet-mesh-shoulder-bag.png"
_CARD_LABELS = {"pattern": "도안", "diagnosis": "문제 진단", "technique": "기법", "practice": "연습"}
_COMMANDS = {
    "pattern": ("도안 만들기", "작품 사진과 내 조건으로 도안 초안을 만들어요."),
    "diagnose": ("사진으로 문제 찾기", "막힌 부분의 사진을 올리고 원인을 같이 살펴봐요."),
    "technique": ("기법 배우기", "배우고 싶은 기법을 내 수준에 맞게 익혀요."),
    "tools": ("실·바늘 고르기", "실 굵기와 작품에 맞는 도구를 골라요."),
}


def _set_mode(mode: str) -> None:
    st.session_state.workspace_view = "chat"
    st.session_state.composer_mode = mode
    st.session_state.composer_context = ""


def _open_technique_library() -> None:
    st.session_state.workspace_view = "techniques"
    st.session_state.composer_mode = "chat"


def _ask_about_technique(name: str) -> None:
    st.session_state.workspace_view = "chat"
    st.session_state.composer_mode = "technique"
    st.session_state.composer_context = f"{name.split('(')[0]}에 대해 질문할게요. "


def _open_card(thread_id: str, card_id: str) -> None:
    activate_thread(thread_id)
    st.session_state.selected_work_card_id = card_id


def _close_panel() -> None:
    st.session_state.selected_work_card_id = None


def _use_card_context(text: str) -> None:
    st.session_state.composer_mode = "chat"
    st.session_state.composer_context = text


def _dismiss_pattern_dialog() -> None:
    st.session_state.composer_mode = "chat"


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="brand-mark"><span class="stitch-mark">KN</span>'
            '<div><strong>KnitCoach</strong><small>KNITTING WORKBENCH</small></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="stitched-rule"></div>', unsafe_allow_html=True)
        with st.container(key="lnb_new"):
            st.button("＋  새 뜨개 대화", on_click=create_thread, use_container_width=True, type="primary")

        with st.container(key="lnb_recent"):
            st.markdown('<p class="lnb-label">RECENT WORK</p>', unsafe_allow_html=True)
            threads = recent_threads()
            if threads:
                for thread in threads[:8]:
                    active = thread["id"] == st.session_state.active_thread_id
                    st.button(
                        thread["title"],
                        key=f"thread_{thread['id']}",
                        on_click=activate_thread,
                        args=(thread["id"],),
                        use_container_width=True,
                        type="primary" if active else "secondary",
                    )
            else:
                st.caption("첫 대화를 시작하면 작업이 쌓여요.")

        with st.container(key="lnb_tools"):
            st.markdown('<p class="lnb-label">WORKBENCH TOOLS</p>', unsafe_allow_html=True)
            for mode, icon, label in WORKSHOP_TOOLS:
                callback = _open_technique_library if mode == "technique_library" else _set_mode
                args = () if mode == "technique_library" else (mode,)
                st.button(
                    f"{icon}  {label}",
                    key=f"lnb_{mode}",
                    on_click=callback,
                    args=args,
                    use_container_width=True,
                    type="primary" if st.session_state.workspace_view == "techniques" and mode == "technique_library" else "secondary",
                )

        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
        if ENABLE_VISION and HAS_OPENAI_KEY:
            st.markdown('<div class="system-status"><i></i> 사진 분석 사용 가능</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="system-status demo"><i></i> 샘플 데모 모드</div>', unsafe_allow_html=True)
            st.caption("이 접속의 대화만 임시로 기억해요.")


def _latest_cards() -> list[tuple[str, dict]]:
    cards: list[tuple[str, dict, float]] = []
    for thread in recent_threads():
        for card in reversed(thread["work_cards"]):
            cards.append((thread["id"], card, thread["updated_at"]))
    cards.sort(key=lambda item: item[2], reverse=True)
    return [(thread_id, card) for thread_id, card, _ in cards[:3]]


def _render_welcome_header() -> None:
    st.markdown(
        f"""
        <section class="workbench-welcome">
          {ui.eyebrow("READY AT THE WORKBENCH")}
          <h1>오늘은 어떤 뜨개를 같이 볼까요?</h1>
          <p>사진, 도안, 막힌 한 코—편한 방식으로 올려주세요.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_action_shelf() -> None:
    latest = _latest_cards()
    with st.container(key="action_shelf"):
        if latest:
            st.markdown('<span class="shelf-label">CONTINUE</span>', unsafe_allow_html=True)
            with st.container(key="resume_actions", horizontal=True, gap="small"):
                for thread_id, card in latest[:2]:
                    label = card["title"]
                    if len(label) > 18:
                        label = f"{label[:18]}…"
                    st.button(
                        f"↗  {label}",
                        key=f"continue_{card['id']}",
                        on_click=_open_card,
                        args=(thread_id, card["id"]),
                    )

        st.markdown('<span class="shelf-label">QUICK TOOLS</span>', unsafe_allow_html=True)
        with st.container(key="quick_actions", horizontal=True, gap="small"):
            for mode in ("pattern", "diagnose", "technique", "tools"):
                title, _ = _COMMANDS[mode]
                st.button(
                    title,
                    key=f"quick_{mode}",
                    on_click=_set_mode,
                    args=(mode,),
                )


def _render_work_card(card: dict) -> None:
    with st.container(border=True):
        label = _CARD_LABELS.get(card["type"], "작업")
        st.markdown(ui.tag(label), unsafe_allow_html=True)
        st.markdown(f"**{card['title']}**")
        st.caption(card["summary"])
        st.button(
            "작업대에서 자세히 보기 →",
            key=f"card_{card['id']}",
            on_click=lambda card_id=card["id"]: setattr(st.session_state, "selected_work_card_id", card_id),
        )


def _render_messages() -> None:
    thread = active_thread()
    cards = {card["id"]: card for card in thread["work_cards"]}
    for message in thread["messages"]:
        with st.chat_message(message["role"], avatar="🧶" if message["role"] == "assistant" else None):
            if message.get("image"):
                st.image(message["image"], caption=message.get("image_name"), width=300)
            st.markdown(message["content"])
            for card_id in message.get("card_ids", []):
                if card_id in cards:
                    _render_work_card(cards[card_id])
            if DEBUG_MODE and message.get("debug"):
                with st.expander("개발자 정보"):
                    st.json(message["debug"])


def _record_agent_result(result: dict) -> None:
    response = result.get("user_response") or str(result["messages"][-1].content)
    assistant_id = append_message("assistant", response, card_ids=[], debug=debug_metadata(result))
    card_ids = attach_work_cards(result, assistant_id)
    active_thread()["messages"][-1]["card_ids"] = card_ids
    if card_ids and result.get("pattern_draft"):
        st.session_state.selected_work_card_id = card_ids[0]


def _handle_chat_submission(submission) -> None:
    prompt = submission if isinstance(submission, str) else submission.text
    files = [] if isinstance(submission, str) else list(submission.files)
    if not prompt.strip():
        st.warning("사진과 함께 궁금한 점도 적어 주세요.")
        return

    mode = st.session_state.composer_mode
    prefixes = {
        "diagnose": "이 작품에서 막힌 부분을 진단해줘. ",
        "technique": "이 동작을 처음 배우는 사람에게 차분히 가르쳐줘. ",
        "tools": "이 작품에 맞는 실과 바늘을 추천해줘. ",
        "pattern_read": "이 도안을 초보자가 이해하기 쉽게 풀어 설명해줘. ",
    }
    context = st.session_state.composer_context
    agent_prompt = f"{context}{prefixes.get(mode, '')}{prompt}".strip()
    image = files[0] if files else None
    image_bytes = image.getvalue() if image else None
    append_message(
        "user",
        prompt,
        image=image_bytes,
        image_name=image.name if image else None,
    )

    temp_path = temporary_image(image_bytes, Path(image.name).suffix.lower()) if image else None
    try:
        status = "사진에서 코의 흐름을 살펴보는 중이에요..." if image else "질문에 필요한 기법을 정리하는 중이에요..."
        with st.spinner(status):
            result = invoke_turn(
                get_agent(),
                agent_prompt,
                active_thread()["id"],
                str(temp_path) if temp_path else None,
                original_image_name=image.name if image else "",
            )
        _record_agent_result(result)
    except Exception as error:
        append_message("assistant", f"작업을 마치지 못했어요. 입력을 조금 바꿔 다시 알려주세요.\n\n`{error}`")
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)

    st.session_state.composer_mode = "chat"
    st.session_state.composer_context = ""
    st.rerun()


def _seed_pattern_form(prefix: str, preset_key: str) -> None:
    preset = PROJECT_PRESETS[st.session_state[preset_key]]
    for field in ("tool_type", "finished_size", "yarn_weight", "tool_size", "gauge", "skill_level"):
        st.session_state[f"{prefix}_{field}"] = preset[field]


@st.dialog(
    "사진으로 도안 만들기",
    width="large",
    on_dismiss=_dismiss_pattern_dialog,
)
def _render_pattern_dialog() -> None:
    thread_id = active_thread()["id"]
    prefix = f"pattern_{thread_id}"
    preset_key = f"{prefix}_preset"
    st.markdown(
        '<div class="dialog-note">사진과 제작 조건을 함께 살펴보고, 검증 가능한 초안을 만들게요.</div>',
        unsafe_allow_html=True,
    )
    if preset_key not in st.session_state:
        st.session_state[preset_key] = DEFAULT_PRESET
        _seed_pattern_form(prefix, preset_key)

    st.selectbox(
        "시작 형태",
        PRESET_NAMES,
        key=preset_key,
        on_change=_seed_pattern_form,
        args=(prefix, preset_key),
    )
    image = st.file_uploader("참고할 작품 사진", type=["png", "jpg", "jpeg", "webp"], key=f"{prefix}_image")
    with st.form(f"{prefix}_form"):
        first, second = st.columns(2)
        with first:
            st.selectbox(
                "뜨개 방식",
                ["auto", "crochet", "needle_knitting"],
                key=f"{prefix}_tool_type",
                format_func={"auto": "자동 감지", "crochet": "코바늘", "needle_knitting": "대바늘"}.get,
            )
            st.text_input("원하는 완성 크기", key=f"{prefix}_finished_size")
            st.text_input("실 굵기·종류", key=f"{prefix}_yarn_weight")
        with second:
            st.text_input("바늘 크기", key=f"{prefix}_tool_size")
            st.text_input("게이지", key=f"{prefix}_gauge")
            st.selectbox(
                "나의 수준",
                ["beginner", "confident_beginner", "intermediate"],
                key=f"{prefix}_skill_level",
                format_func={"beginner": "초보", "confident_beginner": "기초 경험 있음", "intermediate": "중급"}.get,
            )
        st.text_area("추가 요청", key=f"{prefix}_notes", placeholder="예: 손잡이는 짧게 하고 안감 없이 만들고 싶어요.")
        submitted = st.form_submit_button("도안 초안 만들기", type="primary", use_container_width=True)

    if st.button("닫기", key=f"{prefix}_cancel"):
        _set_mode("chat")
        st.rerun()
    if not submitted:
        return

    preset_name = st.session_state[preset_key]
    required = [
        st.session_state[f"{prefix}_finished_size"].strip(),
        st.session_state[f"{prefix}_yarn_weight"].strip(),
        st.session_state[f"{prefix}_tool_size"].strip(),
    ]
    if not all(required):
        st.warning("완성 크기, 실 굵기와 바늘 크기는 비워둘 수 없어요.")
        return
    if image is None and not PROJECT_PRESETS[preset_name]["sample"]:
        st.warning("작품 사진을 첨부하거나 샘플 숄더백을 선택해 주세요.")
        return

    source = _SAMPLE_IMAGE
    image_name = _SAMPLE_IMAGE.name
    temp_path = None
    image_bytes = None
    if image is not None:
        image_bytes = image.getvalue()
        temp_path = temporary_image(image_bytes, Path(image.name).suffix.lower())
        source = temp_path
        image_name = image.name

    options = {
        key: st.session_state[f"{prefix}_{key}"]
        for key in ("tool_type", "finished_size", "yarn_weight", "tool_size", "gauge", "skill_level", "notes")
    }
    request_summary = (
        f"{preset_name} 도안을 만들어줘\n\n"
        f"완성 크기 {options['finished_size']} · {options['yarn_weight']} · {options['tool_size']}"
    )
    append_message("user", request_summary, image=image_bytes, image_name=image.name if image else image_name)
    try:
        with st.spinner("사진에서 구조를 읽고, 뜨는 순서를 정리하는 중이에요..."):
            result = invoke_turn(
                get_agent(),
                "이 이미지로 도안을 만들어줘",
                active_thread()["id"],
                str(source),
                task="generate_pattern",
                pattern_options=options,
                original_image_name=image_name,
            )
        _record_agent_result(result)
    except Exception as error:
        append_message("assistant", f"도안 초안을 마치지 못했어요. 조건을 확인해 다시 시도해 주세요.\n\n`{error}`")
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
    st.session_state.composer_mode = "chat"
    st.rerun()


def _render_composer() -> None:
    mode = st.session_state.composer_mode
    if mode == "pattern":
        _render_pattern_dialog()

    labels = {
        "chat": "사진이나 도안을 올리고, 막힌 곳을 이야기해 주세요",
        "diagnose": "문제 부위 사진을 올리고 어떤 점이 어려운지 알려주세요",
        "technique": "배우고 싶은 기법이나 현재 어려운 동작을 적어주세요",
        "tools": "만들 작품과 가지고 있는 실을 알려주세요",
        "pattern_read": "도안 이미지나 텍스트를 올리고 어려운 부분을 알려주세요",
    }
    context = st.session_state.composer_context
    placeholder = labels.get(mode, labels["chat"])
    if context:
        placeholder = f"이 작업 이어서 · {context.strip()[:42]}"
    submission = st.chat_input(
        placeholder,
        accept_file=True,
        file_type=["png", "jpg", "jpeg", "webp"],
        max_upload_size=10,
        key=f"workspace_chat_{active_thread()['id']}",
    )
    if submission:
        _handle_chat_submission(submission)


def _list_section(title: str, items: list[str]) -> None:
    if not items:
        return
    st.markdown(f"#### {title}")
    for item in items:
        st.markdown(f"- {item}")


def _render_detail_panel(card: dict) -> None:
    header, close = st.columns([5, 1])
    with header:
        st.markdown(ui.tag(_CARD_LABELS.get(card["type"], "작업")), unsafe_allow_html=True)
        st.markdown(f"## {card['title']}")
    with close:
        st.button("×", key="close_work_panel", on_click=_close_panel, help="작업대 닫기")
    st.write(card["summary"])
    st.divider()
    payload = card["payload"]

    if card["type"] == "pattern":
        metrics = st.columns(3)
        metrics[0].metric("방식", "코바늘" if payload.get("tool_type") == "crochet" else "대바늘")
        metrics[1].metric("확신", payload.get("confidence", "unknown"))
        metrics[2].metric("기법", len(payload.get("techniques", [])))
        _list_section("준비물", payload.get("materials", []))
        if payload.get("gauge_guidance"):
            st.markdown("#### 게이지")
            st.write(payload["gauge_guidance"])
        _list_section("작품 구조", payload.get("construction", []))
        _list_section("뜨는 순서", payload.get("instructions", []))
        _list_section("마무리", payload.get("finishing", []))
        with st.expander("사진에서 확인할 수 없어 가정한 내용"):
            _list_section("가정", payload.get("assumptions", []))
            _list_section("추가로 있으면 좋은 사진", payload.get("additional_photos", []))
        st.button(
            "이 도안 수정하기",
            key=f"revise_{card['id']}",
            on_click=_use_card_context,
            args=(f"'{card['title']}' 도안을 수정하고 싶어요. ",),
            use_container_width=True,
            type="primary",
        )
    elif card["type"] == "diagnosis":
        _list_section("사진에서 확인한 부분", payload.get("findings", []))
        _list_section("원인 후보", payload.get("diagnoses", []))
        _list_section("먼저 고쳐볼 것", payload.get("fixes", []))
        st.button(
            "이 부분을 다시 설명해줘",
            key=f"explain_{card['id']}",
            on_click=_use_card_context,
            args=(f"'{card['title']}' 진단 내용을 더 쉽게 설명해줘. ",),
            use_container_width=True,
        )
    elif card["type"] == "technique":
        _list_section("함께 본 기법", payload.get("techniques", []))
        st.markdown("#### 선생님 메모")
        st.write(payload.get("summary", ""))
        if payload.get("check"):
            st.info(payload["check"])
        st.button(
            "이 기법으로 연습하기",
            key=f"practice_tech_{card['id']}",
            on_click=_use_card_context,
            args=(f"'{card['title']}' 기법을 직접 연습할 순서를 알려줘. ",),
            use_container_width=True,
        )
    else:
        st.markdown("#### 오늘의 짧은 연습")
        st.write(payload.get("plan", ""))
        if payload.get("check"):
            st.info(payload["check"])
        if payload.get("next_action"):
            st.markdown("#### 다음 행동")
            st.write(payload["next_action"])
        st.button(
            "연습 결과 이야기하기",
            key=f"continue_practice_{card['id']}",
            on_click=_use_card_context,
            args=(f"'{card['title']}' 연습 결과를 이야기할게. ",),
            use_container_width=True,
        )


def render() -> None:
    initialize_session()
    _render_sidebar()
    if st.session_state.workspace_view == "techniques":
        from views import techniques

        techniques.render(on_ask=_ask_about_technique)
        return
    selected = find_work_card(st.session_state.selected_work_card_id)
    has_messages = bool(active_thread()["messages"])

    if not has_messages:
        with st.container(key="empty_stage"):
            left_space, center, right_space = st.columns([1, 2.2, 1])
            with center:
                _render_welcome_header()
                with st.container(key="empty_composer"):
                    _render_composer()
                _render_action_shelf()
        return

    if selected:
        conversation, detail = st.columns([1.65, 1], gap="large")
    else:
        conversation, detail = st.container(key="conversation_shell"), None

    with conversation:
        st.markdown(
            '<div class="workspace-heading"><span class="workspace-thread"></span>'
            '<div><strong>공방 선생님과 작업 중</strong><small>결과 카드는 옆 작업대에 펼쳐볼 수 있어요.</small></div></div>',
            unsafe_allow_html=True,
        )
        _render_messages()

    if detail is not None:
        with detail:
            st.markdown('<span class="detail-panel-marker"></span>', unsafe_allow_html=True)
            with st.container(border=True, key="detail_panel"):
                _render_detail_panel(selected)

    # At root level Streamlit places chat_input in its fixed bottom container.
    # Empty conversations render the same composer inside a centered container above.
    _render_composer()
