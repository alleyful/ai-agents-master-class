"""Chat-first KnitCoach workspace with a work LNB and inspectable result cards."""

from pathlib import Path

import streamlit as st

import ui
from nav import PHOTO_PATTERN_UI_ENABLED, WORKSHOP_TOOLS
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
from content.techniques import resolve_techniques
from domain.curricula import CURATED_BEGINNER_PROJECT_IDS, CURRICULA, current_curriculum_step
from domain.journeys import JOURNEY_DEFINITIONS
from domain.models import JourneyType
from domain.project_patterns import phase_index_for_step, phase_progress, phases_for_project
from knitcoach import DEBUG_MODE, invoke_turn
from model_provider import active_provider_name, provider_status_label
from views.project_workbench import render_project_workbench

_SAMPLE_IMAGE = Path(__file__).resolve().parent.parent / "samples" / "crochet-mesh-shoulder-bag.png"
_BASE_DIR = Path(__file__).resolve().parent.parent
_CARD_LABELS = {
    "pattern": "도안",
    "diagnosis": "문제 진단",
    "technique": "기법",
    "practice": "연습",
    "tools": "도구",
    "project_gallery": "입문 작품",
    "learning_step": "진행",
    "purchase_kit": "첫 구매 안내",
}
_MODE_TO_JOURNEY = {
    "pattern": JourneyType.RECREATE_FROM_PHOTO,
    "diagnose": JourneyType.DIAGNOSE_PROJECT,
    "technique": JourneyType.CONTINUE_LEARNING,
    "tools": JourneyType.START_FROM_MATERIALS,
    "pattern_read": JourneyType.EXPLAIN_PATTERN,
}


def _set_mode(mode: str) -> None:
    st.session_state.workspace_view = "chat"
    st.session_state.composer_mode = mode
    st.session_state.composer_context = ""
    if mode in _MODE_TO_JOURNEY:
        st.session_state.selected_journey = _MODE_TO_JOURNEY[mode].value


def _select_journey(journey_value: str) -> None:
    journey = JourneyType(journey_value)
    st.session_state.workspace_view = "chat"
    st.session_state.selected_journey = journey.value
    st.session_state.composer_mode = JOURNEY_DEFINITIONS[journey].mode
    st.session_state.composer_context = ""


def _run_quick_start(prompt: str, journey_value: str) -> None:
    """Start a useful coaching turn directly from the empty-state choices."""
    journey = JourneyType(journey_value)
    st.session_state.selected_journey = journey.value
    st.session_state.composer_mode = JOURNEY_DEFINITIONS[journey].mode
    append_message("user", prompt, journey=journey.value)
    with st.spinner("선택한 내용으로 첫 안내를 준비하는 중이에요..."):
        result = invoke_turn(get_agent(), prompt, active_thread()["id"])
    _record_agent_result(result)
    st.session_state.composer_mode = "chat"
    st.session_state.composer_context = ""


def _show_all_starter_projects() -> None:
    st.session_state.show_all_starter_projects = True


def _open_technique_library() -> None:
    st.session_state.workspace_view = "techniques"
    st.session_state.composer_mode = "chat"
    st.session_state.selected_work_card_id = None


def _open_technique_detail(name: str) -> None:
    """Open the authored lesson pack for the technique clicked in a workbench."""
    matches = resolve_techniques(name)
    if matches:
        st.session_state.selected_technique = matches[0].name
    st.session_state.workspace_view = "techniques"
    st.session_state.composer_mode = "chat"
    st.session_state.selected_work_card_id = None


def _open_tool_library() -> None:
    st.session_state.workspace_view = "tools"
    st.session_state.composer_mode = "chat"


def _ask_about_technique(name: str) -> None:
    st.session_state.workspace_view = "chat"
    st.session_state.composer_mode = "technique"
    st.session_state.selected_journey = JourneyType.CONTINUE_LEARNING.value
    st.session_state.composer_context = f"{name.split('(')[0]}에 대해 질문할게요. "


def _ask_about_tool(name: str) -> None:
    st.session_state.workspace_view = "chat"
    st.session_state.composer_mode = "tools"
    st.session_state.selected_journey = JourneyType.START_FROM_MATERIALS.value
    st.session_state.composer_context = f"{name}을(를) 내 프로젝트에 맞게 추천해줘. "


def _open_card(thread_id: str, card_id: str) -> None:
    activate_thread(thread_id)
    st.session_state.selected_work_card_id = card_id


def _close_panel() -> None:
    st.session_state.selected_work_card_id = None


def _use_card_context(text: str) -> None:
    st.session_state.composer_mode = "chat"
    st.session_state.composer_context = text


