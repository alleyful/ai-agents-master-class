"""Model-assisted conversation routing for the knitting tutor.

The model interprets conversational intent and writes a short direct answer when
appropriate.  Curated pattern data and progress mutations remain deterministic.
"""

from __future__ import annotations

import json
import os
from enum import StrEnum

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from pydantic import BaseModel, ConfigDict, Field

from content.techniques import TECHNIQUE_CATALOG
from content.tools import TOOL_GUIDES
from domain.curricula import CURRICULA, current_curriculum_step
from model_provider import ModelProviderError, run_structured_model, structured_model_available


class ConversationAction(StrEnum):
    GENERAL_QUESTION = "general_question"
    SELECT_PROJECT = "select_project"
    START_PROJECT = "start_project"
    NEED_MATERIALS = "need_materials"
    PREVIEW_PROJECT = "preview_project"
    SHOW_OVERVIEW = "show_overview"
    EXPLAIN_CURRENT_STEP = "explain_current_step"
    ADVANCE_STEP = "advance_step"
    COMPLETE_STEP = "complete_step"
    RESTART_PROJECT = "restart_project"
    TECHNIQUE_QUESTION = "technique_question"
    TOOL_QUESTION = "tool_question"
    DIAGNOSE_PROJECT = "diagnose_project"
    EXPLAIN_PATTERN = "explain_pattern"
    OUT_OF_SCOPE = "out_of_scope"
    OTHER_KNITTING = "other_knitting"


class SupportModule(StrEnum):
    """Authored service modules the model may request for this turn."""

    DIRECT_ANSWER = "direct_answer"
    TECHNIQUE_LIBRARY = "technique_library"
    TOOL_LIBRARY = "tool_library"
    CURATED_PROJECT = "curated_project"
    PROJECT_OVERVIEW = "project_overview"
    PROJECT_STEP = "project_step"
    PATTERN_GUIDE = "pattern_guide"
    DIAGNOSIS = "diagnosis"


class ConversationDecision(BaseModel):
    """Small, inspectable contract used before the deterministic graph workers."""

    model_config = ConfigDict(extra="forbid")

    action: ConversationAction
    curriculum_id: str
    suggested_curriculum_ids: list[str]
    support_modules: list[SupportModule]
    technique_names: list[str]
    tool_slugs: list[str]
    assistant_reply: str
    follow_up_question: str
    reasoning_summary: str = Field(description="한 문장으로 적는 분류 근거. 숨겨진 추론 과정은 포함하지 않음.")


def _message_role(message: BaseMessage) -> str:
    return "user" if isinstance(message, HumanMessage) else "assistant" if isinstance(message, AIMessage) else "system"


def _conversation_excerpt(messages: list[BaseMessage]) -> list[dict[str, str]]:
    excerpt: list[dict[str, str]] = []
    for message in messages[-8:]:
        content = message.content if isinstance(message.content, str) else str(message.content)
        excerpt.append({"role": _message_role(message), "content": content[:1200]})
    return excerpt


def _program_context(program: dict) -> dict:
    if not program or program.get("curriculum_id") not in CURRICULA:
        return {}
    curriculum = CURRICULA[program["curriculum_id"]]
    step = current_curriculum_step(program)
    return {
        "curriculum_id": curriculum.id,
        "title": curriculum.title,
        "status": program.get("status", ""),
        "current_step_index": program.get("current_step", 0),
        "current_step_title": step.title if step else "",
        "completed_steps": program.get("completed_steps", []),
        "total_steps": len(curriculum.steps),
    }


