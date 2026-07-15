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
        cards.append(_work_card(
            "diagnosis",
            "작품 문제 진단",
            (result.get("recommended_fixes") or result.get("photo_findings") or ["확인 내용을 정리했어요."])[0],
            {
                "findings": result.get("photo_findings", []),
                "diagnoses": result.get("mistake_diagnoses", []),
                "fixes": result.get("recommended_fixes", []),
                "confidence": result.get("difficulty_level", "unknown"),
            },
            source_message_id,
        ))

    if result.get("detected_techniques") and result.get("intent") == "learn_technique":
        names = result["detected_techniques"]
        cards.append(_work_card(
            "technique",
            names[0].split("(")[0].strip() if len(names) == 1 else f"기법 {len(names)}가지",
            result.get("lesson_summary") or "단계와 주의할 점을 정리했어요.",
            {
                "techniques": names,
                "summary": result.get("lesson_summary", ""),
                "resources": result.get("technique_resources", []),
                "check": result.get("understanding_check", ""),
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
        "intent": result.get("intent"),
        "tool_type": result.get("tool_type"),
        "pattern_type": result.get("pattern_type"),
        "difficulty": result.get("difficulty_level"),
        "techniques": result.get("detected_techniques"),
        "tool_findings": result.get("tool_findings"),
    }