def _choose_curated_project(curriculum_id: str) -> None:
    """Turn a visual project choice into the next coaching turn."""
    curriculum = CURRICULA[curriculum_id]
    prompt = f"{curriculum.title}을 선택할게요"
    append_message("user", prompt, journey=JourneyType.START_FROM_ZERO.value)
    with st.spinner("선택한 작품의 준비물을 정리하는 중이에요..."):
        result = invoke_turn(get_agent(), prompt, active_thread()["id"])
    _record_agent_result(result)
    st.session_state.composer_mode = "chat"
    st.session_state.composer_context = ""
    st.toast(f"{curriculum.title} 선택 완료 · 아래에서 준비물을 확인하세요.", icon="🧶")


def _complete_learning_step(curriculum_id: str, expected_index: int) -> None:
    """Persist the visible step and move to the next one without phrase guessing."""
    program = active_thread().get("learning_program", {})
    if (
        program.get("curriculum_id") != curriculum_id
        or program.get("status") not in {"active", "preview"}
        or program.get("current_step") != expected_index
    ):
        return
    curriculum = CURRICULA[curriculum_id]
    step = curriculum.steps[expected_index]
    prompt = f"{step.title} 다음 단계 미리보기" if program.get("status") == "preview" else f"{step.title} 단계 완료"
    append_message("user", prompt, journey=JourneyType.CONTINUE_LEARNING.value)
    with st.spinner("진도를 저장하고 다음 단을 여는 중이에요..."):
        result = invoke_turn(
            get_agent(),
            prompt,
            active_thread()["id"],
            learning_program=program,
        )
    _record_agent_result(result)


def _focus_learning_step(curriculum_id: str, expected_index: int) -> None:
    """Open the current step explanation without completing or advancing it."""
    program = active_thread().get("learning_program", {})
    if (
        program.get("curriculum_id") != curriculum_id
        or program.get("status") not in {"active", "preview"}
        or program.get("current_step") != expected_index
    ):
        return
    prompt = "현재 단계부터 자세히 설명해줘"
    append_message("user", prompt, journey=JourneyType.CONTINUE_LEARNING.value)
    with st.spinner("현재 단계의 동작과 완료 기준을 여는 중이에요..."):
        result = invoke_turn(get_agent(), prompt, active_thread()["id"], learning_program=program)
    _record_agent_result(result)


def _start_learning_from_purchase(curriculum_id: str, preview: bool = False) -> None:
    """Move from the purchase card into real practice or a non-recording preview."""
    program = active_thread().get("learning_program", {})
    allowed_statuses = {"awaiting_tools", "shopping"} if preview else {"awaiting_tools", "shopping", "preview", "preview_complete"}
    if program.get("curriculum_id") != curriculum_id or program.get("status") not in allowed_statuses:
        return
    prompt = "도구 없이 단계별 과정을 먼저 볼게요" if preview else "준비됐어요. 1단부터 시작할게요"
    append_message("user", prompt, journey=JourneyType.CONTINUE_LEARNING.value)
    with st.spinner("작품의 첫 단계를 여는 중이에요..."):
        result = invoke_turn(get_agent(), prompt, active_thread()["id"], learning_program=program)
    _record_agent_result(result)


def _technique_labels(curriculum) -> list[str]:
    labels: list[str] = []
    for step in curriculum.steps:
        label = step.technique.split("(")[0].strip()
        if label not in labels:
            labels.append(label)
    return labels