def route_conversation_with_model(state: dict) -> ConversationDecision | None:
    """Ask the configured model to interpret the current turn in context.

    A provider failure returns ``None`` so the explicit offline rules remain a
    safe fallback instead of breaking the whole Streamlit session.
    """
    if not structured_model_available():
        return None

    project_catalog = [
        {
            "id": curriculum.id,
            "title": curriculum.title,
            "tool_type": curriculum.tool_type,
            "outcome": curriculum.outcome,
        }
        for curriculum in CURRICULA.values()
    ]
    technique_catalog = [
        {
            "name": name,
            "tool_type": content.get("tool_type", ""),
            "description": content.get("description", "")[:180],
        }
        for name, content in TECHNIQUE_CATALOG.items()
    ]
    tool_catalog = [
        {
            "slug": tool.slug,
            "name": tool.name,
            "craft": tool.craft,
            "summary": tool.summary[:180],
        }
        for tool in TOOL_GUIDES
    ]
    prompt = f"""
당신은 한국어 뜨개 전문 코칭 서비스의 대화 라우터입니다.
사용자의 마지막 말만 키워드로 보지 말고, 최근 대화와 현재 작품 상태를 함께 해석하세요.

서비스의 목표:
- 사용자가 뜨개를 이해하는 데서 끝나지 않고 실제로 시작하고, 현재 동작을 확인하고, 완성까지 이어가게 돕습니다.
- 답을 먼저 주고, 도움이 되는 경우에만 서비스의 기법 보관함·도구 보관함·검수 작품·도안 안내를 연결합니다.
- 구조화 자료를 무조건 붙이지 마세요. 질문 해결에 실제로 도움이 되는 최소 모듈만 support_modules에 고르세요.
- 현재 작품과 관련 없는 일반 질문에는 전체 도안이나 현재 단계 카드를 다시 열지 마세요.

반드시 지킬 분류 원칙:
- 일반적인 뜨개 질문(예: '뜨개질이 뭐야?')은 general_question이며 질문에 바로 답하세요.
- 검수된 작품을 만들고 싶다는 말은 select_project입니다. 정확히 대응할 때만 catalog의 curriculum_id를 고르세요.
- 작품의 전체 도안·전체 순서를 보고 싶으면 show_overview입니다.
- '1단계부터', '현재 단 설명', '여기부터 자세히'는 진도를 이동하지 않는 explain_current_step입니다.
- '다음 단계', '계속해줘'가 현재 작품 진행을 뜻하면 advance_step입니다.
- 실제 완료를 보고하면 complete_step입니다.
- '처음부터'는 restart_project입니다.
- 준비물이 갖춰졌다는 말은 start_project, 도구 없이 먼저 보려는 말은 preview_project입니다.
- 현재 작품의 준비물이 없거나 구매 안내가 필요하면 need_materials입니다.
- 현재 작품과 무관한 기법/도구 질문은 technique_question/tool_question이며 진도를 바꾸지 마세요.
- 뜨개와 무관한 질문만 out_of_scope입니다. 짧은 후속 표현도 최근 문맥상 뜨개이면 거절하지 마세요.
- 기법 질문에는 technique_library, 도구 질문에는 tool_library를 질문 해결에 도움이 될 때 선택하고, catalog의 정확한 name/slug만 반환하세요.
- 완성 목표가 검수 작품과 정확히 맞으면 curated_project를 선택하세요. 단순히 관련 단어가 있다는 이유로 작품 과정을 강제하지 마세요.
- 작품 추천이나 비교를 요청하면 curated_project와 suggested_curriculum_ids를 사용해 catalog에서 최대 3개를 고르세요. 아직 하나를 고르지 않았으므로 select_project로 분류하지 마세요.
- assistant_reply는 general_question, technique_question, tool_question, other_knitting일 때 먼저 읽을 수 있는 자연스럽고 정확한 한국어 답변을 1~3문단으로 작성하세요.
- assistant_reply는 질문에 답하지 않은 채 조건만 되묻거나 서비스 메뉴를 나열해서는 안 됩니다.
- 사용자가 실제로 다음 행동을 정해야 할 때만 follow_up_question을 한 문장으로 작성하세요.
- 검수된 작품의 코 수, 단 수, 도안을 새로 만들지 마세요. 작품 진행 action에서는 assistant_reply를 비워도 됩니다.
- curriculum_id는 catalog에 있는 정확한 id만 쓰거나 빈 문자열로 두세요.
- technique_names와 tool_slugs는 아래 catalog에 있는 정확한 값만 쓰고, 필요 없으면 빈 배열로 두세요.

현재 작품 상태:
{json.dumps(_program_context(state.get('learning_program', {})), ensure_ascii=False)}

검수된 작품 catalog:
{json.dumps(project_catalog, ensure_ascii=False)}

기법 보관함 catalog:
{json.dumps(technique_catalog, ensure_ascii=False)}

도구 보관함 catalog:
{json.dumps(tool_catalog, ensure_ascii=False)}

최근 대화:
{json.dumps(_conversation_excerpt(state.get('messages', [])), ensure_ascii=False)}
""".strip()
    model_name = os.getenv("KNITCOACH_ROUTER_MODEL") or os.getenv("KNITTING_AGENT_MODEL", "gpt-4.1-mini")
    try:
        decision = run_structured_model(prompt, ConversationDecision, model_name=model_name)
    except ModelProviderError:
        return None
    if decision.curriculum_id and decision.curriculum_id not in CURRICULA:
        decision = decision.model_copy(update={"curriculum_id": ""})
    valid_techniques = [name for name in decision.technique_names if name in TECHNIQUE_CATALOG]
    valid_tool_slugs = {tool.slug for tool in TOOL_GUIDES}
    return decision.model_copy(update={
        "technique_names": valid_techniques,
        "tool_slugs": [slug for slug in decision.tool_slugs if slug in valid_tool_slugs],
        "suggested_curriculum_ids": [
            curriculum_id
            for curriculum_id in decision.suggested_curriculum_ids[:3]
            if curriculum_id in CURRICULA
        ],
    })
