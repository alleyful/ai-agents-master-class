"""Shared helpers for KnitCoach pages (agent access, session, temp files)."""

import tempfile
import time
import uuid
from pathlib import Path

import streamlit as st

from knitcoach import create_knitcoach


@st.cache_resource
def get_agent():
    """Build the compiled KnitCoach graph once per server process."""
    return create_knitcoach()


def initialize_session() -> None:
    """Ensure the per-user session and in-session conversation workspace exist."""
    if "threads" not in st.session_state:
        first = _new_thread_data()
        st.session_state.threads = {first["id"]: first}
        st.session_state.active_thread_id = first["id"]
    elif st.session_state.get("active_thread_id") not in st.session_state.threads:
        first = _new_thread_data()
        st.session_state.threads[first["id"]] = first
        st.session_state.active_thread_id = first["id"]

    st.session_state.thread_id = st.session_state.active_thread_id
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("pattern_result", None)
    st.session_state.setdefault("selected_work_card_id", None)
    st.session_state.setdefault("composer_mode", "chat")
    st.session_state.setdefault("composer_context", "")
    st.session_state.setdefault("workspace_view", "chat")
    st.session_state.setdefault("selected_journey", "start_from_zero")


def _new_thread_data() -> dict:
    now = time.time()
    thread_id = uuid.uuid4().hex
    return {
        "id": thread_id,
        "title": "새 뜨개 대화",
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "work_cards": [],
        "learning_program": {},
    }


def create_thread() -> str:
    """Create and activate a new in-session conversation."""
    initialize_session()
    thread = _new_thread_data()
    st.session_state.threads[thread["id"]] = thread
    st.session_state.active_thread_id = thread["id"]
    st.session_state.thread_id = thread["id"]
    st.session_state.selected_work_card_id = None
    st.session_state.composer_mode = "chat"
    st.session_state.composer_context = ""
    st.session_state.workspace_view = "chat"
    st.session_state.selected_journey = "start_from_zero"
    return thread["id"]


def activate_thread(thread_id: str) -> None:
    """Switch the workspace to an existing conversation."""
    initialize_session()
    if thread_id not in st.session_state.threads:
        return
    st.session_state.active_thread_id = thread_id
    st.session_state.thread_id = thread_id
    st.session_state.selected_work_card_id = None
    st.session_state.composer_mode = "chat"
    st.session_state.composer_context = ""
    st.session_state.workspace_view = "chat"
    st.session_state.selected_journey = "start_from_zero"


def active_thread() -> dict:
    initialize_session()
    return st.session_state.threads[st.session_state.active_thread_id]


def recent_threads() -> list[dict]:
    """Return non-empty conversations in most-recently-used order."""
    initialize_session()
    threads = [thread for thread in st.session_state.threads.values() if thread["messages"]]
    return sorted(threads, key=lambda thread: thread["updated_at"], reverse=True)


def append_message(role: str, content: str, **metadata) -> str:
    """Append a display message to the active conversation."""
    thread = active_thread()
    message_id = uuid.uuid4().hex
    message = {"id": message_id, "role": role, "content": content, **metadata}
    thread["messages"].append(message)
    thread["updated_at"] = time.time()
    if role == "user" and thread["title"] == "새 뜨개 대화":
        clean = " ".join(content.replace("#", "").split())
        thread["title"] = clean[:26] + ("…" if len(clean) > 26 else "")
    return message_id