def _render_project_gallery(card: dict) -> None:
    curriculum_ids = [item for item in card["payload"].get("curriculum_ids", []) if item in CURRICULA]
    if not curriculum_ids:
        return
    active_program = active_thread().get("learning_program", {})
    selected_id = active_program.get("curriculum_id")
    compact = card["payload"].get("compact", False)
    with st.container(key=f"project_board_{card['id']}"):
        if selected_id in curriculum_ids:
            curriculum = CURRICULA[selected_id]
            with st.container(border=True, key=f"selected_project_{card['id']}"):
                image_column, copy_column = st.columns([1, 3], gap="medium")
                with image_column:
                    image_path = _BASE_DIR / curriculum.cover_image
                    if curriculum.cover_image and image_path.exists():
                        st.image(str(image_path), use_container_width=True)
                with copy_column:
                    st.markdown(ui.tag("선택한 첫 작품"), unsafe_allow_html=True)
                    st.markdown(f"#### {curriculum.title}")
                    st.caption(curriculum.outcome)
                    st.success("선택 완료 · 바로 아래에서 준비물을 확인하세요.")
            return
        if not compact:
            st.markdown('<span class="project-board-kicker">BEGINNER PROJECT MENU</span>', unsafe_allow_html=True)
            st.markdown("### 사진으로 고르는 첫 작품")
            st.caption("완성 모습부터 고르세요. 작품을 정한 뒤에만 도구를 확인하고 기법 연습을 시작합니다.")
        if compact:
            for start in range(0, len(curriculum_ids), 2):
                for column, curriculum_id in zip(st.columns(2, gap="small"), curriculum_ids[start:start + 2]):
                    curriculum = CURRICULA[curriculum_id]
                    with column:
                        with st.container(border=True, key=f"compact_project_{card['id']}_{curriculum_id}"):
                            image_column, copy_column = st.columns([1, 1.65], gap="small", vertical_alignment="center")
                            with image_column:
                                image_path = _BASE_DIR / curriculum.cover_image
                                if curriculum.cover_image and image_path.exists():
                                    st.image(str(image_path), use_container_width=True)
                            with copy_column:
                                craft = "코바늘" if curriculum.tool_type == "crochet" else "대바늘"
                                st.markdown(ui.tag(craft), unsafe_allow_html=True)
                                st.markdown(f"**{curriculum.title}**")
                                st.caption(curriculum.outcome)
                                st.button(
                                    "이 작품 선택 →",
                                    key=f"compact_choose_{card['id']}_{curriculum_id}",
                                    on_click=_choose_curated_project,
                                    args=(curriculum_id,),
                                    use_container_width=True,
                                )
            return
        for start in range(0, len(curriculum_ids), 3):
            for column, curriculum_id in zip(st.columns(3, gap="small"), curriculum_ids[start:start + 3]):
                curriculum = CURRICULA[curriculum_id]
                with column:
                    with st.container(border=True, key=f"project_choice_{card['id']}_{curriculum_id}"):
                        image_path = _BASE_DIR / curriculum.cover_image
                        if curriculum.cover_image and image_path.exists():
                            st.image(str(image_path), use_container_width=True)
                        craft = "코바늘" if curriculum.tool_type == "crochet" else "대바늘"
                        st.markdown(ui.tag(f"{craft} · {curriculum.badge}"), unsafe_allow_html=True)
                        st.markdown(f"#### {curriculum.title}")
                        st.caption(curriculum.outcome)
                        if not compact:
                            st.markdown(
                                f'<div class="project-facts"><span>{curriculum.difficulty}</span>'
                                f'<span>{curriculum.estimated_time}</span></div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"**배우는 기법** · {' · '.join(_technique_labels(curriculum))}")
                            if curriculum.recommended_for:
                                st.caption(f"이런 분께: {curriculum.recommended_for}")
                        is_selected = selected_id == curriculum_id
                        st.button(
                            "선택한 작품" if is_selected else "이 작품으로 시작하기 →",
                            key=f"choose_{card['id']}_{curriculum_id}",
                            on_click=_choose_curated_project,
                            args=(curriculum_id,),
                            use_container_width=True,
                            type="primary" if is_selected else "secondary",
                            disabled=bool(selected_id),
                        )


def _render_learning_step_card(card: dict) -> None:
    card_program = card["payload"].get("learning_program", {})
    curriculum_id = card_program.get("curriculum_id")
    index = card_program.get("current_step", 0)
    if curriculum_id not in CURRICULA or index >= len(CURRICULA[curriculum_id].steps):
        return
    curriculum = CURRICULA[curriculum_id]
    step = curriculum.steps[index]
    active_program = active_thread().get("learning_program", {})
    is_current = (
        active_program.get("curriculum_id") == curriculum_id
        and active_program.get("status") in {"active", "preview"}
        and active_program.get("status") == card_program.get("status")
        and active_program.get("current_step") == index
    )
    with st.container(border=True, key=f"learning_step_{card['id']}"):
        st.markdown(ui.tag("현재 단"), unsafe_allow_html=True)
        st.markdown(f"**{step.title}**")
        is_preview = active_program.get("status") == "preview"
        st.caption("읽은 뒤 다음 단계를 계속 둘러보세요." if is_preview else "완료 확인 기준을 만족했다면 아래 버튼으로 바로 다음 단을 여세요.")
        st.button(
            ("다음 단계 미리보기 →" if is_preview else f"{step.title} 완료하고 다음으로 →") if is_current else "완료된 단계",
            key=f"complete_{card['id']}",
            on_click=_complete_learning_step,
            args=(curriculum_id, index),
            use_container_width=True,
            type="primary",
            disabled=not is_current,
        )


def _render_technique_strip(card: dict) -> None:
    names = card["payload"].get("techniques", [])
    if not names:
        return
    with st.container(border=True, key=f"technique_strip_{card['id']}"):
        st.caption("이번 단계에서 새로 쓰는 기법")
        with st.container(horizontal=True, gap="small"):
            for name in names:
                label = name.split("(")[0].strip()
                st.button(
                    f"⌘ {label}",
                    key=f"technique_chip_{card['id']}_{label}",
                    on_click=lambda card_id=card["id"]: setattr(st.session_state, "selected_work_card_id", card_id),
                )


def _render_purchase_kit(card: dict) -> None:
    payload = card["payload"]
    yarn = payload.get("yarn", {})
    tools = payload.get("tools", [])
    with st.container(border=True, key=f"purchase_kit_{card['id']}"):
        st.markdown(ui.tag("준비물이 없을 때"), unsafe_allow_html=True)
        st.markdown(f"### {payload.get('title', '첫 작품')} · 이것만 준비하세요")
        st.caption("지금 살 필요는 없어요. 전체 과정을 먼저 본 뒤 시작하고 싶을 때만 준비하세요.")

        cover, yarn_copy = st.columns([1, 2.2], gap="medium")
        with cover:
            cover_path = _BASE_DIR / payload.get("cover_image", "")
            if payload.get("cover_image") and cover_path.exists():
                st.image(str(cover_path), use_container_width=True)
        with yarn_copy:
            st.markdown("**① 실**")
            st.markdown(f"**{yarn.get('name', '')} · {yarn.get('quantity', '')}**")
            st.write(yarn.get("check", ""))
            if yarn.get("avoid"):
                st.caption(f"처음에는 피하기 · {yarn['avoid']}")

        if payload.get("reference_video_url"):
            st.link_button(
                f"완성 영상 보기 · {payload.get('reference_video_title', '작품 튜토리얼')} ↗",
                payload["reference_video_url"],
                use_container_width=True,
            )

        with st.container(border=True, key=f"pattern_spec_{card['id']}"):
            st.markdown("**이 재료로 완성되는 기준**")
            st.markdown(
                f"**바늘** {payload.get('needle_size', '')}  ·  "
                f"**완성 크기** {payload.get('finished_size', '')}"
            )
            if payload.get("gauge") and payload.get("curriculum_id") != "needle-garter-scarf":
                st.caption(f"게이지 · {payload['gauge']}")
            st.caption(f"구조 · {payload.get('construction', '')}")

        st.markdown("**② 도구 · 사진과 규격으로 확인**")
        for start in range(0, len(tools), 2):
            for column, tool in zip(st.columns(2, gap="medium"), tools[start:start + 2]):
                with column:
                    image_path = _BASE_DIR / tool.get("image", "")
                    if tool.get("image") and image_path.exists():
                        st.image(str(image_path), use_container_width=True)
                    st.markdown(f"**{tool['name']}**")
                    st.caption(tool.get("spec", ""))

        extras = payload.get("extras", [])
        if extras:
            st.markdown("**③ 작품 부자재** · " + " · ".join(extras))

        st.markdown("**어디서 살까요?**")
        for store in payload.get("stores", []):
            store_copy, store_link = st.columns([3, 1], vertical_alignment="center")
            with store_copy:
                st.markdown(f"**{store['name']}** · {store['best_for']}")
                st.caption(store["note"])
            with store_link:
                st.link_button("매장 보기 ↗", store["url"], use_container_width=True)
        st.markdown("---")
        st.markdown("**다음 단계로 이동**")
        ready_column, preview_column = st.columns(2, gap="medium")
        curriculum_id = payload.get("curriculum_id", "")
        current_program = active_thread().get("learning_program", {})
        current_status = current_program.get("status") if current_program.get("curriculum_id") == curriculum_id else ""
        with ready_column:
            st.button(
                "준비됐어요 · 1단 시작 →",
                key=f"purchase_ready_{card['id']}",
                on_click=_start_learning_from_purchase,
                args=(curriculum_id, False),
                use_container_width=True,
                type="primary",
                disabled=current_status not in {"awaiting_tools", "shopping", "preview", "preview_complete"},
            )
        with preview_column:
            st.button(
                "도구 없이 먼저 보기 →",
                key=f"purchase_preview_{card['id']}",
                on_click=_start_learning_from_purchase,
                args=(curriculum_id, True),
                use_container_width=True,
                disabled=current_status not in {"awaiting_tools", "shopping"},
            )
        st.caption("먼저 보기는 진도를 완료 처리하지 않아요. 준비물이 생기면 1단부터 실제 과정으로 다시 시작합니다.")


def _dismiss_pattern_dialog() -> None:
    st.session_state.composer_mode = "chat"


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="brand-mark"><span class="stitch-mark">KN</span>'
            '<div><strong>KnitCoach</strong><small>뜨개 코칭 작업실</small></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="stitched-rule"></div>', unsafe_allow_html=True)
        with st.container(key="lnb_new"):
            st.button("＋  새 뜨개 대화", on_click=create_thread, use_container_width=True, type="primary")

        with st.container(key="lnb_recent"):
            st.markdown('<p class="lnb-label">최근 뜨개</p>', unsafe_allow_html=True)
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

        program = active_thread().get("learning_program", {})
        if program and program.get("curriculum_id") in CURRICULA:
            curriculum = CURRICULA[program["curriculum_id"]]
            completed = len(program.get("completed_steps", []))
            total = len(curriculum.steps)
            step = current_curriculum_step(program)
            with st.container(key="lnb_learning_path"):
                st.markdown('<p class="lnb-label">진행 중인 작품</p>', unsafe_allow_html=True)
                st.markdown(f"**{curriculum.title}**")
                st.progress(completed / total, text=f"전체 진도 {completed}/{total}")
                if program.get("status") == "awaiting_tools":
                    st.info("준비물 확인 중 · 연습 시작 전")
                elif program.get("status") == "shopping":
                    st.info("구매 목록 확인 중 · 먼저 둘러봐도 좋아요")
                elif program.get("status") == "preview":
                    st.info(f"작품 과정 미리보기 · {program.get('current_step', 0) + 1}/{total}")
                    st.button(
                        "현재 단계 자세히 열기 →",
                        key=f"lnb_focus_preview_{curriculum.id}_{program.get('current_step', 0)}",
                        on_click=_focus_learning_step,
                        args=(curriculum.id, program.get("current_step", 0)),
                        use_container_width=True,
                    )
                elif step:
                    phases = phases_for_project(curriculum.id)
                    if phases:
                        phase = phases[phase_index_for_step(curriculum.id, step.id)]
                        phase_current, phase_total = phase_progress(curriculum.id, step.id)
                        detail = f" · {phase_current}/{phase_total}" if phase_total > 1 else ""
                        st.caption(f"지금: {phase.title}{detail} · {step.title}")
                    else:
                        st.caption(f"지금: {step.title}")
                    st.button(
                        "현재 단계 자세히 열기 →",
                        key=f"lnb_focus_step_{curriculum.id}_{program.get('current_step', 0)}",
                        on_click=_focus_learning_step,
                        args=(curriculum.id, program.get("current_step", 0)),
                        use_container_width=True,
                    )
                else:
                    st.success("작품 완료" if curriculum.written_pattern else "기법 완료 · 작품 제작 단계")

        with st.container(key="lnb_tools"):
            st.markdown('<p class="lnb-label">뜨개 자료실</p>', unsafe_allow_html=True)
            for mode, icon, label in WORKSHOP_TOOLS:
                library_callbacks = {"technique_library": _open_technique_library, "tool_library": _open_tool_library}
                callback = library_callbacks.get(mode, _set_mode)
                args = () if mode in library_callbacks else (mode,)
                is_active_library = (
                    (mode == "technique_library" and st.session_state.workspace_view == "techniques")
                    or (mode == "tool_library" and st.session_state.workspace_view == "tools")
                )
                st.button(
                    f"{icon}  {label}",
                    key=f"lnb_{mode}",
                    on_click=callback,
                    args=args,
                    use_container_width=True,
                    type="primary" if is_active_library else "secondary",
                )

        st.markdown('<div class="sidebar-spacer"></div><div class="lnb-knit-strip" aria-hidden="true"></div>', unsafe_allow_html=True)
        status, status_caption = provider_status_label()
        status_class = "system-status demo" if active_provider_name() == "rules" else "system-status"
        st.markdown(f'<div class="{status_class}"><i></i> {status}</div>', unsafe_allow_html=True)
        st.caption(status_caption)


def _latest_cards() -> list[tuple[str, dict]]:
    cards: list[tuple[str, dict, float]] = []
    for thread in recent_threads():
        for card in reversed(thread["work_cards"]):
            cards.append((thread["id"], card, thread["updated_at"]))
    cards.sort(key=lambda item: item[2], reverse=True)
    return [(thread_id, card) for thread_id, card, _ in cards[:3]]


def _render_welcome_header() -> None:
    journey = JourneyType(st.session_state.selected_journey)
    definition = JOURNEY_DEFINITIONS[journey]
    st.markdown(
        f"""
        <section class="workbench-welcome">
          {ui.eyebrow("READY AT THE WORKBENCH")}
          <h1>오늘은 어떤 뜨개를 같이 볼까요?</h1>
          <p>지금의 경험과 목적에 가까운 항목을 고르거나, 편하게 이야기해 주세요.</p>
          <div class="journey-current"><strong>{definition.title}</strong><span>{definition.prompt}</span></div>
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

        st.markdown('<span class="shelf-label">원하는 도움을 선택하세요</span>', unsafe_allow_html=True)
        journeys = [
            (journey, definition)
            for journey, definition in JOURNEY_DEFINITIONS.items()
            if journey != JourneyType.START_FROM_MATERIALS
            and (PHOTO_PATTERN_UI_ENABLED or journey != JourneyType.RECREATE_FROM_PHOTO)
        ]
        for column, (journey, definition) in zip(st.columns(len(journeys), gap="small"), journeys):
            with column:
                selected = journey.value == st.session_state.selected_journey
                st.button(
                    f"{definition.icon}  {definition.title}",
                    key=f"journey_{journey.value}",
                    on_click=_select_journey,
                    args=(journey.value,),
                    use_container_width=True,
                    type="primary" if selected else "secondary",
                )


def _render_quick_start_buttons(items: list[tuple[str, str]], journey: JourneyType, key_prefix: str) -> None:
    for start in range(0, len(items), 2):
        for column, (label, prompt) in zip(st.columns(2, gap="small"), items[start:start + 2]):
            with column:
                st.button(
                    label,
                    key=f"{key_prefix}_{start}_{label}",
                    on_click=_run_quick_start,
                    args=(prompt, journey.value),
                    use_container_width=True,
                )


def _render_journey_starter() -> None:
    """Show a real next action after a journey is selected; typing stays optional."""
    journey = JourneyType(st.session_state.selected_journey)
    with st.container(border=True, key=f"journey_starter_{journey.value}"):
        if journey == JourneyType.START_FROM_ZERO:
            st.markdown("### 첫 작품 2개 중 골라보세요")
            st.caption("가장 단순한 코바늘·대바늘 작품을 하나씩 골랐어요. 선택하면 준비물부터 확인합니다.")
            featured = ["crochet-round-coaster", "needle-garter-scarf"]
            ids = CURATED_BEGINNER_PROJECT_IDS if st.session_state.get("show_all_starter_projects") else featured
            _render_project_gallery({"id": "welcome_projects", "payload": {"curriculum_ids": ids, "compact": True}})
            if len(ids) < len(CURATED_BEGINNER_PROJECT_IDS):
                st.button(
                    "다른 입문 작품도 보기 ↓",
                    key="show_all_starter_projects",
                    on_click=_show_all_starter_projects,
                    use_container_width=True,
                )
        elif journey == JourneyType.CONTINUE_LEARNING:
            st.markdown("### 기억나는 기법부터 선택하세요")
            st.caption("어디까지 배웠는지 정확히 몰라도 괜찮아요. 선택한 기법의 성공 기준부터 확인합니다.")
            _render_quick_start_buttons(
                [
                    ("사슬뜨기 이어보기 →", "사슬뜨기를 배웠는데 현재 수준을 확인하고 다음 연습을 안내해줘"),
                    ("짧은뜨기 이어보기 →", "짧은뜨기를 배웠는데 현재 수준을 확인하고 다음 연습을 안내해줘"),
                    ("겉뜨기 이어보기 →", "겉뜨기를 배웠는데 현재 수준을 확인하고 다음 연습을 안내해줘"),
                    ("안뜨기 이어보기 →", "안뜨기를 배웠는데 현재 수준을 확인하고 다음 연습을 안내해줘"),
                ],
                journey,
                "continue_quick",
            )
            st.button("기법 보관함에서 직접 찾기 →", on_click=_open_technique_library, use_container_width=True)
        elif journey == JourneyType.DIAGNOSE_PROJECT:
            st.markdown("### 지금 보이는 문제를 골라보세요")
            st.caption("버튼만 눌러도 먼저 확인할 원인과 수정 순서를 안내합니다. 사진은 다음 메시지에서 추가해도 돼요.")
            _render_quick_start_buttons(
                [
                    ("가장자리가 휘어요 →", "뜨고 있는 작품의 가장자리가 휘어요. 사진 없이 먼저 확인할 항목부터 알려줘"),
                    ("코 수가 달라져요 →", "단마다 코 수가 달라져요. 초보자가 먼저 확인할 위치부터 알려줘"),
                    ("구멍이 생겼어요 →", "원하지 않은 구멍이 생겼어요. 원인 후보와 확인 순서를 알려줘"),
                    ("너무 조이거나 헐거워요 →", "편물이 너무 조이거나 헐거워요. 장력을 확인하고 수정하는 순서를 알려줘"),
                ],
                journey,
                "diagnose_quick",
            )
            st.info("사진으로 확인하려면 아래 입력창의 ＋ 버튼으로 사진만 추가하고, 문제 부위를 짧게 적어주세요.")
        elif journey == JourneyType.RECREATE_FROM_PHOTO:
            st.markdown("### 사진을 올리면 작품 구조부터 정리해요")
            st.caption("사진 선택 창이 열렸습니다. 완성 크기와 뜨개 방식을 고르면 테스트 도안을 만듭니다.")
            st.button("사진 업로드 창 다시 열기 →", on_click=_set_mode, args=("pattern",), use_container_width=True, type="primary")
        elif journey == JourneyType.EXPLAIN_PATTERN:
            st.markdown("### 어려운 도안 형태를 선택하세요")
            st.caption("예시 버튼으로 읽는 법부터 볼 수 있고, 내 도안은 아래 입력창에 그대로 붙여 넣으면 됩니다.")
            _render_quick_start_buttons(
                [
                    ("영문 코바늘 약어 →", "ch, sc, dc, sl st가 들어간 영문 코바늘 도안을 처음 읽는 법을 예시로 알려줘"),
                    ("코바늘 기호 도안 →", "코바늘 기호 도안의 중심, 단 시작, 반복 구간을 찾는 법을 예시로 알려줘"),
                    ("영문 대바늘 약어 →", "K, P, yo, k2tog가 들어간 영문 대바늘 도안을 처음 읽는 법을 예시로 알려줘"),
                    ("반복 구간 찾기 →", "뜨개 도안에서 괄호, 별표, repeat 반복 구간을 찾는 법을 예시로 알려줘"),
                ],
                journey,
                "pattern_read_quick",
            )
        else:
            st.markdown("### 가지고 있는 것과 가장 가까운 항목을 고르세요")
            st.caption("제품명을 몰라도 괜찮아요. 가진 재료를 기준으로 가능한 첫 작품을 좁혀 드립니다.")
            _render_quick_start_buttons(
                [
                    ("실만 있어요 →", "뜨개실만 있고 바늘은 없어요. 실 라벨을 어디서 보고 어떤 작품과 바늘을 고를지 알려줘"),
                    ("코바늘만 있어요 →", "코바늘만 있고 실은 없어요. 바늘 mm를 확인하고 첫 작품용 실을 고르는 법을 알려줘"),
                    ("실과 코바늘이 있어요 →", "중간 굵기 실과 4~5mm 코바늘이 있어요. 만들기 좋은 첫 작품을 추천해줘"),
                    ("실과 대바늘이 있어요 →", "중간 굵기 실과 대바늘이 있어요. 만들기 좋은 첫 작품을 추천해줘"),
                ],
                journey,
                "materials_quick",
            )
            st.button("도구 보관함에서 생김새 확인하기 →", on_click=_open_tool_library, use_container_width=True)

def _render_journey_flow() -> None:
    journey = JourneyType(st.session_state.selected_journey)
    definition = JOURNEY_DEFINITIONS[journey]
    steps = '<span aria-hidden="true">→</span>'.join(
        f'<span class="journey-step{" current" if index == 0 else ""}">{step}</span>'
        for index, step in enumerate(definition.steps)
    )
    st.markdown(f'<div class="journey-flow">{steps}</div>', unsafe_allow_html=True)


def _render_work_card(card: dict) -> None:
    if card["type"] == "project_gallery":
        _render_project_gallery(card)
        return
    if card["type"] == "learning_step":
        card_program = card["payload"].get("learning_program", {})
        active_program = active_thread().get("learning_program", {})
        is_current = (
            card_program.get("curriculum_id") == active_program.get("curriculum_id")
            and card_program.get("status") == active_program.get("status")
            and card_program.get("current_step") == active_program.get("current_step")
            and active_program.get("status") in {"active", "preview"}
        )
        if is_current:
            render_project_workbench(
                card,
                complete_step=_complete_learning_step,
                focus_step=_focus_learning_step,
                open_library=_open_technique_detail,
                base_dir=_BASE_DIR,
            )
        return
    if card["type"] == "technique":
        _render_technique_strip(card)
        return
    if card["type"] == "purchase_kit":
        _render_purchase_kit(card)
        return
    with st.container(border=True):
        label = _CARD_LABELS.get(card["type"], "작업")
        st.markdown(ui.tag(label), unsafe_allow_html=True)
        st.markdown(f"**{card['title']}**")
        st.caption(card["summary"])
        st.button(
            "상세 자료 보기 →",
            key=f"card_{card['id']}",
            on_click=lambda card_id=card["id"]: setattr(st.session_state, "selected_work_card_id", card_id),
        )


def _render_messages() -> None:
    thread = active_thread()
    cards = {card["id"]: card for card in thread["work_cards"]}
    latest_learning_card_id = next(
        (card["id"] for card in reversed(thread["work_cards"]) if card["type"] == "learning_step"),
        None,
    )
    for message in thread["messages"]:
        with st.chat_message(message["role"], avatar="🧶" if message["role"] == "assistant" else None):
            if message.get("image"):
                st.image(message["image"], caption=message.get("image_name"), width=300)
            st.markdown(message["content"])
            for card_id in message.get("card_ids", []):
                if card_id in cards:
                    if cards[card_id]["type"] == "learning_step" and card_id != latest_learning_card_id:
                        continue
                    _render_work_card(cards[card_id])
            if DEBUG_MODE and message.get("debug"):
                with st.expander("개발자 정보"):
                    st.json(message["debug"])


def _record_agent_result(result: dict) -> None:
    response = result.get("user_response") or str(result["messages"][-1].content)
    assistant_id = append_message("assistant", response, card_ids=[], debug=debug_metadata(result))
    card_ids = attach_work_cards(result, assistant_id)
    active_thread()["messages"][-1]["card_ids"] = card_ids
    if result.get("learning_program"):
        active_thread()["learning_program"] = result["learning_program"]
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
        "start": "뜨개질을 처음 시작하는 사람에게 필요한 것부터 차분히 안내해줘. ",
        "continue": "이전에 배운 내용과 현재 어려운 점을 확인하고 다음 연습을 안내해줘. ",
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
        journey=st.session_state.selected_journey,
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
                learning_program=active_thread().get("learning_program") or None,
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

    journey = JourneyType(st.session_state.selected_journey)
    definition = JOURNEY_DEFINITIONS[journey]
    context = st.session_state.composer_context
    placeholder = definition.placeholder
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
    st.markdown(ui.tag(_CARD_LABELS.get(card["type"], "작업")), unsafe_allow_html=True)
    st.markdown(f"## {card['title']}")
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
        _list_section("보이는 제작 구조", payload.get("construction", []))
        _list_section("원인 후보", payload.get("diagnoses", []))
        _list_section("먼저 고쳐볼 것", payload.get("fixes", []))
        _list_section("사진 한 장으로 확정할 수 없는 부분", payload.get("uncertainties", []))
        _list_section("판단에 필요한 추가 사진", payload.get("additional_photos", []))
        if payload.get("model_note"):
            st.caption(payload["model_note"])
        st.button(
            "이 부분을 다시 설명해줘",
            key=f"explain_{card['id']}",
            on_click=_use_card_context,
            args=(f"'{card['title']}' 진단 내용을 더 쉽게 설명해줘. ",),
            use_container_width=True,
        )
    elif card["type"] == "tools":
        _list_section("추천 도구", payload.get("tools", []))
        _list_section("실 선택 메모", payload.get("materials", []))
        _list_section("함께 준비할 부자재", payload.get("accessories", []))
        st.button(
            "도구 보관함에서 비교하기",
            key=f"compare_tools_{card['id']}",
            on_click=_open_tool_library,
            use_container_width=True,
            type="primary",
        )
    elif card["type"] == "technique":
        _list_section("함께 본 기법", payload.get("techniques", []))
        for resource in payload.get("resources", []):
            st.write(resource.get("description", ""))
            _list_section("핵심 순서", resource.get("steps", []))
            cards = resource.get("reference_cards", [])[:3]
            if cards:
                st.markdown("#### 핵심 장면")
                for column, reference in zip(st.columns(len(cards), gap="small"), cards):
                    with column:
                        image_path = _BASE_DIR / reference["path"]
                        if image_path.exists():
                            st.image(str(image_path), use_container_width=True)
                        st.caption(reference["title"])
            _list_section("자주 틀리는 부분", resource.get("common_mistakes", []))
            videos = resource.get("reference_videos", [])
            if videos:
                st.link_button("기초 영상으로 동작 확인 ↗", videos[0]["url"], use_container_width=True)
            if resource.get("success_check"):
                st.info(resource["success_check"])
        st.button(
            "기법 보관함에서 전체 보기",
            key=f"practice_tech_{card['id']}",
            on_click=_open_technique_library,
            use_container_width=True,
        )
    elif card["type"] == "purchase_kit":
        _render_purchase_kit(card)
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


@st.dialog("상세 자료", width="large", on_dismiss=_close_panel)
def _render_work_drawer(card: dict) -> None:
    st.markdown('<span class="work-detail-marker"></span>', unsafe_allow_html=True)
    _render_detail_panel(card)


def render() -> None:
    initialize_session()
    _render_sidebar()
    if st.session_state.workspace_view == "techniques":
        from views import techniques

        techniques.render(on_ask=_ask_about_technique)
        return
    if st.session_state.workspace_view == "tools":
        from views import tools

        tools.render(on_ask=_ask_about_tool)
        return
    selected = find_work_card(st.session_state.selected_work_card_id)
    has_messages = bool(active_thread()["messages"])

    if not has_messages:
        with st.container(key="empty_stage"):
            left_space, center, right_space = st.columns([.35, 3.3, .35])
            with center:
                _render_welcome_header()
                _render_action_shelf()
                _render_journey_starter()
                _render_journey_flow()
        # Use Streamlit's root-level composer in the empty state too, so it
        # remains fixed and visible on shorter screens.
        _render_composer()
        return

    with st.container(key="conversation_shell"):
        st.markdown(
            '<div class="workspace-heading"><span class="workspace-thread"></span>'
            '<div><strong>공방 선생님과 작업 중</strong><small>현재 작품은 작업대에서 진행하고, 도안·진단 결과는 상세 자료로 열어볼 수 있어요.</small></div></div>',
            unsafe_allow_html=True,
        )
        _render_messages()

    if selected:
        _render_work_drawer(selected)

    # Root-level chat_input stays fixed in both empty and active conversations.
    _render_composer()