def attach_work_cards(result: dict, source_message_id: str) -> list[str]:
    """Derive compact, inspectable work cards from one graph result."""
    thread = active_thread()
    cards: list[dict] = []

    if result.get("project_suggestions"):
        cards.append(_work_card(
            "project_gallery",
            "처음 완성하기 좋은 작품",
            "완성 사진을 보고 마음에 드는 작품을 고르세요. 선택 후 준비물부터 함께 확인합니다.",
            {"curriculum_ids": result["project_suggestions"]},
            source_message_id,
        ))

    if result.get("purchase_plan"):
        plan = result["purchase_plan"]
        cards.append(_work_card(
            "purchase_kit",
            f"{plan['title']} 첫 구매 목록",
            "도구 사진, 정확한 규격, 구매처와 작품 미리보기를 한곳에 모았어요.",
            plan,
            source_message_id,
        ))

    if result.get("pattern_draft"):
        draft = result["pattern_draft"]
        cards.append(_work_card(
            "pattern",
            draft.get("title", "도안 초안"),
            draft.get("summary", "준비물과 제작 순서를 정리했어요."),
            draft,
            source_message_id,
        ))
    elif result.get("photo_findings") or result.get("recommended_fixes"):
        observation = result.get("image_observation", {})
        cards.append(_work_card(
            "diagnosis",
            "작품 문제 진단",
            (result.get("recommended_fixes") or result.get("photo_findings") or ["확인 내용을 정리했어요."])[0],
            {
                "findings": result.get("photo_findings", []),
                "diagnoses": result.get("mistake_diagnoses", []),
                "fixes": result.get("recommended_fixes", []),
                "confidence": result.get("difficulty_level", "unknown"),
                "construction": observation.get("construction", []),
                "uncertainties": observation.get("uncertainties", []),
                "additional_photos": observation.get("additional_photos", []),
                "model_provider": result.get("model_provider", "rules"),
                "model_note": result.get("model_note", ""),
            },
            source_message_id,
        ))

    if (
        result.get("detected_techniques")
        and result.get("intent") == "learn_technique"
        and not result.get("program_turn")
    ):
        names = result["detected_techniques"]
        if result.get("learning_program"):
            already_introduced = {
                technique
                for existing_card in thread["work_cards"]
                if existing_card["type"] == "technique"
                for technique in existing_card["payload"].get("techniques", [])
            }
            names = [name for name in names if name not in already_introduced]
    else:
        names = []

    if names:
        cards.append(_work_card(
            "technique",
            names[0].split("(")[0].strip() if len(names) == 1 else f"기법 {len(names)}가지",
            "핵심 동작, 자주 틀리는 부분과 복습 자료를 모았어요.",
            {
                "techniques": names,
                "summary": result.get("lesson_summary", ""),
                "resources": result.get("technique_resources", []),
                "check": result.get("understanding_check", ""),
            },
            source_message_id,
        ))

    if (
        result.get("intent") == "advise_tools"
        and result.get("required_tools")
        and not result.get("program_turn")
    ):
        cards.append(_work_card(
            "tools",
            "질문에 맞는 도구 안내",
            result["required_tools"][0],
            {
                "tools": result.get("required_tools", []),
                "materials": result.get("required_materials", []),
                "accessories": result.get("accessories", []),
                "tool_slugs": result.get("selected_tool_slugs", []),
            },
            source_message_id,
        ))

    program = result.get("learning_program", {})
    if (
        result.get("program_turn")
        and program.get("status") in {"active", "preview"}
        and result.get("input_type") != "tool_question"
        and result.get("project_view", "step") != "none"
    ):
        cards.append(_work_card(
            "learning_step",
            "현재 단계 완료하기",
            "완료하면 진도를 저장하고 다음 단으로 이동합니다.",
            {
                "learning_program": program,
                "view_mode": result.get("project_view", "step"),
                "conversation_action": result.get("conversation_action", ""),
            },
            source_message_id,
        ))

    if result.get("practice_plan"):
        cards.append(_work_card(
            "practice",
            "다음 연습",
            result["practice_plan"],
            {
                "plan": result["practice_plan"],
                "check": result.get("understanding_check", ""),
                "next_action": result.get("next_action", ""),
            },
            source_message_id,
        ))

    thread["work_cards"].extend(cards)
    return [card["id"] for card in cards]


def _work_card(card_type: str, title: str, summary: str, payload: dict, source_message_id: str) -> dict:
    return {
        "id": uuid.uuid4().hex,
        "type": card_type,
        "title": title,
        "summary": summary,
        "payload": payload,
        "source_message_id": source_message_id,
        "status": "ready",
    }


def find_work_card(card_id: str | None) -> dict | None:
    if not card_id:
        return None
    for thread in st.session_state.get("threads", {}).values():
        for card in thread["work_cards"]:
            if card["id"] == card_id:
                return card
    return None


def temporary_image(image_bytes: bytes, suffix: str) -> Path:
    """Persist uploaded image bytes to a temp file and return its path."""
    file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    file.write(image_bytes)
    file.close()
    return Path(file.name)


def debug_metadata(result: dict) -> dict:
    """Extract the developer-facing metadata shown in debug expanders."""
    return {
        "active_agent": result.get("active_agent"),
        "journey": result.get("journey"),
        "intent": result.get("intent"),
        "tool_type": result.get("tool_type"),
        "pattern_type": result.get("pattern_type"),
        "difficulty": result.get("difficulty_level"),
        "techniques": result.get("detected_techniques"),
        "tool_findings": result.get("tool_findings"),
        "project_suggestions": result.get("project_suggestions"),
        "learning_program": result.get("learning_program"),
        "conversation_action": result.get("conversation_action"),
        "support_modules": result.get("support_modules", []),
        "selected_tool_slugs": result.get("selected_tool_slugs", []),
        "suggested_curriculum_ids": result.get("suggested_curriculum_ids", []),
        "model_routed": result.get("model_routed"),
        "project_view": result.get("project_view"),
    }
