"""Reusable LangGraph core for the KnitCoach Streamlit application."""


import operator
import os
import re
import uuid
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Overwrite, Send
from pydantic import BaseModel, ConfigDict, Field

from content.techniques import TECHNIQUE_CATALOG, TECHNIQUES, resolve_techniques
from content.tools import get_tool, recommend_tools, resolve_tools
from domain.curricula import (
    CURRICULA,
    activate_learning_program,
    advance_learning_program,
    beginner_project_ids,
    current_curriculum_step,
    detect_curriculum,
    new_learning_program,
    mark_learning_program_shopping,
    preview_learning_program,
    restart_learning_program,
)
from content.purchases import build_purchase_plan
from conversation_router import ConversationAction, SupportModule, route_conversation_with_model
from domain.journeys import infer_journey
from domain.models import JourneyType
from model_provider import (
    ModelProviderError,
    active_provider_name,
    run_structured_model,
    structured_model_available,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = os.getenv("KNITTING_AGENT_MODEL", "gpt-4.1-mini")
HAS_OPENAI_KEY = bool(os.getenv("OPENAI_API_KEY"))
ENABLE_VISION = os.getenv("KNITCOACH_ENABLE_VISION") == "1"
DEBUG_MODE = os.getenv("KNITCOACH_DEBUG") == "1"
class PatternRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_type: Literal["auto", "crochet", "needle_knitting"] = "auto"
    finished_size: str = Field(min_length=1)
    yarn_weight: str = Field(min_length=1)
    tool_size: str = Field(min_length=1)
    gauge: str = "미측정"
    skill_level: Literal["beginner", "confident_beginner", "intermediate"] = "beginner"
    notes: str = ""


class PatternDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    summary: str
    tool_type: Literal["crochet", "needle_knitting", "unknown"]
    confidence: Literal["low", "medium", "high"]
    techniques: list[str]
    materials: list[str]
    gauge_guidance: str
    construction: list[str]
    instructions: list[str]
    finishing: list[str]
    assumptions: list[str]
    additional_photos: list[str]


class ImageObservation(BaseModel):
    """Facts that a model actually observed in one uploaded knitting image."""

    model_config = ConfigDict(extra="forbid")

    summary: str
    tool_type: Literal["crochet", "needle_knitting", "unknown"]
    project_type: str
    confidence: Literal["low", "medium", "high"]
    visible_facts: list[str]
    likely_techniques: list[str]
    construction: list[str]
    diagnoses: list[str]
    suggested_actions: list[str]
    uncertainties: list[str]
    additional_photos: list[str]


class KnitCoachState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    out_of_scope: bool
    guardrail_reason: str
    journey: JourneyType
    learner_profile: dict
    input_type: Literal["text", "image_path", "pattern_text", "explanation_text", "link", "feedback", "tool_question"]
    intent: Literal["analyze_artifact", "generate_pattern", "convert_pattern", "learn_technique", "advise_tools", "revise_output"]
    task: Literal["tutor", "generate_pattern"]
    pattern_options: dict
    pattern_draft: dict
    original_image_name: str
    user_response: str
    artifact_source: str
    uploaded_image_path: str
    image_observation: dict
    model_provider: str
    model_note: str
    artifact_analysis: str
    tool_type: Literal["crochet", "needle_knitting", "unknown"]
    pattern_type: Literal["photo", "finished_object", "written_pattern", "symbol_chart", "diagram_chart", "unknown"]
    detected_project_type: str
    construction_parts: list[str]
    pattern_reference_note: str
    detected_techniques: list[str]
    difficulty_level: Literal["beginner", "confident_beginner", "intermediate", "advanced", "unknown"]
    difficulty_reasons: list[str]
    photo_findings: list[str]
    mistake_diagnoses: list[str]
    recommended_fixes: list[str]
    required_tools: list[str]
    required_materials: list[str]
    accessories: list[str]
    technique_resources: Annotated[list[dict], operator.add]
    tool_findings: str
    active_agent: str
    conversion_mode: Literal["pattern_to_explanation", "explanation_to_pattern", "explanation_to_chart", "tutor_only"]
    generated_explanation: str
    generated_pattern: str
    chart_spec: dict
    chart_image_path: str
    user_feedback: str
    goal: str
    current_skill: str
    blockers: list[str]
    learning_path: Literal["crochet_beginner", "needle_knitting_beginner", "diagnose_tool"]
    curriculum_stage: str
    lesson_summary: str
    practice_plan: str
    understanding_check: str
    next_action: str
    learning_program: dict
    program_turn: bool
    project_suggestions: list[str]
    purchase_plan: dict
    conversation_action: str
    support_modules: list[str]
    selected_tool_slugs: list[str]
    suggested_curriculum_ids: list[str]
    model_reply: str
    model_follow_up: str
    model_routed: bool
    project_view: Literal["none", "overview", "step"]


CROCHET_KEYWORDS = {
    "코바늘", "crochet", "사슬", "사슬뜨기", "짧은뜨기", "긴뜨기", "빼뜨기", "모티브", "원형뜨기", "컵받침",
    "코스터", "키링", "열쇠고리", "매직링", "magic ring", "한길긴뜨기", "네트", "망사", "mesh", "shoulder-bag", "ch", "sc", "dc", "sl st", "mr", "amigurumi", "아미구루미"
}
NEEDLE_KEYWORDS = {
    "대바늘", "knit", "knitting", "겉뜨기", "안뜨기", "메리야스", "고무뜨기", "코잡기", "코 잡기", "목도리", "k2tog", "yo", "purl", "stockinette", "ribbing"
}
for _technique in TECHNIQUES:
    _keywords = {_technique.name.split("(")[0], *_technique.aliases}
    if _technique.tool_type == "crochet":
        CROCHET_KEYWORDS.update(_keywords)
    else:
        NEEDLE_KEYWORDS.update(_keywords)
# 단어 경계 기반으로만 판정하는 뜨개 약어/단 표기 (부분문자열 오탐 방지: "chart"의 "ch", "코바늘"의 "코" 등)
_PATTERN_TERMS = sorted(
    {
        technique.abbreviation.casefold()
        for technique in TECHNIQUES
        if re.fullmatch(r"[A-Za-z0-9 /×-]{2,}", technique.abbreviation)
        and technique.abbreviation.casefold() not in {"slip knot"}
    },
    key=len,
    reverse=True,
)
PATTERN_ABBREV_RE = re.compile(
    r"(?<![a-z0-9])(?:" + "|".join(re.escape(term) for term in _PATTERN_TERMS) + r")(?![a-z0-9])|\d+\s*단(?![색계])",
    re.IGNORECASE,
)
# 안전한(명확한) 다중 문자 pattern 신호만 유지. 단일 문자("코", "단", "k", "p")는 오탐이 커서 제거.
PATTERN_KEYWORDS = {"repeat from", "rep from", "반복하세요", "되풀이하세요"}
LEARNING_REQUEST_WORDS = {"알려줘", "가르쳐", "배우고", "배울래", "뜨는 법", "뜨는법", "어떻게 떠", "연습하고"}
# "바늘", "실"은 "코바늘"/"실수" 등에 부분 매칭되어 오탐이 크므로 tool_question 키워드에서 제외.
TOOL_QUESTION_KEYWORDS = {"호수", "부자재", "굵기", "제품", "추천", "몇 호", "몇호", "재료", "줄바늘", "장갑바늘", "숏팁", "롱팁", "아후강", "튀니지안", "표시링", "돗바늘", "다이소", "니트프로", "튤립"}
BLOCKER_KEYWORDS = {
    "늘어나": "코가 늘어남",
    "빠져": "코가 빠짐",
    "구멍": "의도하지 않은 구멍",
    "조여": "장력이 너무 조임",
    "헐거": "장력이 너무 헐거움",
    "말려": "편물이 말림",
    "휘어": "가장자리 휘어짐",
    "단 수": "단 수가 맞지 않음",
    "어려": "기술 이해가 어려움",
}

CROCHET_CURRICULUM = {
    "사슬뜨기": "1. 사슬뜨기로 일정한 foundation 만들기",
    "짧은뜨기": "2. 짧은뜨기로 작은 사각형 만들기",
    "긴뜨기": "3. 긴뜨기로 높이와 장력 비교하기",
    "한길긴뜨기": "3-1. 한길긴뜨기를 두 번에 나누어 빼기",
    "매직링": "4. 매직링으로 중심 구멍을 조절하기",
    "원형뜨기": "5. 매직링으로 원형을 시작하고 늘림 위치 익히기",
}
NEEDLE_CURRICULUM = {
    "코 잡기": "1. 코를 일정한 간격으로 잡기",
    "겉뜨기": "2. 겉뜨기로 garter stitch 만들기",
    "안뜨기": "3. 안뜨기와 겉뜨기 방향 구분하기",
    "고무뜨기": "4. 겉뜨기 1코/안뜨기 1코 반복으로 1×1 고무뜨기 만들기",
    "게이지": "5. 게이지를 재고 바늘 크기 조정하기",
}

SAMPLE_PROJECT_REFERENCES = {
    "crochet-mesh-shoulder-bag": {
        "project_type": "가방/bag",
        "tool_type": "crochet",
        "construction_parts": ["가방바닥", "가방몸통", "손잡이", "크로스끈"],
        "techniques": [
            "사슬뜨기(chain stitch)",
            "빼뜨기(slip stitch)",
            "한길긴뜨기(double crochet)",
            "매직링으로 원형 시작하기(crocheting in the round)",
        ],
        "difficulty_level": "intermediate",
        "difficulty_reasons": [
            "구멍 패턴 반복 위치를 일정하게 맞춰야 합니다.",
            "가방 바닥 단수를 늘리면 전체 크기와 몸통 연결 위치가 달라집니다.",
            "손잡이와 크로스끈 연결부 마감이 필요합니다.",
        ],
        "pattern_reference_note": (
            "도안 reference는 가방바닥 3단까지만 보이는 기준입니다. "
            "샘플 완성품 크기는 바닥을 6-7단 정도까지 확장한 응용으로 추정합니다."
        ),
        "photo_findings": [
            "완성품은 코바늘 네트/레이스 숄더백으로 보이며, 몸통 전체에 반복 구멍 무늬가 있습니다.",
            "도안 reference는 가방바닥, 가방몸통, 손잡이, 크로스끈을 나누어 보여줍니다.",
            "손잡이는 사슬뜨기 40코를 만든 뒤 크로스끈과 연결하는 구조로 읽힙니다.",
        ],
        "mistake_diagnoses": [
            "초보자는 몸통 반복 무늬에서 사슬 공간을 건너뛰는 위치를 헷갈릴 수 있습니다.",
            "바닥 단수를 3단에서 6-7단으로 늘리면 모서리 늘림 위치와 몸통 시작 위치를 다시 맞춰야 합니다.",
        ],
        "recommended_fixes": [
            "바닥을 확장할 때는 각 단의 모서리 늘림 위치에 마커를 걸어 6-7단까지 같은 규칙으로 키웁니다.",
            "몸통은 한 반복 단위를 먼저 표시하고, 사슬 공간과 한길긴뜨기 묶음 위치를 반복마다 확인합니다.",
            "손잡이 사슬 40코는 양쪽 길이를 맞춘 뒤 빼뜨기 또는 돗바늘 마감으로 연결부를 보강합니다.",
        ],
        "custom_project_video_prompt": (
            "코바늘 네트 숄더백 도안을 기준으로 바닥 3단에서 6-7단까지 확장하는 방법, "
            "몸통 반복 구멍무늬를 읽는 방법, 손잡이 사슬 40코와 크로스끈 연결부를 "
            "클로즈업으로 단계별 설명하는 20초 튜토리얼 영상"
        ),
    }
}


def get_sample_reference(text: str) -> dict:
    lowered = normalize_text(text)
    if "crochet-mesh-shoulder-bag" in lowered or ("가방" in text and "도안" in text and any(word in text for word in ["6-7단", "6~7단", "바닥", "손잡이"])):
        return SAMPLE_PROJECT_REFERENCES["crochet-mesh-shoulder-bag"]
    return {}


def merge_unique(base: list[str], additions: list[str]) -> list[str]:
    return list(dict.fromkeys([*base, *additions]))


def beginner_explanation_from_pattern(text: str) -> str:
    lowered = normalize_text(text)
    chain_count = None
    row_count = None
    ch_match = re.search(r"ch\s*(\d+)", lowered)
    if ch_match:
        chain_count = int(ch_match.group(1))
    # 숫자가 마커 앞("5 rows")이든 뒤("rows 5")이든 잡는다.
    row_match = re.search(r"(\d+)\s*rows?\b", lowered) or re.search(r"\brows?\s*(\d+)", lowered)
    if row_match:
        row_count = int(row_match.group(1))
    steps = []
    if chain_count is not None:
        steps.append(f"사슬뜨기 {chain_count}코를 만들어 시작합니다.")
    if re.search(r"(?<![a-z0-9])sc(?![a-z0-9])", lowered):
        steps.append("sc는 짧은뜨기입니다. 지시된 각 코에 짧은뜨기를 1번씩 뜹니다.")
    if re.search(r"(?<![a-z0-9])dc(?![a-z0-9])", lowered):
        steps.append("dc는 한길긴뜨기입니다. 실을 한 번 감고 두 고리씩 두 번에 나누어 빼냅니다.")
    if "across" in lowered:
        steps.append("across는 현재 단의 끝까지 같은 동작을 반복하라는 뜻입니다.")
    if row_count is not None:
        steps.append(f"입력에 적힌 총 {row_count}단까지 같은 규칙을 이어갑니다.")
    else:
        steps.append("반복할 단 수는 입력에 없으므로 다음 줄의 지시나 원본 도안을 확인해야 합니다.")
    steps.append("첫 코와 마지막 코를 빠뜨리지 않았는지 단 끝에서 코 수를 확인합니다.")
    numbered = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    return f"초보자 설명:\n{numbered}"


def row_by_row_pattern_from_text(text: str) -> str:
    lowered = normalize_text(text)
    chain_match = re.search(r"(?:사슬|ch)\s*(\d+)", lowered)
    row_match = re.search(r"(\d+)\s*단", lowered) or re.search(r"(\d+)\s*rows?", lowered)
    if not chain_match or not row_match:
        return "시작 코 수와 반복 단 수가 입력에 없어 확정 도안을 만들 수 없습니다. 원하는 크기와 게이지를 알려주세요."
    chain_count = int(chain_match.group(1))
    row_count = int(row_match.group(1))
    return (
        f"시작: 사슬 {chain_count}코.\n"
        f"1–{row_count}단: 각 코에 짧은뜨기 1코.\n"
        "단을 시작하는 기둥코와 마무리 방법은 입력에 없으므로 원본 조건을 확인해야 합니다."
    )

def latest_user_text(state: KnitCoachState) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def current_turn_messages(state: KnitCoachState) -> list[BaseMessage]:
    """Return messages created since the most recent user turn."""
    messages = list(state["messages"])
    for index in range(len(messages) - 1, -1, -1):
        if isinstance(messages[index], HumanMessage):
            return messages[index:]
    return messages


def normalize_text(text: str) -> str:
    return text.lower().replace("_", "-")


def has_pattern_abbrev(text: str) -> bool:
    """단어 경계 기반으로 실제 뜨개 약어/단 표기가 있는지 확인 (부분문자열 오탐 방지)."""
    return bool(PATTERN_ABBREV_RE.search(normalize_text(text)))


def keyword_hit(text_lower: str, keyword: str) -> bool:
    """짧은 영문 약어(ch, sc, dc, mr, yo 등)는 단어 경계로, 그 외(한글/긴 영단어)는 부분문자열로 매칭.

    파일명/영단어의 부분문자열(scarf의 sc, stitch의 ch, chart의 ch)로 인한 오탐을 방지한다.
    """
    kw = keyword.lower()
    if re.fullmatch(r"[a-z0-9 -]+", kw) and len(kw) <= 5:
        return re.search(r"\b" + re.escape(kw) + r"\b", text_lower) is not None
    return kw in text_lower


KNITTING_SCOPE_KEYWORDS = {
    "뜨개", "손뜨개", "편물", "코바늘", "대바늘", "줄바늘", "뜨개실", "실 라벨",
    "도안", "기호 도안", "영문 도안", "게이지", "코잡기", "코 잡기", "코막음",
    "짧은뜨기", "긴뜨기", "한길긴뜨기", "사슬뜨기", "빼뜨기", "겉뜨기", "안뜨기",
    "매직링", "늘려뜨기", "모아뜨기", "표시링", "마커", "돗바늘", "바늘 호수",
    "가방", "모자", "인형", "양말", "장갑", "수세미", "목도리", "머플러", "파우치",
    "키링", "티코스터", "컵받침", "아미구루미",
    "뜨고", "뜨는", "떠요", "떠서", "떠보", "뜨다가", "코 수", "단 수", "손땀",
}
PROGRAM_CONTINUATION_PHRASES = {
    "준비됐", "준비 완료", "아무것도 없", "도구가 없", "먼저 보기", "먼저 볼",
    "미리보기", "과정을 먼저", "둘러볼",
    "연습 완료", "단계 완료", "완료했", "다 떴", "끝냈", "마쳤", "다음 단계",
    "다음은", "이어서", "계속", "진행해", "다음으로", "다음단계", "처음부터 설명", "처음부터 알려",
    "처음부터 보여", "첫 단계부터", "여기까지", "이게 맞", "잘 안돼", "다시 설명", "사진으로 볼",
    "현재 단계", "1단계부터", "1단부터", "자세히 시작",
}


def is_pattern_literacy_request(text: str) -> bool:
    """Identify requests to learn how to read notation, not to make a project."""
    lowered = normalize_text(text)
    return any(
        phrase in lowered
        for phrase in (
            "도안을 처음 읽", "도안 읽는 법", "약어를 읽", "약어 설명", "영문 코바늘 약어",
            "영문 대바늘 약어", "기호 도안의", "기호 도안 읽", "반복 구간", "repeat 반복",
        )
    )


def is_knitting_scope(
    text: str,
    *,
    existing_program: dict | None = None,
    has_image: bool = False,
    task: str = "tutor",
) -> bool:
    """Return True only when this turn belongs to the knitting tutor's domain.

    A saved curriculum does not make every later question in-scope. Only explicit
    knitting signals or known progress controls may reuse that curriculum.
    """
    lowered = normalize_text(text).strip()
    if task == "generate_pattern" or has_image:
        return True
    if detect_curriculum(text) or has_pattern_abbrev(lowered):
        return True
    catalog_keywords = {*CROCHET_KEYWORDS, *NEEDLE_KEYWORDS, *KNITTING_SCOPE_KEYWORDS}
    if any(keyword_hit(lowered, keyword) for keyword in catalog_keywords):
        return True
    if existing_program and any(phrase in lowered for phrase in PROGRAM_CONTINUATION_PHRASES):
        return True
    return False


def detect_tool_type(text: str) -> Literal["crochet", "needle_knitting", "unknown"]:
    lowered = normalize_text(text)
    has_crochet = any(keyword_hit(lowered, keyword) for keyword in CROCHET_KEYWORDS)
    has_needle = any(keyword_hit(lowered, keyword) for keyword in NEEDLE_KEYWORDS)
    if has_crochet and not has_needle:
        return "crochet"
    if has_needle and not has_crochet:
        return "needle_knitting"
    return "unknown"


def detect_input_type(text: str) -> Literal["text", "image_path", "pattern_text", "explanation_text", "link", "feedback", "tool_question"]:
    lowered = normalize_text(text)
    if "http://" in lowered or "https://" in lowered:
        return "link"
    if any(ext in lowered for ext in [".png", ".jpg", ".jpeg", ".webp"]):
        return "image_path"
    if any(word in text for word in LEARNING_REQUEST_WORDS):
        return "text"
    explicit_pattern_request = any(
        phrase in text for phrase in ["도안으로 바꿔", "패턴으로 바꿔", "도안으로 만들어", "패턴으로 만들어"]
    )
    if explicit_pattern_request:
        return "explanation_text"
    conversion_request = any(word in text for word in ["도안으로", "도안과", "차트", "chart", "chart spec", "바꿔", "변환"])
    pattern_abbrev = has_pattern_abbrev(lowered)
    # 변환 요청이면서 실제 도안 약어가 없으면 설명글 -> 도안/차트 방향.
    if conversion_request and not pattern_abbrev:
        return "explanation_text"
    # 도안 약어(단어 경계) 또는 명확한 pattern 키워드가 있을 때만 pattern_text.
    if pattern_abbrev or any(keyword in lowered for keyword in PATTERN_KEYWORDS):
        return "pattern_text"
    if any(word in text for word in ["수정", "더 잘", "피드백 반영"]):
        return "feedback"
    if any(word in text for word in TOOL_QUESTION_KEYWORDS):
        return "tool_question"
    return "text"

def detect_intent(text: str, input_type: str) -> Literal["analyze_artifact", "convert_pattern", "learn_technique", "advise_tools", "revise_output"]:
    if input_type == "feedback":
        return "revise_output"
    if input_type == "tool_question":
        return "advise_tools"
    if any(word in text for word in LEARNING_REQUEST_WORDS):
        return "learn_technique"
    if input_type in {"image_path", "link"} or any(
        word in text
        for word in ["분석", "완성품", "사진", "이미지", "난이도", "문제", "막힌", "진단", "왜", "휘어", "말려", "빠져", "늘어나"]
    ):
        return "analyze_artifact"
    if input_type in {"pattern_text", "explanation_text"} or any(word in text for word in ["설명글", "도안으로", "변환", "chart", "차트"]):
        return "convert_pattern"
    return "learn_technique"


def is_tool_definition_question(text: str) -> bool:
    """Distinguish 'what is this tool?' from shopping or project matching."""
    lowered = normalize_text(text)
    definition_phrases = ("뭐야", "뭔가", "무엇", "어떤 도구", "어떻게 생", "설명해", "뜻이")
    return bool(resolve_tools(text)) and any(phrase in lowered for phrase in definition_phrases)


def detect_current_skill(text: str, tool_type: str) -> str:
    catalog_tool = tool_type if tool_type in {"crochet", "needle_knitting"} else None
    matches = resolve_techniques(text, catalog_tool)
    if matches:
        return matches[0].name.split("(")[0]
    if tool_type == "crochet":
        return "사슬뜨기"
    if tool_type == "needle_knitting":
        return "코 잡기"
    return "도구 선택"


def detect_goal(text: str, tool_type: str) -> str:
    lowered = text.lower()
    if "키링" in text or "열쇠고리" in text or "keyring" in lowered or "key ring" in lowered:
        return "키링 만들기"
    if "목도리" in text or "scarf" in lowered:
        return "목도리 만들기"
    if "컵받침" in text or "coaster" in lowered:
        return "컵받침 만들기"
    if "가방" in text or "bag" in lowered or "shoulder-bag" in lowered:
        return "가방 만들기"
    if "인형" in text or "amigurumi" in lowered:
        return "아미구루미 만들기"
    if "비니" in text or "모자" in text or "hat" in lowered:
        return "모자 만들기"
    if tool_type == "crochet":
        return "코바늘 기초 익히기"
    if tool_type == "needle_knitting":
        return "대바늘 기초 익히기"
    return "나에게 맞는 뜨개 도구와 첫 프로젝트 정하기"


def detect_project_type(text: str) -> str:
    lowered = normalize_text(text)
    mapping = {"키링": "키링/keyring", "열쇠고리": "키링/keyring", "keyring": "키링/keyring", "컵받침": "컵받침/coaster", "코스터": "컵받침/coaster", "coaster": "컵받침/coaster", "목도리": "목도리/scarf", "scarf": "목도리/scarf", "가방": "가방/bag", "bag": "가방/bag", "모자": "모자/hat", "hat": "모자/hat", "비니": "모자/hat", "인형": "아미구루미/amigurumi", "amigurumi": "아미구루미/amigurumi", "도안": "도안/pattern", "chart": "차트 도안/chart"}
    for keyword, label in mapping.items():
        if keyword in lowered or keyword in text:
            return label
    return "미확정 프로젝트"


def detect_pattern_type(text: str, input_type: str) -> Literal["photo", "finished_object", "written_pattern", "symbol_chart", "diagram_chart", "unknown"]:
    lowered = normalize_text(text)
    if input_type == "pattern_text":
        return "written_pattern"
    if "chart" in lowered or "차트" in text or "기호" in text:
        return "symbol_chart"
    if "도안" in text and input_type == "image_path":
        return "diagram_chart"
    if input_type == "image_path":
        return "photo"
    if any(word in text for word in ["완성품", "작품"]):
        return "finished_object"
    return "unknown"


def detect_blockers(text: str) -> list[str]:
    return [label for keyword, label in BLOCKER_KEYWORDS.items() if keyword in text]


def detect_techniques(text: str, tool_type: str, current_skill: str) -> list[str]:
    catalog_tool = tool_type if tool_type in {"crochet", "needle_knitting"} else None
    techniques = [technique.name for technique in resolve_techniques(text, catalog_tool)]
    if not techniques and current_skill != "도구 선택":
        catalog_key = next((key for key in TECHNIQUE_CATALOG if current_skill in key), current_skill)
        techniques.append(catalog_key)
    if not techniques and tool_type == "crochet":
        techniques.append("사슬뜨기(chain stitch)")
    if not techniques and tool_type == "needle_knitting":
        techniques.append("롱테일 코잡기(long-tail cast on)")
    return list(dict.fromkeys(techniques))


def infer_tool_type_from_techniques(tool_type: str, techniques: list[str]) -> Literal["crochet", "needle_knitting", "unknown"]:
    if tool_type != "unknown":
        return tool_type
    if any(TECHNIQUE_CATALOG.get(t, {}).get("tool_type") == "crochet" for t in techniques):
        return "crochet"
    if any(TECHNIQUE_CATALOG.get(t, {}).get("tool_type") == "needle_knitting" for t in techniques):
        return "needle_knitting"
    return "unknown"


def infer_difficulty(pattern_type: str, project_type: str, techniques: list[str], blockers: list[str]) -> tuple[str, list[str]]:
    reasons = []
    score = 0
    if pattern_type in {"symbol_chart", "diagram_chart"}:
        score += 1
        reasons.append("도안/차트 해석이 필요합니다.")
    if any("매직링" in t or "긴뜨기" in t or "고무뜨기" in t or "안뜨기" in t for t in techniques):
        score += 1
        reasons.append("기초 다음 단계 기법이 포함되어 있습니다.")
    if any("원형뜨기" in t or "k2tog" in t or "yarn over" in t for t in techniques):
        score += 2
        reasons.append("늘림/줄임 또는 원형 진행 관리가 필요합니다.")
    if any(word in project_type for word in ["가방", "모자", "아미구루미"]):
        score += 1
        reasons.append("형태를 잡거나 부자재를 연결하는 작품입니다.")
    if any("한길긴뜨기" in t for t in techniques):
        score += 1
        reasons.append("사슬 공간과 긴 기둥코 반복을 읽어야 합니다.")
    if blockers:
        reasons.append("현재 막힌 지점이 있어 장력과 코 수 확인이 중요합니다.")
    if score <= 0:
        return "beginner", reasons or ["기초 기법 위주로 시작할 수 있습니다."]
    if score == 1:
        return "confident_beginner", reasons
    if score <= 3:
        return "intermediate", reasons
    return "advanced", reasons


def build_photo_findings(text: str, pattern_type: str, techniques: list[str], blockers: list[str]) -> tuple[list[str], list[str], list[str]]:
    findings = []
    diagnoses = []
    fixes = []
    if pattern_type in {"photo", "finished_object"}:
        findings.append("사진/완성품 입력으로 보고 작품 형태, 가장자리, 코 크기, 단 진행을 확인해야 합니다.")
    if pattern_type in {"symbol_chart", "diagram_chart", "written_pattern"}:
        findings.append("도안 입력으로 보고 반복 구간, row/round 표기, 기호 legend를 먼저 확인해야 합니다.")
    if "장력이 너무 조임" in blockers:
        diagnoses.append("실을 당기는 힘이 강해 코가 작아지고 가장자리가 말릴 수 있습니다.")
        fixes.append("다음 샘플은 바늘 몸통까지 코를 밀어 넣고, 실이 바늘을 편하게 지나갈 정도로만 당깁니다.")
    if "장력이 너무 헐거움" in blockers:
        diagnoses.append("코 크기가 커져 조직이 벌어지고 형태가 흐려질 수 있습니다.")
        fixes.append("실을 손가락에 한 번 더 걸어 일정한 저항을 만들고 같은 속도로 떠 봅니다.")
    if "코가 늘어남" in blockers:
        diagnoses.append("단 시작 코를 한 번 더 뜨거나 마지막 코를 두 번 떠서 코 수가 늘어났을 가능성이 있습니다.")
        fixes.append("단 시작 위치에 작은 표시 고리인 마커를 걸고, 다음 단에서 시작 코를 중복해서 뜨지 않았는지 확인합니다.")
    if "코가 빠짐" in blockers or "의도하지 않은 구멍" in blockers:
        diagnoses.append("중간에 코를 놓쳤거나 실 위치가 앞뒤로 잘못 이동했을 가능성이 있습니다.")
        fixes.append("문제가 생긴 줄 바로 아래 안정된 줄을 찾고, 작은 표시 고리인 마커로 위치를 표시한 뒤 한 코씩 복구합니다.")
    if "편물이 말림" in blockers or "가장자리 휘어짐" in blockers:
        diagnoses.append("단 끝 코 누락, 기둥코 처리, 또는 장력 차이 때문에 가장자리가 틀어질 수 있습니다.")
        fixes.append("각 단 마지막 코를 세고, 단 시작/끝에 작은 표시 고리인 마커를 걸어 빠뜨린 코가 없는지 확인합니다.")
    if any("한길긴뜨기" in t for t in techniques):
        fixes.append("네트 패턴은 사슬 공간과 한길긴뜨기 묶음 위치를 한 반복 단위씩 표시하며 진행합니다.")
    if any("짧은뜨기" in t for t in techniques) and not fixes:
        fixes.append("짧은뜨기는 매 단 끝에서 전체 코 수를 세고 마지막 코 위치를 사진으로 남기면 오류를 빨리 찾을 수 있습니다.")
    if any("매직링" in t for t in techniques):
        fixes.append("매직링은 첫 단을 모두 넣은 뒤 중심 꼬리실을 조이고, 첫 코 위치에 마커를 둡니다.")
    if not findings:
        findings.append("텍스트 설명만으로는 작품의 실제 장력과 코 누락 여부를 확정할 수 없습니다.")
    if not diagnoses:
        diagnoses.append("v1 fallback 분석에서는 사진 자체보다 입력 설명과 파일명에서 가능한 문제를 추론합니다.")
    if not fixes:
        fixes.append("정면 사진 1장과 가장자리/문제 부위 클로즈업 1장을 함께 남기면 다음 분석 정확도가 올라갑니다.")
    return findings, diagnoses, fixes


def build_tool_advice(tool_type: str, project_type: str, techniques: list[str]) -> tuple[list[str], list[str], list[str]]:
    request_text = f"{project_type} {' '.join(techniques)}"
    catalog_advice = recommend_tools(request_text, tool_type, "beginner")
    if tool_type == "crochet":
        tools = [*catalog_advice, "호수 이름보다 실 라벨의 권장 mm를 먼저 확인하고 작은 샘플로 조정"]
        materials = ["면사 또는 아크릴 중간 굵기: 코 모양이 잘 보여 초보 연습에 적합", "가방/소품은 형태 유지를 위해 너무 흐물거리지 않는 실 선택"]
        accessories = ["단수링/마커: 첫 코나 단 시작 위치를 표시하는 작은 고리", "돗바늘: 실 끝을 숨기거나 편물을 잇는 굵은 바늘", "가위", "줄자"]
        if any("매직링" in t or "원형뜨기" in t for t in techniques):
            accessories.append("원형 시작점 표시용 잠금 마커")
        if "가방" in project_type:
            accessories.extend(["가방 손잡이 또는 D링", "안감 선택 사항"])
    elif tool_type == "needle_knitting":
        tools = [*catalog_advice, "목도리용 중간 굵기 실은 4.0-5.5mm가 흔한 출발 범위지만, 실 라벨 권장 mm와 세탁·건조한 10cm 게이지로 최종 결정"]
        materials = ["밝은 단색 실: 겉뜨기/안뜨기 구분이 쉽습니다.", "게이지(10cm 안의 코와 단 수)가 중요한 의류는 반드시 10cm 샘플을 먼저 뜹니다."]
        accessories = ["코수 마커: 코 위치를 표시하는 작은 고리", "돗바늘: 실 끝을 숨기거나 편물을 잇는 굵은 바늘", "가위", "줄자", "단수 카운터: 뜬 단 수를 기록하는 도구(선택)"]
    else:
        tools = [*catalog_advice, "코바늘/대바늘 중 작품 목표를 먼저 정하고, 실 라벨의 mm와 게이지를 확인하세요."]
        materials = ["처음에는 밝은 단색 중간 굵기 실을 선택하세요."]
        accessories = ["마커: 코나 단 위치를 표시하는 작은 고리", "돗바늘: 실 끝을 숨기거나 편물을 잇는 굵은 바늘", "가위", "줄자"]
    return tools, materials, accessories


def build_technique_resources(techniques: list[str]) -> list[dict]:
    resources = []
    for technique in techniques:
        item = TECHNIQUE_CATALOG.get(technique)
        if item:
            resources.append({"technique": technique, **item})
    return resources


def analyze_image_with_model(image_path: str, user_request: str) -> ImageObservation:
    """Observe an uploaded image through the configured structured provider."""
    prompt = (
        "너는 한국 뜨개 초보 코치의 이미지 관찰 담당자다. 첨부된 이미지에 실제로 보이는 내용만 먼저 기록하라. "
        "코바늘/대바늘, 작품 종류, 전체 형태, 조직, 바닥·몸통·손잡이 등 보이는 구조를 한국어로 설명하라. "
        "사진 한 장으로 확인할 수 없는 코 수, 뒷면, 바닥, 실 굵기, 정확한 기법은 사실처럼 단정하지 말고 uncertainties에 넣어라. "
        "사용자가 문제 해결을 요청했다면 보이는 근거가 있는 원인과 지금 할 수정만 diagnoses와 suggested_actions에 넣어라. "
        "additional_photos에는 현재 이미지에 이미 보이는 구도를 다시 요청하지 말고, 도안이나 진단을 바꾸는 숨은 구조만 넣어라. "
        "likely_techniques에는 한국어 표준 기법명을 사용하라. 모든 필드를 채우되 근거가 없으면 빈 배열을 사용하라.\n\n"
        f"사용자 요청: {user_request}"
    )
    return run_structured_model(prompt, ImageObservation, image_path=image_path, model_name=MODEL_NAME)


# ---------------------------------------------------------------------------
# Agent Tools (LangChain @tool): 웹 검색 / 파일 검색 / 커스텀 도메인
# resource_agent가 bind_tools로 물고, ToolNode + tools_condition 루프로 호출한다.
# 모든 tool은 네트워크/API 키가 없어도 동작하도록 deterministic fallback을 갖는다.
# ---------------------------------------------------------------------------

YARN_WEIGHT_GUIDE = {
    "lace": {"crochet_hook_mm": "1.5-2.25", "needle_mm": "1.5-2.25", "note": "매우 얇은 실. 숄/도일리용."},
    "fingering": {"crochet_hook_mm": "2.25-3.5", "needle_mm": "2.25-3.25", "note": "양말/얇은 의류용."},
    "dk": {"crochet_hook_mm": "3.5-4.5", "needle_mm": "3.25-4.0", "note": "가벼운 의류/소품용."},
    "worsted": {"crochet_hook_mm": "4.5-5.5", "needle_mm": "4.0-5.0", "note": "초보 연습에 가장 무난한 중간 굵기."},
    "aran": {"crochet_hook_mm": "5.5-6.5", "needle_mm": "5.0-5.5", "note": "가방/모자 등 형태 있는 소품용."},
    "bulky": {"crochet_hook_mm": "6.5-9", "needle_mm": "5.5-8.0", "note": "굵은 실. 빨리 완성되는 소품용."},
}


@tool
def search_technique_tutorials(technique: str, tool_type: str = "") -> list[dict]:
    """뜨개 기법 이름으로 실제 튜토리얼/영상 리소스를 웹에서 검색한다.

    사용자가 특정 기법(예: 매직링, 짧은뜨기, 겉뜨기)의 영상/튜토리얼을 원할 때 호출한다.
    네트워크나 검색 라이브러리(ddgs)가 없으면 curated fallback(유튜브 검색 링크 + 카탈로그 설명)을 반환한다.
    반환: [{"title": str, "url": str, "source": str}]
    """
    from urllib.parse import quote_plus

    query = f"{technique} 뜨개 tutorial".strip()
    try:
        from ddgs import DDGS  # API 키 불필요, 네트워크 필요

        with DDGS() as ddgs:
            hits = list(ddgs.text(query, max_results=3))
        results = [
            {"title": h.get("title", ""), "url": h.get("href", ""), "source": "ddgs"}
            for h in hits
            if h.get("href")
        ]
        if results:
            return results
    except Exception:
        pass
    # fallback: 키/네트워크 없이도 항상 유효한 결과를 준다.
    catalog = TECHNIQUE_CATALOG.get(technique, {})
    return [
        {
            "title": f"{technique} 기초 영상 검색",
            "url": f"https://www.youtube.com/results?search_query={quote_plus(query)}",
            "source": "fallback:youtube-search",
        },
        {
            "title": f"{technique} 설명",
            "url": catalog.get("prebuilt_video_asset_path", "local://videos/basics"),
            "source": "fallback:catalog",
        },
    ]


@tool
def search_local_pattern_samples(query: str) -> list[dict]:
    """로컬 저장소(samples/ 폴더 + 기법 카탈로그)에서 query에 맞는 자료 경로를 찾는다.

    사용자 작품과 비슷한 로컬 샘플 사진이나 기법별 prebuilt 영상 asset을 찾을 때 호출한다.
    반환: [{"path": str, "kind": str, "matched": str}]
    """
    lowered = query.lower()
    tokens = [tok for tok in lowered.split() if tok]
    results: list[dict] = []
    samples_dir = BASE_DIR / "samples"
    if samples_dir.exists():
        for path in sorted(samples_dir.glob("*")):
            if path.is_file() and (not tokens or any(tok in path.name.lower() for tok in tokens)):
                results.append({"path": str(path), "kind": "sample_image", "matched": path.name})
    for name, item in TECHNIQUE_CATALOG.items():
        if not tokens or lowered in name.lower() or any(tok in name.lower() for tok in tokens):
            results.append({"path": item["prebuilt_video_asset_path"], "kind": "video_asset", "matched": name})
    return results[:8] or [{"path": "samples/", "kind": "none", "matched": query}]


@tool
def recommend_tools_for_yarn(yarn_weight: str, tool_type: str = "crochet") -> dict:
    """실 굵기(yarn weight)로 권장 코바늘/대바늘 호수(mm)와 부자재를 추천한다.

    사용자가 특정 실 굵기(lace/fingering/dk/worsted/aran/bulky)에 맞는 도구를 물을 때 호출한다.
    반환: {"yarn_weight","crochet_hook_mm","needle_mm","recommended_mm","notions","note"}
    """
    key = yarn_weight.strip().lower()
    guide = YARN_WEIGHT_GUIDE.get(key, YARN_WEIGHT_GUIDE["worsted"])
    notions = ["단수링/마커", "돗바늘", "가위", "줄자"]
    recommended = guide["needle_mm"] if tool_type == "needle_knitting" else guide["crochet_hook_mm"]
    return {
        "yarn_weight": key if key in YARN_WEIGHT_GUIDE else f"{key}(미확인, worsted 기준)",
        "crochet_hook_mm": guide["crochet_hook_mm"],
        "needle_mm": guide["needle_mm"],
        "recommended_mm": recommended,
        "notions": notions,
        "note": guide["note"],
    }


KNITCOACH_TOOLS = [search_technique_tutorials, search_local_pattern_samples, recommend_tools_for_yarn]


def sample_bag_pattern(request: PatternRequest) -> PatternDraft:
    return PatternDraft(
        title="코바늘 네트 숄더백 도안 초안",
        summary=f"완성 크기 {request.finished_size}를 목표로 바닥부터 원형으로 올리는 네트 가방입니다.",
        tool_type="crochet",
        confidence="medium",
        techniques=["사슬뜨기", "빼뜨기", "한길긴뜨기", "매직링으로 원형 시작하기와 늘림"],
        materials=[f"{request.yarn_weight} 실", f"코바늘 {request.tool_size}", "단수링", "돗바늘", "가위"],
        gauge_guidance=(
            f"현재 게이지: {request.gauge}. 10cm 네트 샘플을 먼저 뜨고 목표 폭에 맞춰 "
            "바닥의 마지막 단 반복 수를 조정하세요."
        ),
        construction=["타원형 또는 원형 바닥", "네트 무늬 몸통", "짧은 손잡이", "별도 크로스끈"],
        instructions=[
            "1단: 사슬 12코를 만들고 양쪽 면을 돌아 타원형 바닥을 시작합니다.",
            "2–3단: 양 끝의 늘림 위치에 각 3코씩 넣고, 평평하게 놓이는지 확인합니다.",
            "4단 이후: 목표 바닥 크기까지 같은 늘림 규칙을 유지합니다. 샘플 사진은 약 6–7단 확장으로 추정됩니다.",
            "몸통 1단: *한길긴뜨기 1, 사슬 1, 한 코 건너뛰기*를 한 바퀴 반복하고 빼뜨기로 연결합니다.",
            "몸통: 원하는 높이까지 네트 무늬를 반복하며 매 단 시작점을 단수링으로 표시합니다.",
            "손잡이: 양쪽 중심을 표시하고 필요한 길이만큼 사슬을 만든 뒤 다음 단에서 짧은뜨기로 보강합니다.",
        ],
        finishing=["실 끝을 돗바늘로 숨깁니다.", "손잡이 연결부를 한 번 더 보강합니다.", "젖은 블로킹 후 크기를 확인합니다."],
        assumptions=[
            "사진만으로 정확한 코 수와 실 굵기를 확인할 수 없어 입력한 제작 조건을 우선했습니다.",
            "바닥과 몸통 연결부가 사진에 보이지 않아 일반적인 네트 가방 구조를 적용했습니다.",
            "완성 전 작은 게이지 샘플과 바닥 크기 확인이 필요합니다.",
        ],
        additional_photos=["가방 바닥 정면", "몸통 무늬 클로즈업", "손잡이 연결부"],
    )


def model_pattern_draft(image_path: str, request: PatternRequest) -> PatternDraft:
    """Create a structured provisional pattern through the configured provider."""
    prompt = (
        "너는 한국 뜨개 도안 설계자다. 첨부 이미지를 먼저 관찰한 뒤 사용자의 제작 조건에 맞는 한국어 테스트 도안 초안을 작성하라. "
        "사진에서 실제로 보이는 형태와 조직을 summary와 construction에 반영하라. 사진에서 보이지 않는 코 수, 뒷면 구조, "
        "바닥 구조와 게이지는 확정하지 말고 assumptions에 기록하라. additional_photos에는 현재 사진에 이미 보이는 구도를 다시 "
        "요청하지 말고 도안을 바꿀 수 있는 숨은 구조만 넣어라. instructions는 초보자가 작은 시험 샘플부터 검증할 수 있는 "
        "단계별 순서로 작성하라. 코바늘 가방에서 옆 솔기나 별도 패널의 증거가 보이지 않으면 두 장을 떠서 잇는 구조를 임의로 "
        "기본값으로 쓰지 말고, 바닥에서 시작해 빼뜨기와 기둥코로 단을 연결하며 원형으로 올라가는 임시 구조를 우선하라. "
        "사진만으로 원형뜨기인지 나선뜨기인지 확정할 수 없다면 그 차이도 assumptions에 밝혀라. 모든 필드를 한국어로 채워라.\n\n"
        f"사용자 제작 조건: {request.model_dump_json()}"
    )
    return run_structured_model(prompt, PatternDraft, image_path=image_path, model_name=MODEL_NAME)


def pattern_draft_agent(state: KnitCoachState) -> dict:
    image_path = state["uploaded_image_path"]
    if not image_path:
        response = "도안 초안을 만들려면 뜨개 작품 사진을 먼저 첨부해 주세요."
        return {"active_agent": "pattern_draft_agent", "pattern_draft": {}, "user_response": response}

    try:
        request = PatternRequest.model_validate(state["pattern_options"])
    except Exception:
        response = "상단의 **도안 만들기** 메뉴에서 완성 크기, 실 굵기와 바늘 크기를 입력하면 이 사진으로 도안 초안을 만들 수 있어요."
        return {"active_agent": "pattern_draft_agent", "pattern_draft": {}, "user_response": response}

    is_sample = "crochet-mesh-shoulder-bag" in state["original_image_name"].lower()
    try:
        if structured_model_available():
            draft = model_pattern_draft(image_path, request)
        elif is_sample:
            draft = sample_bag_pattern(request)
        else:
            response = (
                "현재 규칙 테스트 모드에서는 이 이미지의 실제 내용을 읽을 수 없습니다. "
                "`KNITCOACH_MODEL_PROVIDER=codex_exec` 개발 모드 또는 최종 `openai_api` 모드가 필요합니다."
            )
            return {"active_agent": "pattern_draft_agent", "pattern_draft": {}, "user_response": response}
    except ModelProviderError as exc:
        response = f"이미지 도안 분석을 완료하지 못했습니다. {exc}"
        return {
            "active_agent": "pattern_draft_agent",
            "pattern_draft": {},
            "user_response": response,
            "model_provider": active_provider_name(),
            "model_note": str(exc),
        }

    return {
        "active_agent": "pattern_draft_agent",
        "pattern_draft": draft.model_dump(),
        "tool_type": draft.tool_type,
        "detected_techniques": draft.techniques,
        "model_provider": active_provider_name(),
    }


def pattern_response_agent(state: KnitCoachState) -> dict:
    if state["user_response"]:
        return {"messages": [AIMessage(content=state["user_response"])]}
    draft = PatternDraft.model_validate(state["pattern_draft"])
    response = (
        f"### {draft.title}\n\n{draft.summary}\n\n"
        f"**핵심 기법:** {', '.join(draft.techniques)}\n\n"
        "도안 초안을 만들었습니다. 사진 한 장에서 확인할 수 없는 부분은 가정으로 표시했으니, "
        "작은 게이지 샘플을 먼저 떠 본 뒤 코 수를 조정해 주세요."
    )
    return {"user_response": response, "messages": [AIMessage(content=response)]}


def classifier_agent(state: KnitCoachState) -> dict:
    text = latest_user_text(state)
    existing_program = state.get("learning_program", {})
    model_decision = route_conversation_with_model(state)
    model_action = model_decision.action if model_decision else None
    support_modules = [module.value for module in model_decision.support_modules] if model_decision else []
    model_techniques = model_decision.technique_names if model_decision else []
    selected_tool_slugs = model_decision.tool_slugs if model_decision else []
    suggested_curriculum_ids = model_decision.suggested_curriculum_ids if model_decision else []
    rule_out_of_scope = not is_knitting_scope(
        text,
        existing_program=existing_program,
        has_image=bool(state["uploaded_image_path"]),
        task=state["task"],
    )
    out_of_scope = (
        model_action == ConversationAction.OUT_OF_SCOPE
        if model_decision
        else rule_out_of_scope
    )
    previous_journey = state.get("journey", JourneyType.START_FROM_ZERO)
    previous_profile = state.get("learner_profile", {})
    previous_project = state.get("detected_project_type", "")
    previous_tool_type = state.get("tool_type", "unknown")
    selected_curriculum_id = (
        model_decision.curriculum_id
        if model_decision and model_action == ConversationAction.SELECT_PROJECT
        else detect_curriculum(text)
    )
    pattern_literacy = is_pattern_literacy_request(text)
    asks_to_restart = (
        model_action == ConversationAction.RESTART_PROJECT
        if model_decision
        else bool(
            existing_program
            and any(
                phrase in normalize_text(text)
                for phrase in ("처음부터 설명", "처음부터 알려", "처음부터 보여", "첫 단계부터")
            )
        )
    )
    completion_phrases = ("연습 완료", "단계 완료", "다음 단계 미리보기", "완료했어요", "완료했어", "다 했어요", "다 했어", "다 떴어요", "다 떴어", "끝냈어요", "마쳤어요", "성공했어요", "성공했어")
    progression_phrases = ("다음 단계", "다음단계", "계속해줘", "계속 해줘", "계속 진행", "다음으로")
    asks_to_advance = (
        model_action in {ConversationAction.ADVANCE_STEP, ConversationAction.COMPLETE_STEP}
        if model_decision
        else bool(
            existing_program
            and existing_program.get("status") in {"active", "preview"}
            and any(phrase in normalize_text(text) for phrase in progression_phrases)
        )
    )
    is_program_completion = bool(
        existing_program
        and existing_program.get("status") in {"active", "preview"}
        and (
            asks_to_advance
            if model_decision
            else any(phrase in text for phrase in completion_phrases) or asks_to_advance
        )
    )
    model_program_actions = {
        ConversationAction.SELECT_PROJECT,
        ConversationAction.START_PROJECT,
        ConversationAction.NEED_MATERIALS,
        ConversationAction.PREVIEW_PROJECT,
        ConversationAction.SHOW_OVERVIEW,
        ConversationAction.EXPLAIN_CURRENT_STEP,
        ConversationAction.ADVANCE_STEP,
        ConversationAction.COMPLETE_STEP,
        ConversationAction.RESTART_PROJECT,
    }
    is_program_control = bool(
        existing_program
        and (
            model_action in model_program_actions
            if model_decision
            else any(phrase in normalize_text(text) for phrase in PROGRAM_CONTINUATION_PHRASES)
        )
    )
    program_turn = bool(selected_curriculum_id or is_program_control)
    if selected_curriculum_id:
        learning_program = new_learning_program(selected_curriculum_id)
    elif asks_to_restart:
        learning_program = restart_learning_program(existing_program)
    elif existing_program and existing_program.get("status") in {"awaiting_tools", "shopping", "preview", "preview_complete"} and (
        model_action == ConversationAction.START_PROJECT
        or (not model_decision and _curriculum_tools_ready(text, existing_program))
    ):
        learning_program = activate_learning_program(existing_program)
    elif existing_program and existing_program.get("status") in {"awaiting_tools", "shopping"} and (
        model_action == ConversationAction.PREVIEW_PROJECT
        or (not model_decision and _curriculum_wants_preview(text))
    ):
        learning_program = preview_learning_program(existing_program)
    elif existing_program and existing_program.get("status") in {"awaiting_tools", "shopping"} and not model_decision and _curriculum_wants_continue(text):
        # A bare “계속해줘” means “show me what comes next”, not “I own the tools”.
        # Continue safely in preview mode without recording practice progress.
        learning_program = preview_learning_program(existing_program)
    elif existing_program and existing_program.get("status") in {"awaiting_tools", "shopping"} and (
        model_action == ConversationAction.NEED_MATERIALS
        or (not model_decision and _curriculum_has_no_tools(text))
    ):
        learning_program = mark_learning_program_shopping(existing_program)
    elif is_program_completion:
        learning_program = advance_learning_program(existing_program)
    else:
        learning_program = existing_program
    if model_action == ConversationAction.SHOW_OVERVIEW:
        project_view = "overview"
    elif model_action in {
        ConversationAction.EXPLAIN_CURRENT_STEP,
        ConversationAction.ADVANCE_STEP,
        ConversationAction.COMPLETE_STEP,
        ConversationAction.RESTART_PROJECT,
    }:
        project_view = "step"
    elif model_action in {ConversationAction.START_PROJECT, ConversationAction.PREVIEW_PROJECT}:
        project_view = "overview"
    elif not model_decision and learning_program.get("status") in {"active", "preview"} and program_turn:
        was_inactive = existing_program.get("status") not in {"active", "preview"}
        project_view = "overview" if was_inactive else "step"
    else:
        project_view = "none"
    input_type = (
        "image_path"
        if state["uploaded_image_path"]
        else "text"
        if is_program_control
        else detect_input_type(text)
    )
    tool_type = detect_tool_type(text)
    for slug in selected_tool_slugs:
        selected_tool = get_tool(slug)
        if selected_tool and selected_tool.craft in {"crochet", "needle_knitting"}:
            tool_type = selected_tool.craft
            break
    if tool_type == "unknown" and previous_tool_type in {"crochet", "needle_knitting"}:
        tool_type = previous_tool_type
    current_skill = detect_current_skill(text, tool_type)
    pattern_request_words = ["도안 만들어", "도안을 만들어", "도안으로", "패턴 만들어", "pattern 만들어"]
    wants_image_pattern = state["task"] == "generate_pattern" or (
        bool(state["uploaded_image_path"]) and any(word in text.lower() for word in pattern_request_words)
    )
    intent = "generate_pattern" if wants_image_pattern else detect_intent(text, input_type)
    if model_action == ConversationAction.TOOL_QUESTION:
        input_type = "tool_question"
        intent = "advise_tools"
    elif model_action == ConversationAction.TECHNIQUE_QUESTION:
        intent = "learn_technique"
    elif model_action == ConversationAction.DIAGNOSE_PROJECT:
        intent = "analyze_artifact"
    elif model_action == ConversationAction.EXPLAIN_PATTERN:
        intent = "convert_pattern"
    if is_program_control:
        intent = "learn_technique"
    is_side_tool_question = input_type == "tool_question" and not is_program_control
    journey = infer_journey(
        text,
        input_type=input_type,
        intent=intent,
        has_image=bool(state["uploaded_image_path"]),
        task=state["task"],
    )
    if pattern_literacy:
        journey = JourneyType.EXPLAIN_PATTERN
    learner_level = "beginner" if any(word in text for word in ["처음", "초보", "입문"]) else previous_profile.get("level", "unknown")
    if (
        previous_journey == JourneyType.START_FROM_ZERO
        and learner_level == "beginner"
        and journey == JourneyType.CONTINUE_LEARNING
        and not any(word in text for word in ["지난", "이어서", "연습 결과", "다음 단계", "배웠", "완료"])
    ):
        journey = JourneyType.START_FROM_ZERO
    learner_profile = {"level": learner_level, "preferred_style": "hands_on" if "연습" in text else "unknown", "goal": detect_goal(text, tool_type)}
    techniques = detect_techniques(text, tool_type, current_skill)
    techniques = merge_unique(model_techniques, techniques)
    if pattern_literacy:
        current_skill = "도안 읽기"
        techniques = []
    if intent == "advise_tools":
        current_skill = "도구 선택"
        techniques = []
    explicit_techniques = resolve_techniques(text, tool_type if tool_type in {"crochet", "needle_knitting"} else None)
    if intent == "analyze_artifact" and not explicit_techniques and not state["uploaded_image_path"]:
        techniques = []
    sample_reference = get_sample_reference(text)
    if sample_reference:
        techniques = merge_unique(techniques, sample_reference["techniques"])
        tool_type = sample_reference["tool_type"]
    active_step = current_curriculum_step(learning_program)
    if learning_program:
        curriculum = CURRICULA[learning_program["curriculum_id"]]
        tool_type = curriculum.tool_type
        if program_turn and learning_program.get("status") in {"awaiting_tools", "shopping"}:
            current_skill = "도구 준비"
            techniques = []
        elif program_turn and active_step and not is_side_tool_question:
            current_skill = active_step.technique.split("(")[0]
            techniques = [active_step.technique]
    tool_type = infer_tool_type_from_techniques(tool_type, techniques)
    return {
        "out_of_scope": out_of_scope,
        "guardrail_reason": "뜨개 범위를 벗어난 질문" if out_of_scope else "",
        "journey": journey,
        "input_type": input_type,
        "intent": intent,
        "artifact_source": state["uploaded_image_path"] or text,
        "tool_type": tool_type,
        "learner_profile": learner_profile,
        "goal": learner_profile["goal"],
        "current_skill": current_skill,
        "blockers": detect_blockers(text),
        "detected_project_type": (
            previous_project or "미확정 프로젝트"
            if pattern_literacy
            else sample_reference.get("project_type", detect_project_type(text) or previous_project)
        ),
        "construction_parts": sample_reference.get("construction_parts", []),
        "pattern_reference_note": sample_reference.get("pattern_reference_note", ""),
        "pattern_type": detect_pattern_type(text, input_type),
        "detected_techniques": techniques,
        "user_feedback": text if intent == "revise_output" else "",
        "learning_program": learning_program,
        "program_turn": program_turn,
        "conversation_action": model_action.value if model_action else "rules_fallback",
        "support_modules": support_modules,
        "selected_tool_slugs": selected_tool_slugs,
        "suggested_curriculum_ids": suggested_curriculum_ids,
        "model_reply": model_decision.assistant_reply if model_decision else "",
        "model_follow_up": model_decision.follow_up_question if model_decision else "",
        "model_routed": bool(model_decision),
        "project_view": project_view,
    }


def _curriculum_tools_ready(text: str, program: dict) -> bool:
    """Require an affirmative tool-and-yarn confirmation before practice."""
    lowered = text.casefold()
    if any(word in lowered for word in ("없어요", "없어", "안 샀", "사야", "구매해야")):
        return False
    if any(word in lowered for word in ("준비됐", "준비 완료", "다 있어", "모두 있어")):
        return True
    curriculum = CURRICULA[program["curriculum_id"]]
    tool_words = ("코바늘",) if curriculum.tool_type == "crochet" else ("대바늘", "줄바늘")
    return "실" in lowered and any(word in lowered for word in tool_words)


def _curriculum_has_no_tools(text: str) -> bool:
    lowered = text.casefold()
    return any(word in lowered for word in ("아무것도 없", "준비물이 없", "도구가 없", "하나도 없", "안 샀", "사야", "구매해야"))


def _curriculum_wants_preview(text: str) -> bool:
    lowered = text.casefold()
    return any(phrase in lowered for phrase in ("먼저 보기", "먼저 볼", "미리보기", "과정을 먼저", "둘러볼"))


def _curriculum_wants_continue(text: str) -> bool:
    """Recognize short contextual commands after a project has been selected."""
    lowered = text.casefold().strip()
    return any(phrase in lowered for phrase in ("계속", "진행해", "다음으로"))


def scope_guardrail_agent(state: KnitCoachState) -> dict:
    """Keep the service knitting-only without leaking the previous lesson reply."""
    program = state.get("learning_program", {})
    if program and program.get("curriculum_id") in CURRICULA:
        curriculum = CURRICULA[program["curriculum_id"]]
        step = current_curriculum_step(program)
        progress_note = f" 현재 단계는 **{step.title}**입니다." if step else ""
        resume_note = (
            f"현재 **{curriculum.title}** 진도는 그대로 보관했어요.{progress_note} "
            "계속하려면 ‘현재 단계를 다시 설명해줘’, ‘다음 단계로 갈게요’처럼 말해 주세요."
        )
    else:
        resume_note = (
            "뜨개를 처음 시작한다면 만들고 싶은 작품을 말해 주세요. "
            "예: ‘코바늘로 작은 키링을 만들고 싶어요.’"
        )
    response = (
        "저는 **뜨개 질문과 작품 제작을 안내하는 코치**라서 요리나 다른 주제의 방법은 안내하지 않아요.\n\n"
        f"{resume_note}\n\n"
        "도와드릴 수 있는 내용은 코바늘·대바늘 기법, 도안 풀어 읽기, 실과 바늘 선택, "
        "작품별 단계 진행, 뜨다가 막힌 부분 진단입니다."
    )
    return {
        "active_agent": "scope_guardrail_agent",
        "user_response": response,
        "messages": [AIMessage(content=response)],
        "project_suggestions": [],
        "purchase_plan": {},
    }


def route_by_intent(state: KnitCoachState) -> str:
    if state.get("out_of_scope"):
        return "scope_guardrail_agent"
    # advise_tools도 technique_planner_agent를 먼저 거쳐 learning_path를 확정한 뒤
    # 공통 pipeline(technique_planner -> tool_advisor -> ...)에서 도구 안내를 생성한다.
    intent_to_agent = {
        "generate_pattern": "pattern_draft_agent",
        "analyze_artifact": "artifact_analyzer_agent",
        "convert_pattern": "pattern_converter_agent",
        "learn_technique": "technique_planner_agent",
        "advise_tools": "technique_planner_agent",
        "revise_output": "pattern_converter_agent",
    }
    return intent_to_agent.get(state["intent"], "technique_planner_agent")


def mark_active_agent(agent_name: str) -> dict:
    return {"active_agent": agent_name}


def artifact_analyzer_agent(state: KnitCoachState) -> dict:
    text = latest_user_text(state)
    techniques = state["detected_techniques"]
    tool_type = infer_tool_type_from_techniques(state["tool_type"], techniques)
    pattern_type = detect_pattern_type(text, state["input_type"])
    project_type = state["detected_project_type"] or detect_project_type(text)
    photo_findings, mistake_diagnoses, recommended_fixes = build_photo_findings(text, pattern_type, techniques, state["blockers"])
    image_observation: dict = {}
    model_note = ""
    if state["input_type"] == "image_path":
        image_path = state["uploaded_image_path"] or state["artifact_source"]
        if structured_model_available():
            try:
                observation = analyze_image_with_model(image_path, text)
                image_observation = observation.model_dump()
                if observation.tool_type != "unknown":
                    tool_type = observation.tool_type
                observed_project = detect_project_type(observation.project_type)
                if observed_project != "미확정 프로젝트":
                    project_type = observed_project
                observed_techniques: list[str] = []
                for label in observation.likely_techniques:
                    observed_techniques.extend(
                        item.name
                        for item in resolve_techniques(
                            label,
                            observation.tool_type if observation.tool_type != "unknown" else None,
                        )
                    )
                techniques = merge_unique(techniques, observed_techniques)
                photo_findings = observation.visible_facts
                mistake_diagnoses = observation.diagnoses
                recommended_fixes = observation.suggested_actions
            except ModelProviderError as exc:
                model_note = str(exc)
        else:
            model_note = "현재 규칙 테스트 모드에서는 사진 픽셀을 분석하지 않습니다."

    difficulty_level, difficulty_reasons = infer_difficulty(pattern_type, project_type, techniques, state["blockers"])
    sample_reference = get_sample_reference(text)
    if sample_reference:
        difficulty_level = sample_reference["difficulty_level"]
        difficulty_reasons = merge_unique(difficulty_reasons, sample_reference["difficulty_reasons"])
        photo_findings = merge_unique(photo_findings, sample_reference["photo_findings"])
        mistake_diagnoses = merge_unique(mistake_diagnoses, sample_reference["mistake_diagnoses"])
        recommended_fixes = merge_unique(recommended_fixes, sample_reference["recommended_fixes"])
    if image_observation:
        analysis = image_observation["summary"]
    elif pattern_type in {"photo", "finished_object"}:
        analysis = "완성품/사진 입력을 기준으로 작품 유형, 기법, 난이도, 문제 가능 지점을 분석했습니다."
    elif pattern_type in {"symbol_chart", "diagram_chart", "written_pattern"}:
        analysis = "도안 입력을 기준으로 반복 구조, 필요한 기법, 초보자가 막힐 지점을 분석했습니다."
    else:
        analysis = "사용자 설명을 기준으로 필요한 기법과 학습 순서를 분석했습니다."
    return {
        "active_agent": "artifact_analyzer_agent",
        "artifact_analysis": analysis,
        "pattern_type": pattern_type,
        "tool_type": tool_type,
        "detected_project_type": project_type,
        "difficulty_level": difficulty_level,
        "difficulty_reasons": difficulty_reasons,
        "photo_findings": photo_findings,
        "mistake_diagnoses": mistake_diagnoses,
        "recommended_fixes": recommended_fixes,
        "construction_parts": image_observation.get("construction", sample_reference.get("construction_parts", state["construction_parts"])),
        "pattern_reference_note": sample_reference.get("pattern_reference_note", state["pattern_reference_note"]),
        "image_observation": image_observation,
        "model_provider": active_provider_name(),
        "model_note": model_note,
    }


def pattern_converter_agent(state: KnitCoachState) -> dict:
    text = latest_user_text(state)
    lowered = normalize_text(text)
    should_convert = state["intent"] in {"convert_pattern", "revise_output"} or state["input_type"] in {"pattern_text", "explanation_text"}
    if not should_convert:
        return {}
    if state["input_type"] == "explanation_text":
        generated_pattern = row_by_row_pattern_from_text(text)
        generated_explanation = "입력에서 명시적으로 확인되는 코 수와 단 수만 도안 초안에 반영했습니다."
        conversion_mode = "explanation_to_chart" if "chart" in lowered or "차트" in text else "explanation_to_pattern"
    elif state["input_type"] == "pattern_text" or has_pattern_abbrev(lowered):
        generated_explanation = beginner_explanation_from_pattern(text)
        generated_pattern = text
        conversion_mode = "pattern_to_explanation"
    else:
        generated_pattern = row_by_row_pattern_from_text(text)
        generated_explanation = "입력에서 명시적으로 확인되는 코 수와 단 수만 도안 초안에 반영했습니다."
        conversion_mode = "explanation_to_chart" if "chart" in lowered or "차트" in text or "도안" in text else "explanation_to_pattern"
    return {"active_agent": "pattern_converter_agent", "conversion_mode": conversion_mode, "generated_explanation": generated_explanation, "generated_pattern": generated_pattern, "chart_spec": {}}


def chart_generator_agent(state: KnitCoachState) -> dict:
    if not state["chart_spec"]:
        return {}
    return {"active_agent": state["active_agent"] or "chart_generator_agent", "chart_image_path": ""}


def technique_planner_agent(state: KnitCoachState) -> dict:
    tool_type = state["tool_type"]
    current_skill = state["current_skill"]
    selected = next(
        (TECHNIQUE_CATALOG[name] for name in state["detected_techniques"] if name in TECHNIQUE_CATALOG),
        None,
    )
    if tool_type == "crochet":
        learning_path = "crochet_beginner"
        curriculum_stage = CROCHET_CURRICULUM.get(
            current_skill,
            f"{selected['learning_goal']}" if selected else CROCHET_CURRICULUM["사슬뜨기"],
        )
    elif tool_type == "needle_knitting":
        learning_path = "needle_knitting_beginner"
        curriculum_stage = NEEDLE_CURRICULUM.get(
            current_skill,
            f"{selected['learning_goal']}" if selected else NEEDLE_CURRICULUM["코 잡기"],
        )
    else:
        learning_path = "diagnose_tool"
        curriculum_stage = "0. 목표 작품과 보유 도구를 확인해 학습 path 결정하기"
    return {"active_agent": state["active_agent"] or "technique_planner_agent", "learning_path": learning_path, "curriculum_stage": curriculum_stage}


def tool_advisor_agent(state: KnitCoachState) -> dict:
    required_tools, required_materials, accessories = build_tool_advice(state["tool_type"], state["detected_project_type"], state["detected_techniques"])
    if state["intent"] == "advise_tools":
        text = latest_user_text(state)
        level = state.get("learner_profile", {}).get("level", "beginner")
        selected_tools = [get_tool(slug) for slug in state.get("selected_tool_slugs", [])]
        selected_tools = [item for item in selected_tools if item]
        if selected_tools:
            direct_advice = [
                f"{item.name}: {item.budget_choice if level in {'beginner', 'first_project', 'unknown'} else item.upgrade_choice}"
                for item in selected_tools[:3]
            ]
        else:
            direct_advice = recommend_tools(text, state["tool_type"], level)
        if resolve_tools(text):
            sizing_notes = [item for item in required_tools if "권장 mm" in item or "게이지" in item]
            required_tools = merge_unique(direct_advice, sizing_notes)
        else:
            required_tools = merge_unique(direct_advice, required_tools)
    return {"active_agent": state["active_agent"] or "tool_advisor_agent", "required_tools": required_tools, "required_materials": required_materials, "accessories": accessories}


def technique_scout(payload: dict) -> dict:
    """Send로 전달된 단일 기법 하나에 대한 리소스 dict를 만든다 (병렬 fan-out의 map 단계).

    payload에 완성된 resource dict가 실려 오면(예: 샘플 가방 맞춤 영상) 그대로 사용하고,
    그 외에는 기법 이름으로 TECHNIQUE_CATALOG를 조회한다.
    """
    if payload.get("resource"):
        return {"technique_resources": [payload["resource"]]}
    technique = payload.get("technique", "")
    return {"technique_resources": build_technique_resources([technique])}


def fan_out_techniques(state: KnitCoachState):
    """감지된 기법마다 technique_scout로 Send fan-out(병렬 map).

    기법이 하나도 없으면 Send 대신 문자열 "resource_agent"를 돌려보내 그래프가 멈추지 않게 한다.
    """
    if state.get("program_turn") and state.get("learning_program", {}).get("status") == "awaiting_tools":
        return "resource_agent"
    techniques = list(state["detected_techniques"])
    if not techniques and state["learning_path"] == "crochet_beginner":
        techniques = ["사슬뜨기(chain stitch)", "짧은뜨기(single crochet)"]
    elif not techniques and state["learning_path"] == "needle_knitting_beginner":
        techniques = ["롱테일 코잡기(long-tail cast on)", "겉뜨기(knit stitch)"]
    sends = [Send("technique_scout", {"technique": t}) for t in techniques]
    if state["pattern_reference_note"]:
        sample_ref = get_sample_reference(latest_user_text(state))
        sends.append(Send("technique_scout", {"resource": {
            "technique": "샘플 가방 맞춤 영상",
            "tool_type": "crochet",
            "difficulty": state["difficulty_level"],
            "description": "완성품 사진과 도안 reference를 함께 설명하는 작품별 생성 영상 요청입니다.",
            "common_mistakes": ["바닥 단수 확장 규칙 누락", "몸통 반복무늬 연결 위치 혼동"],
            "prebuilt_video_asset_path": "local://videos/crochet-mesh-shoulder-bag-reference",
            "custom_video_generation_prompt": sample_ref.get("custom_project_video_prompt", "샘플 작품의 도안 구조와 수정 포인트를 설명하는 짧은 영상"),
        }}))
    return sends or "resource_agent"


def resource_agent(state: KnitCoachState) -> dict:
    """LLM이 tool(웹검색/파일검색/커스텀)을 호출해 리소스를 보강하는 노드.

    - OPENAI_API_KEY가 있으면 bind_tools + tools_condition 루프로 실제 tool을 호출한다.
    - tool 결과(ToolMessage)를 이미 받은 뒤 재진입하면 tool 없이 요약만 만들어 루프를 1회로 끝낸다.
    - 키가 없거나 기법이 없으면 LLM을 호출하지 않고 tool_calls 없는 메시지만 남겨
      곧장 teacher_agent로 진행한다(offline-first 보장).
    """
    techniques = state["detected_techniques"]
    if not (HAS_OPENAI_KEY and techniques):
        note = (
            "offline mode: tool 호출 없이 카탈로그 기반 리소스를 사용했습니다."
            if not HAS_OPENAI_KEY
            else "감지된 기법이 없어 tool 호출을 생략했습니다."
        )
        return {"tool_findings": note, "messages": [AIMessage(content=f"[resource_agent] {note}")]}
    try:
        from langchain_openai import ChatOpenAI

        base_model = ChatOpenAI(model=MODEL_NAME, temperature=0)
        turn_messages = current_turn_messages(state)
        already_used_tools = any(isinstance(m, ToolMessage) for m in turn_messages)
        if already_used_tools:
            # tool 결과를 받은 뒤: tool 없이 요약만 -> tool_calls가 없으므로 루프 종료 보장.
            summary = base_model.invoke(
                turn_messages
                + [SystemMessage(content="위 tool 결과를 바탕으로 학습자에게 도움이 되는 리소스를 한국어 3줄 이내로 요약하라. 더 이상 tool을 호출하지 마라.")]
            )
            return {"messages": [summary], "tool_findings": str(summary.content)}
        model = base_model.bind_tools(KNITCOACH_TOOLS)
        context = (
            f"학습자 도구: {state['tool_type']}, 작품: {state['detected_project_type']}, "
            f"기법: {', '.join(techniques)}, 난이도: {state['difficulty_level']}."
        )
        response = model.invoke(
            [SystemMessage(content=(
                "너는 뜨개 교육 agent의 리소스 리서처다. 필요하면 제공된 tool을 호출해 "
                "학습자에게 맞는 튜토리얼/로컬 샘플/도구 추천을 찾아라. 각 tool은 최대 한 번씩만 호출하라.\n"
                + context
            ))]
            + turn_messages
        )
        result = {"messages": [response]}
        if not getattr(response, "tool_calls", None):
            result["tool_findings"] = str(response.content)
        return result
    except Exception as exc:
        note = f"tool 리서치를 시도했지만 fallback으로 전환했습니다: {exc.__class__.__name__}"
        return {"tool_findings": note, "messages": [AIMessage(content=f"[resource_agent] {note}")]}


def _primary_technique_content(state: KnitCoachState) -> tuple[str, dict] | tuple[None, None]:
    text = latest_user_text(state)
    if state["journey"] == JourneyType.CONTINUE_LEARNING and "다음 단계" in text:
        next_by_current = {
            "사슬뜨기(chain stitch)": "짧은뜨기(single crochet)",
            "롱테일 코잡기(long-tail cast on)": "겉뜨기(knit stitch)",
        }
        for name in state["detected_techniques"]:
            next_name = next_by_current.get(name)
            if next_name:
                return next_name, TECHNIQUE_CATALOG[next_name]
    for name in state["detected_techniques"]:
        item = TECHNIQUE_CATALOG.get(name)
        if item:
            return name, item
    return None, None


def _tool_definition_lesson(text: str) -> str | None:
    """Return a direct catalog-backed explanation for a named tool or notion."""
    if not is_tool_definition_question(text):
        return None
    matches = resolve_tools(text)
    if not matches:
        return None
    item = matches[0]
    uses = "\n".join(f"- {use}" for use in item.best_for)
    tips = "\n".join(f"- {tip}" for tip in item.buying_tips[:3])
    return (
        f"### {item.name}\n\n"
        f"{item.summary}\n\n"
        f"**어디에 쓰나요?**\n{uses}\n\n"
        f"**처음 사용할 때 확인할 점**\n{tips}\n\n"
        f"처음에는 {item.budget_choice}"
    )


def _selected_tool_lesson(slugs: list[str]) -> str | None:
    """Explain model-selected tools strictly from the authored tool catalog."""
    items = [get_tool(slug) for slug in slugs]
    items = [item for item in items if item]
    if not items:
        return None
    sections = []
    for item in items[:3]:
        uses = " · ".join(item.best_for[:3])
        size_note = item.size_guide[0] if item.size_guide else "작품 도안과 실 라벨의 규격을 먼저 확인하세요."
        sections.append(
            f"### {item.name}\n\n{item.summary}\n\n"
            f"**잘 맞는 작업** · {uses}\n\n"
            f"**규격 확인** · {size_note}\n\n"
            f"**첫 구매** · {item.budget_choice}"
        )
    return "\n\n".join(sections)


def _pattern_literacy_lesson(text: str) -> str | None:
    """Return a beginner-first guide for the four authored notation entry points."""
    if not is_pattern_literacy_request(text):
        return None
    lowered = normalize_text(text)
    if "영문 코바늘" in lowered or all(token in lowered for token in ("ch", "sc", "dc")):
        return (
            "### 영문 코바늘 약어 읽기\n\n"
            "영문 도안은 **단 번호 → 반복 묶음 → 단 끝 코 수** 순서로 읽으면 됩니다.\n\n"
            "- `MR` = 매직링\n- `ch` = 사슬뜨기\n- `sc` = 짧은뜨기\n"
            "- `hdc` = 긴뜨기\n- `dc` = 한길긴뜨기\n- `sl st` = 빼뜨기\n"
            "- `inc` = 한 코에 두 코를 뜨는 늘려뜨기\n- `[12]` = 그 단을 마친 뒤 총 12코\n\n"
            "예: `R2: (1 sc, inc) × 6 [18]`은 **2단에서 짧은뜨기 1코와 늘려뜨기 1회를 여섯 번 반복하고, 총 18코인지 확인**하라는 뜻입니다."
        )
    if "영문 대바늘" in lowered or all(token in lowered for token in ("k", "p", "k2tog")):
        return (
            "### 영문 대바늘 약어 읽기\n\n"
            "대바늘 도안은 먼저 현재 단이 겉면인지 뒷면인지 확인하고 왼쪽부터 읽습니다.\n\n"
            "- `CO` = 코잡기\n- `K` = 겉뜨기\n- `P` = 안뜨기\n"
            "- `yo` = 바늘에 실을 감아 한 코 늘리기\n- `k2tog` = 두 코를 함께 겉뜨기해 한 코 줄이기\n"
            "- `BO` = 코막음\n\n"
            "예: `Row 1: K2, P2, rep to end`는 **겉뜨기 2코, 안뜨기 2코를 단 끝까지 반복**하라는 뜻입니다."
        )
    if "기호 도안" in lowered:
        return (
            "### 코바늘 기호 도안 읽기\n\n"
            "기호 도안은 **범례 → 시작점 → 진행 방향 → 반복 구간 → 단 끝 코 수** 순서로 봅니다.\n\n"
            "- `○` 또는 타원 = 사슬뜨기\n- `×` 또는 `+` = 짧은뜨기\n"
            "- `T` 모양 = 긴뜨기 계열이며 가로선 수에 따라 높이가 달라짐\n"
            "- 검은 점 = 빼뜨기인 경우가 많음\n- 같은 밑점에서 기호 두 개가 갈라짐 = 늘려뜨기\n\n"
            "원형 도안은 가운데 매직링이나 사슬 고리에서 시작해 바깥쪽으로 읽습니다. 단 시작의 기둥코와 빼뜨기 위치는 점이나 화살표를 먼저 찾고, **출판 도안마다 기호가 다를 수 있으므로 그 도안의 범례를 최우선**으로 확인하세요."
        )
    if "반복" in lowered or "repeat" in lowered:
        return (
            "### 반복 구간 찾기\n\n"
            "도안에서 반복은 한 덩어리로 묶어 읽습니다.\n\n"
            "- `(sc 2, inc) × 6` = 괄호 안을 여섯 번 반복\n"
            "- `*K1, P1; rep from *` = 별표 뒤부터 단 끝까지 반복\n"
            "- `[ch 2, dc] 4 times` = 대괄호 안을 네 번 반복\n"
            "- `rep to last 2 sts` = 마지막 2코가 남을 때까지 반복\n\n"
            "반복 한 묶음에서 사용되는 코 수를 먼저 계산한 뒤 반복 횟수를 곱하고, 도안에 적힌 단 끝 총 코 수와 맞는지 확인하세요."
        )
    return (
        "### 뜨개 도안 읽기\n\n"
        "먼저 도안 범례에서 약어와 기호 뜻을 확인한 뒤, 시작 코 수와 단 번호를 찾으세요. "
        "그다음 괄호·별표로 묶인 반복 구간을 한 묶음씩 풀어 쓰고, 마지막에 적힌 총 코 수와 맞는지 확인하면 됩니다. "
        "읽고 있는 한 줄을 그대로 붙여 주면 약어를 한글 동작으로 바꿔 설명해 드릴게요."
    )


def teacher_agent(state: KnitCoachState) -> dict:
    techniques = ", ".join(state["detected_techniques"]) if state["detected_techniques"] else state["current_skill"]
    blockers = ", ".join(state["blockers"]) if state["blockers"] else "아직 뚜렷한 막힘은 없음"
    difficulty = state["difficulty_level"]
    reasons = "; ".join(state["difficulty_reasons"]) if state["difficulty_reasons"] else "난이도 판단 근거가 아직 부족합니다."
    technique_name, technique = _primary_technique_content(state)
    learning_program = state.get("learning_program", {})
    project_suggestions: list[str] = list(state.get("suggested_curriculum_ids", []))
    purchase_plan: dict = {}
    support_modules = set(state.get("support_modules", []))
    direct_tool_lesson = _tool_definition_lesson(latest_user_text(state)) or _selected_tool_lesson(
        state.get("selected_tool_slugs", [])
    )
    pattern_literacy_lesson = _pattern_literacy_lesson(latest_user_text(state))
    structured_technique = bool(
        technique
        and (
            SupportModule.TECHNIQUE_LIBRARY.value in support_modules
            or (not state.get("model_routed") and state["intent"] == "learn_technique")
        )
    )
    if (
        state.get("model_reply")
        and not state.get("program_turn")
        and not direct_tool_lesson
        and not structured_technique
        and not pattern_literacy_lesson
    ):
        lesson = state["model_reply"]
    elif direct_tool_lesson:
        lesson = state.get("model_reply") or direct_tool_lesson
    elif pattern_literacy_lesson:
        lesson = pattern_literacy_lesson
    elif state.get("program_turn") and learning_program and learning_program.get("status") == "shopping":
        curriculum = CURRICULA[learning_program["curriculum_id"]]
        purchase_plan = build_purchase_plan(curriculum.id)
        lesson = (
            f"좋아요. **{curriculum.title}**에 필요한 것만 골라 준비할 수 있게 정리했어요. "
            "같은 준비물 질문은 다시 하지 않을게요.\n\n"
            "아래 구매 카드에서 도구 생김새와 정확한 규격, 초보 구매처를 함께 볼 수 있어요. "
            "지금 바로 살 필요는 없습니다. **도구 없이 먼저 작품 과정 보기**를 열어 전체 순서와 사용 기법부터 둘러봐도 돼요."
        )
    elif state.get("program_turn") and learning_program and learning_program.get("status") == "awaiting_tools":
        curriculum = CURRICULA[learning_program["curriculum_id"]]
        starter_kit = "\n".join(f"- {item}" for item in curriculum.starter_kit)
        if any(word in latest_user_text(state) for word in ("없어요", "없어", "안 샀", "사야", "구매해야")):
            opening = (
                "괜찮아요. 아무 도구가 없어도 여기서부터 준비하면 됩니다. "
                "처음에는 큰 세트보다 아래 규격만 단품으로 사는 편이 부담이 적어요."
            )
        else:
            opening = (
                f"**{curriculum.title}**을 선택했어요. 좋은 선택이에요. "
                "아직 연습은 시작하지 않고, 먼저 집에 있는 도구와 필요한 준비물을 맞춰 볼게요."
            )
        lesson = (
            f"{opening}\n\n"
            f"### 시작 준비물\n{starter_kit}\n\n"
            "실 라벨에 적힌 권장 바늘 mm가 위 범위와 다르면 **실 라벨을 우선**하세요. "
            "이미 도구가 있다면 실 이름·굵기와 바늘의 mm를 적어 주세요. 사진으로 보여줘도 됩니다. "
            "아무것도 없다면 위 목록만 준비하면 되고, 준비됐다고 알려준 뒤 첫 기법을 시작할게요."
        )
    elif state.get("program_turn") and learning_program:
        curriculum = CURRICULA[learning_program["curriculum_id"]]
        completed = len(learning_program["completed_steps"])
        total = len(curriculum.steps)
        step = current_curriculum_step(learning_program)
        if step:
            preview_note = (
                "**미리보기 모드** · 준비물 없이 작품 순서를 둘러보고 있어요. "
                "실제로 시작할 때 ‘준비됐어요’라고 말하면 1단부터 진도를 새로 시작합니다.\n\n"
                if learning_program.get("status") == "preview" else ""
            )
            if curriculum.written_pattern:
                progress = f"미리보기 {learning_program['current_step'] + 1}/{total}" if learning_program.get("status") == "preview" else f"작품 진도 {completed}/{total}"
                if state.get("project_view") == "overview":
                    lesson = (
                        f"{preview_note}### {curriculum.title} 전체 과정\n\n"
                        f"**{progress} · {step.title}**\n\n"
                        "먼저 전체 도안과 시작·본문·마무리 흐름을 한 번 보여드릴게요. "
                        f"아래 작업대 한 곳에서 전체 흐름을 확인한 뒤 **‘{step.title} 자세히 시작하기’**를 누르면 전체 도안은 접고, "
                        "현재 단계의 손동작·코 수·완료 기준에 집중해서 진행합니다."
                    )
                else:
                    lesson = (
                        f"{preview_note}### {curriculum.title}\n\n"
                        f"**{progress} · {step.title}**\n\n"
                        f"{step.why}\n\n"
                        f"지금 할 일은 **{step.practice}**입니다. 아래 작업대에서 도안의 현재 위치와 "
                        "완료 기준을 확인하고, 끝나면 버튼으로 다음 단계로 이동하세요."
                    )
            else:
                progress = (
                    f"미리보기 {learning_program['current_step'] + 1}/{total}"
                    if learning_program.get("status") == "preview"
                    else f"학습 진도 {completed}/{total} · 지금은 {completed + 1}단계"
                )
                lesson = preview_note + (
                    f"### {curriculum.title}\n\n"
                    f"**{progress}**\n\n"
                    f"#### {step.title}\n\n"
                    f"{step.why}\n\n"
                    f"**작품에서 쓰는 곳**\n{step.project_use}"
                )
                if technique:
                    steps = "\n".join(f"{index}. {item}" for index, item in enumerate(technique["steps"], start=1))
                    lesson += f"\n\n**기법 익히기 · {step.technique.split('(')[0]}**\n{steps}"
        else:
            guide = "\n".join(f"{index}. {item}" for index, item in enumerate(curriculum.project_guide, start=1))
            assumptions = "\n".join(f"- {item}" for item in curriculum.assumptions)
            lesson = (
                f"### 기법 연습 완료 · 이제 {curriculum.title}을 떠요\n\n"
                f"필요한 {total}개 기법 단계를 모두 마쳤어요. 아래 순서대로 실제 작품을 진행하세요.\n\n"
                f"**작품 제작 가이드**\n{guide}\n\n"
                f"**이 도안의 기준**\n{assumptions}"
            )
    elif state["journey"] == JourneyType.START_FROM_ZERO:
        if state["detected_project_type"] == "키링/keyring":
            lesson = (
                "키링은 짧은 시간 안에 완성 경험을 만들기 좋은 코바늘 입문 작품이에요. "
                "아래 두 작품은 완성 모양과 배우는 기법이 다릅니다. 사진을 보고 마음에 드는 것을 먼저 골라보세요. "
                "선택한 뒤에 도구를 확인하고, 준비가 끝난 다음에만 기법 연습을 시작합니다."
            )
            project_suggestions = beginner_project_ids(state["detected_project_type"], state["tool_type"])
        elif state["detected_project_type"] == "가방/bag":
            lesson = (
                "가방은 **코바늘**과 **대바늘** 모두 만들 수 있어요. 코바늘은 조직이 단단하고 형태가 잘 잡혀 "
                "작은 토트백이나 네트백에 잘 맞고, 대바늘은 부드럽고 평평한 편물을 떠서 접어 잇는 파우치에 잘 맞습니다.\n\n"
                "완성 사진을 보고 첫 작품을 고르세요. 선택 전에는 연습을 시작하지 않고, 도구와 재료부터 확인합니다."
            )
            project_suggestions = beginner_project_ids(state["detected_project_type"], state["tool_type"])
        elif state["detected_project_type"] in {"컵받침/coaster", "목도리/scarf"}:
            project_suggestions = beginner_project_ids(state["detected_project_type"], state["tool_type"])
            lesson = (
                "좋아요. 같은 종류 안에서도 배우는 기법과 완성 시간이 다릅니다. "
                "아래의 검수된 입문 작품에서 사진과 난이도를 비교해 골라보세요. "
                "고른 뒤 준비물을 확인하고 해당 작품에 필요한 기법만 순서대로 연결하겠습니다."
            )
        elif state["tool_type"] == "unknown" or state["detected_project_type"] == "미확정 프로젝트":
            lesson = (
                "처음이라면 기법 이름부터 고르기보다 **완성하고 싶은 모습**을 먼저 보는 편이 쉬워요. "
                "아래 작품은 이미 준비물·연습 순서·제작 과정을 검수해 둔 입문 코스입니다.\n\n"
                "코바늘은 작고 빨리 완성되는 소품부터, 대바늘은 같은 동작을 반복하는 목도리부터 배치했어요. "
                "사진을 보고 하나를 고르면 도구 보유 여부부터 확인하겠습니다."
            )
            project_suggestions = beginner_project_ids(state["detected_project_type"], state["tool_type"])
        else:
            lesson = (
                f"첫 작품 목표는 **{state['detected_project_type']}**로 이해했어요. "
                "바로 연습을 시작하기 전에 원하는 크기, 가지고 있는 실과 바늘, 하루에 가능한 시간을 알려주세요. "
                "그 조건에 맞춰 가장 쉬운 제작 순서부터 정리할게요."
            )
    elif state["journey"] == JourneyType.CONTINUE_LEARNING and "연습 결과" in latest_user_text(state):
        lesson = (
            "좋아요. 지난 연습 결과부터 같이 확인해 볼게요.\n\n"
            "1. 시작할 때와 끝났을 때의 코 수가 같은가요?\n"
            "2. 코 크기가 유난히 크거나 작은 구간이 있나요?\n"
            "3. 가장자리가 곧은가요, 안쪽이나 바깥쪽으로 휘나요?\n\n"
            "가능하면 전체 모습과 가장자리 가까운 사진을 한 장씩 보여주세요. 사진이 없어도 세 질문에 답하면 다음 연습을 정할 수 있어요."
        )
    elif state["journey"] == JourneyType.START_FROM_MATERIALS:
        tools = "\n".join(f"- {item}" for item in state["required_tools"])
        materials = "\n".join(f"- {item}" for item in state["required_materials"])
        accessories = "\n".join(f"- {item}" for item in state["accessories"])
        if state["tool_type"] == "crochet":
            project_suggestion = "중간 굵기 실 한두 타래라면 코스터, 작은 파우치, 짧은 네트백부터 검토해 보세요."
        elif state["tool_type"] == "needle_knitting":
            project_suggestion = "울 실 두 타래라면 라벨의 총 길이와 굵기를 먼저 확인하세요. 길이가 충분하면 짧은 목도리나 헤어밴드를 후보로 볼 수 있습니다."
        else:
            project_suggestion = "실 라벨의 권장 바늘 크기, 실 굵기, 총 길이를 알려주면 만들 수 있는 작품을 좁혀드릴게요."
        lesson = (
            f"### 가진 재료로 시작하기\n\n{project_suggestion}\n\n"
            f"**바늘 안내**\n{tools}\n\n**실 선택 메모**\n{materials}\n\n**함께 준비할 것**\n{accessories}"
        )
    elif state["intent"] == "learn_technique" and technique:
        if state.get("model_reply") and structured_technique:
            lesson = (
                f"{state['model_reply']}\n\n"
                f"아래 **{technique_name.split('(')[0]} 기법 카드**에서 실제 손동작, 핵심 장면과 연습 기준을 이어서 확인할 수 있어요."
            )
        else:
            steps = "\n".join(f"{index}. {step}" for index, step in enumerate(technique["steps"], start=1))
            corrections = "\n".join(
                f"- {mistake} → {fix}"
                for mistake, fix in zip(technique["common_mistakes"], technique["mistake_fixes"])
            )
            lesson = (
                f"### {technique_name.split('(')[0]} · {technique['abbreviation']}\n\n"
                f"{technique['description']}\n\n"
                f"**이번 목표**\n{technique['learning_goal']}\n\n"
                f"**뜨는 순서**\n{steps}\n\n"
                f"**자주 하는 실수와 교정**\n{corrections}"
            )
        term_notes = []
        if "foundation" in lesson:
            term_notes.append("foundation: 작품을 시작하는 첫 사슬이나 첫 단")
        if "yarn over" in lesson:
            term_notes.append("yarn over: 바늘에 실을 감는 동작")
        if technique["abbreviation"]:
            term_notes.append(f"{technique['abbreviation']}: 도안에서 {technique_name.split('(')[0]}를 줄여 쓰는 표시")
        if term_notes:
            lesson += "\n\n**용어 메모**\n" + "\n".join(f"- {note}" for note in term_notes)
    elif state["learning_path"] == "crochet_beginner":
        lesson = (
            f"지금 목표에는 코바늘이 잘 맞아요. **{state['detected_project_type']}**을 만들기 전에 "
            "완성 크기와 가지고 있는 실·코바늘을 먼저 맞춰 볼게요. "
            "실 라벨의 권장 mm와 가지고 있는 코바늘 mm를 알려주면 필요한 것만 골라드릴게요."
        )
    elif state["learning_path"] == "needle_knitting_beginner":
        lesson = (
            f"지금 목표에는 대바늘이 잘 맞아요. **{state['detected_project_type']}**의 크기와 형태를 정한 뒤 "
            "가지고 있는 실과 대바늘 mm를 확인하겠습니다. 준비물이 맞춰지면 필요한 기법만 순서대로 연습할게요."
        )
    else:
        lesson = (
            "아직 코바늘과 대바늘 중 하나를 고를 필요는 없어요. "
            "작고 형태가 또렷한 소품은 코바늘이, 부드럽고 평평한 편물은 대바늘이 잘 맞습니다. "
            "만들고 싶은 작품을 말해 주면 초보자가 완성하기 쉬운 후보부터 보여드릴게요."
        )
    if (
        not state.get("model_reply")
        and
        technique
        and not project_suggestions
        and not (learning_program and CURRICULA[learning_program["curriculum_id"]].written_pattern)
        and (technique.get("reference_videos") or technique.get("reference_video_url"))
    ):
        references = technique.get("reference_videos") or [{
            "url": technique["reference_video_url"],
            "title": technique.get("reference_video_title", "초보 기법 영상"),
            "focus": "",
        }]
        reference_lines = "\n".join(
            f"- [{reference['title']}]({reference['url']})"
            + (f" — {reference['focus']}" if reference.get("focus") else "")
            for reference in references
        )
        lesson += (
            "\n\n**먼저 실제 손동작 보기**\n"
            f"{reference_lines}\n\n"
            "0.5배속으로 왼손의 실 장력, 엄지·중지가 마지막 사슬을 잡는 위치, "
            "코바늘 홈을 아래로 돌려 고리를 통과시키는 순간을 먼저 확인하세요. "
            "핵심 장면 카드는 실제 손동작을 본 뒤 실의 위치와 움직임을 복습할 때 사용합니다."
        )
    if state["artifact_analysis"]:
        lesson += f"\n\n분석 메모: {state['artifact_analysis']}"
    if state["generated_explanation"]:
        lesson += f"\n\n변환된 설명: {state['generated_explanation']}"
    return {"lesson_summary": lesson, "project_suggestions": project_suggestions, "purchase_plan": purchase_plan}


def practice_planner_agent(state: KnitCoachState) -> dict:
    _, technique = _primary_technique_content(state)
    learning_program = state.get("learning_program", {})
    step = current_curriculum_step(learning_program)
    direct_tool_question = is_tool_definition_question(latest_user_text(state))
    technique_support = SupportModule.TECHNIQUE_LIBRARY.value in state.get("support_modules", [])
    if state.get("model_reply") and not technique_support:
        practice_plan = ""
        next_action = ""
    elif direct_tool_question or is_pattern_literacy_request(latest_user_text(state)):
        practice_plan = ""
        next_action = ""
    elif state.get("program_turn") and learning_program and learning_program.get("status") == "shopping":
        practice_plan = ""
        next_action = "먼저 전체 과정을 둘러보거나 구매 목록을 저장해 두세요. 준비한 뒤에는 실 라벨의 권장 mm와 바늘 mm를 맞춰 보고 ‘준비됐어요’라고 알려주세요."
    elif state.get("program_turn") and learning_program and learning_program.get("status") == "awaiting_tools":
        practice_plan = ""
        next_action = "가지고 있는 실의 굵기와 바늘 mm를 알려주세요. 없다면 ‘아무것도 없어요’라고 말해도 괜찮아요."
    elif state.get("program_turn") and step and learning_program.get("status") == "preview":
        practice_plan = ""
        next_action = "아래 **‘다음 단계 미리보기’** 버튼으로 작품 순서를 계속 둘러보세요. 실제 연습 진도에는 기록되지 않습니다."
    elif state.get("program_turn") and step:
        curriculum = CURRICULA[learning_program["curriculum_id"]]
        if curriculum.written_pattern:
            practice_plan = ""
            next_action = "아래 **‘완료하고 다음으로’** 버튼을 누르거나 ‘단계 완료’라고 말해 주세요."
        else:
            practice_plan = step.practice
            next_action = f"성공 기준: {step.success_check} 확인한 뒤 **‘연습 완료’**라고 말해 주세요. 다음 기법으로 진도가 저장됩니다."
    elif state.get("program_turn") and learning_program and learning_program.get("status") == "project_ready":
        practice_plan = ""
        next_action = "제작 중 막히는 단이나 사진을 보내면 현재 가방 도안을 기준으로 이어서 도와드릴게요."
    elif state.get("program_turn") and learning_program and learning_program.get("status") == "preview_complete":
        practice_plan = ""
        next_action = "전체 과정을 모두 둘러봤어요. 준비물이 생기면 ‘준비됐어요’라고 말해 1단부터 실제 진도를 시작하세요."
    elif state["journey"] == JourneyType.START_FROM_ZERO:
        practice_plan = ""
        next_action = "원하는 형태와 크기, 가지고 있는 실과 바늘을 알려주세요."
    elif state["intent"] == "advise_tools":
        practice_plan = ""
        next_action = "실 라벨의 굵기·권장 mm, 만들 작품의 크기, 예산 범위를 알려주면 규격을 더 정확히 좁힐 수 있어요."
    elif state["intent"] == "learn_technique" and technique and (technique_support or not state.get("model_routed")):
        practice_plan = technique["practice"]
        next_action = technique["success_check"]
    elif state["recommended_fixes"]:
        practice_plan = " ".join(state["recommended_fixes"][:2])
        next_action = "같은 구도 사진 1장과 문제 부위 클로즈업 1장을 다시 남겨 변화가 있는지 비교하세요."
    elif state["learning_path"] == "crochet_beginner":
        practice_plan = "사슬 12코를 만들고 짧은뜨기 5단을 떠 보세요. 각 단 끝에서 코 수를 확인합니다."
        next_action = "샘플을 완성한 뒤 가장 조이거나 헐거운 단을 표시하세요."
    elif state["learning_path"] == "needle_knitting_beginner":
        practice_plan = "15코를 잡고 겉뜨기 6단을 떠 보세요. 매 단 끝에서 코 수가 15개인지 확인합니다."
        next_action = "코가 늘어난 단이 몇 번째 단인지 적어 보세요."
    else:
        practice_plan = "가지고 있는 바늘 종류, 만들고 싶은 첫 작품, 하루 연습 가능 시간을 적어 보세요."
        next_action = "코바늘/대바늘 중 가지고 있는 도구와 만들고 싶은 작품을 한 문장으로 정리하세요."
    return {"practice_plan": practice_plan, "next_action": next_action}


def check_understanding_agent(state: KnitCoachState) -> dict:
    _, technique = _primary_technique_content(state)
    learning_program = state.get("learning_program", {})
    step = current_curriculum_step(learning_program)
    direct_tool_question = is_tool_definition_question(latest_user_text(state))
    technique_support = SupportModule.TECHNIQUE_LIBRARY.value in state.get("support_modules", [])
    if state.get("model_follow_up") and not state.get("program_turn"):
        understanding_check = state["model_follow_up"]
    elif state.get("model_reply") and not technique_support:
        understanding_check = ""
    elif direct_tool_question or is_pattern_literacy_request(latest_user_text(state)):
        understanding_check = ""
    elif learning_program and learning_program.get("status") in {"awaiting_tools", "shopping"}:
        understanding_check = state["next_action"]
    elif step:
        understanding_check = state["next_action"]
    elif learning_program and learning_program.get("status") in {"project_ready", "preview_complete"}:
        understanding_check = state["next_action"]
    elif state["journey"] == JourneyType.START_FROM_ZERO:
        if state.get("project_suggestions"):
            understanding_check = "아래 완성 사진을 보고 마음에 드는 작품의 ‘이 작품으로 시작하기’를 눌러 주세요. 선택한 다음 보유 도구와 준비할 재료부터 확인할게요."
        elif state["detected_project_type"] == "가방/bag":
            understanding_check = "먼저 만들고 싶은 가방을 골라 말해 주세요. 선택한 뒤 보유 도구와 준비할 재료부터 함께 확인할게요."
        else:
            understanding_check = "원하는 형태와 크기, 가지고 있는 도구를 확인한 뒤 첫 연습을 정할게요."
    elif state["intent"] == "advise_tools":
        understanding_check = state["next_action"]
    elif state["intent"] == "learn_technique" and technique:
        understanding_check = technique["success_check"]
    elif state["generated_pattern"]:
        understanding_check = "변환된 pattern에서 반복되는 row/round와 필요한 기법을 표시해 보세요."
    elif state.get("image_observation"):
        observation = state["image_observation"]
        understanding_check = (
            observation.get("suggested_actions", [""])[0]
            if observation.get("suggested_actions")
            else "이 사진을 그대로 재현할지, 크기나 용도를 바꿀지 알려주세요."
        )
    elif state["input_type"] == "image_path":
        understanding_check = "사진 분석 기능을 사용할 수 있는 개발 모드를 확인해 주세요."
    elif state["learning_path"] == "crochet_beginner":
        understanding_check = "각 단 끝에서 코 수와 마지막 코 위치를 확인했나요?"
    elif state["learning_path"] == "needle_knitting_beginner":
        understanding_check = "겉뜨기/안뜨기 전환 시 실 위치가 앞뒤로 올바르게 이동했나요?"
    else:
        understanding_check = "작은 소품과 평평한 편물 중 어떤 결과물을 먼저 만들고 싶나요?"
    techniques = ", ".join(state["detected_techniques"]) or "추가 확인 필요"
    if state["intent"] == "convert_pattern":
        response = state["generated_explanation"] or "도안 내용을 쉬운 순서로 정리했습니다."
        if state["generated_pattern"]:
            response += f"\n\n### 도안 초안\n{state['generated_pattern']}"
    elif state["intent"] == "analyze_artifact":
        has_image = bool(state["uploaded_image_path"])
        observation = state.get("image_observation", {})
        if observation:
            response = observation["summary"]
            if observation.get("visible_facts"):
                response += "\n\n### 사진에서 확인한 내용\n" + "\n".join(f"- {item}" for item in observation["visible_facts"])
            if observation.get("construction"):
                response += "\n\n### 보이는 제작 구조\n" + "\n".join(f"- {item}" for item in observation["construction"])
            if observation.get("likely_techniques"):
                response += "\n\n**사진에서 추정되는 기법** · " + " · ".join(observation["likely_techniques"])
            if observation.get("diagnoses"):
                response += "\n\n### 원인 후보\n" + "\n".join(f"- {item}" for item in observation["diagnoses"])
            if observation.get("suggested_actions"):
                response += "\n\n### 먼저 해볼 것\n" + "\n".join(f"- {item}" for item in observation["suggested_actions"])
            if observation.get("uncertainties"):
                response += "\n\n### 사진 한 장으로 확정할 수 없는 부분\n" + "\n".join(f"- {item}" for item in observation["uncertainties"])
            if observation.get("additional_photos"):
                response += "\n\n### 다음 판단에 꼭 필요한 추가 사진\n" + "\n".join(f"- {item}" for item in observation["additional_photos"])
            response += "\n\n이 작품을 재현하는 도안이 필요하면 **‘이 사진으로 도안을 만들어줘’**라고 말해 주세요."
        elif has_image:
            detail = state.get("model_note") or "설정된 모델 provider가 사진 내용을 반환하지 못했습니다."
            response = (
                "사진은 정상적으로 첨부됐지만 현재 응답에서는 이미지 내용을 실제로 읽지 못했습니다. "
                "사진을 본 것처럼 추측하지 않겠습니다.\n\n"
                f"**개발 모드 확인** · {detail}"
            )
            if state["recommended_fixes"] and state["blockers"]:
                response += "\n\n텍스트 설명만으로 먼저 확인할 항목:\n" + "\n".join(f"- {item}" for item in state["recommended_fixes"][:2])
        else:
            response = f"텍스트 설명에서 추정되는 주요 기법은 **{techniques}**입니다."
            if state["photo_findings"]:
                response += "\n\n" + "\n".join(f"- {item}" for item in state["photo_findings"][:3])
            if state["recommended_fixes"]:
                response += "\n\n### 먼저 해볼 것\n" + "\n".join(f"- {item}" for item in state["recommended_fixes"][:2])
            response += "\n\n더 정확히 확인하려면 작품 전체와 문제 부위를 각각 한 장씩 첨부해 주세요."
    else:
        response = state["lesson_summary"]
        if state["practice_plan"]:
            practice_heading = "이번 단계 연습" if step else "짧게 연습해 보기"
            response += f"\n\n### {practice_heading}\n{state['practice_plan']}"
        if understanding_check:
            response += f"\n\n{understanding_check}"
    glossary = []
    if "마커" in response and "표시 고리" not in response:
        glossary.append("마커: 첫 코나 확인할 위치에 거는 작은 표시 고리")
    if "장력" in response and "실을 당기는 힘" not in response:
        glossary.append("장력: 실을 당기며 유지하는 힘")
    if "게이지" in response and "10cm 안의 코와 단 수" not in response:
        glossary.append("게이지: 10cm 안에 들어가는 코와 단 수")
    if "기둥코" in response and "단 높이를 맞추" not in response:
        glossary.append("기둥코: 새 단을 시작할 때 단 높이를 맞추기 위해 먼저 뜨는 사슬코")
    should_add_glossary = (
        state["intent"] == "convert_pattern"
        and state.get("learner_profile", {}).get("level") == "beginner"
    )
    if glossary and should_add_glossary:
        response += "\n\n### 초보 용어 메모\n" + "\n".join(f"- {item}" for item in glossary)
    return {
        "understanding_check": understanding_check,
        "user_response": response,
        "messages": [AIMessage(content=response)],
    }

def reset_turn_state(state: KnitCoachState) -> dict:
    """Clear derived values while preserving conversation memory and the upload input."""
    return {
        "out_of_scope": False,
        "guardrail_reason": "",
        "journey": state.get("journey", JourneyType.START_FROM_ZERO),
        "learner_profile": state.get("learner_profile", {}),
        "input_type": "text",
        "intent": "learn_technique",
        "pattern_draft": {},
        "user_response": "",
        "artifact_source": "",
        "artifact_analysis": "",
        "image_observation": {},
        "model_provider": active_provider_name(),
        "model_note": "",
        "tool_type": state.get("tool_type", "unknown"),
        "pattern_type": "unknown",
        "detected_project_type": state.get("detected_project_type", ""),
        "construction_parts": [],
        "pattern_reference_note": "",
        "detected_techniques": [],
        "difficulty_level": "unknown",
        "difficulty_reasons": [],
        "photo_findings": [],
        "mistake_diagnoses": [],
        "recommended_fixes": [],
        "required_tools": [],
        "required_materials": [],
        "accessories": [],
        "technique_resources": Overwrite([]),
        "tool_findings": "",
        "active_agent": "",
        "conversion_mode": "tutor_only",
        "generated_explanation": "",
        "generated_pattern": "",
        "chart_spec": {},
        "chart_image_path": "",
        "user_feedback": "",
        "goal": state.get("goal", ""),
        "current_skill": "",
        "blockers": [],
        "learning_path": "diagnose_tool",
        "curriculum_stage": "",
        "lesson_summary": "",
        "practice_plan": "",
        "understanding_check": "",
        "next_action": "",
        "project_suggestions": [],
        "purchase_plan": {},
        "program_turn": False,
        "conversation_action": "",
        "support_modules": [],
        "selected_tool_slugs": [],
        "suggested_curriculum_ids": [],
        "model_reply": "",
        "model_follow_up": "",
        "model_routed": False,
        "project_view": "none",
    }


def create_knitcoach(checkpointer=None):
    """Compile the KnitCoach orchestrator-worker graph."""
    graph_builder = StateGraph(KnitCoachState)
    graph_builder.add_node("reset_turn_state", reset_turn_state)
    graph_builder.add_node("classifier_agent", classifier_agent)
    graph_builder.add_node("scope_guardrail_agent", scope_guardrail_agent)
    graph_builder.add_node("pattern_draft_agent", pattern_draft_agent)
    graph_builder.add_node("pattern_response_agent", pattern_response_agent)
    graph_builder.add_node("artifact_analyzer_agent", artifact_analyzer_agent)
    graph_builder.add_node("pattern_converter_agent", pattern_converter_agent)
    graph_builder.add_node("chart_generator_agent", chart_generator_agent)
    graph_builder.add_node("technique_planner_agent", technique_planner_agent)
    graph_builder.add_node("tool_advisor_agent", tool_advisor_agent)
    graph_builder.add_node("technique_scout", technique_scout)
    graph_builder.add_node("resource_agent", resource_agent)
    graph_builder.add_node("resource_tools", ToolNode(KNITCOACH_TOOLS))
    graph_builder.add_node("teacher_agent", teacher_agent)
    graph_builder.add_node("practice_planner_agent", practice_planner_agent)
    graph_builder.add_node("check_understanding_agent", check_understanding_agent)

    graph_builder.add_edge(START, "reset_turn_state")
    graph_builder.add_edge("reset_turn_state", "classifier_agent")
    graph_builder.add_conditional_edges(
        "classifier_agent",
        route_by_intent,
        {
            "scope_guardrail_agent": "scope_guardrail_agent",
            "pattern_draft_agent": "pattern_draft_agent",
            "artifact_analyzer_agent": "artifact_analyzer_agent",
            "pattern_converter_agent": "pattern_converter_agent",
            "technique_planner_agent": "technique_planner_agent",
        },
    )
    graph_builder.add_edge("scope_guardrail_agent", END)
    graph_builder.add_edge("pattern_draft_agent", "pattern_response_agent")
    graph_builder.add_edge("pattern_response_agent", END)
    graph_builder.add_edge("artifact_analyzer_agent", "technique_planner_agent")
    graph_builder.add_edge("pattern_converter_agent", "chart_generator_agent")
    graph_builder.add_edge("chart_generator_agent", "technique_planner_agent")
    graph_builder.add_edge("technique_planner_agent", "tool_advisor_agent")
    graph_builder.add_conditional_edges(
        "tool_advisor_agent",
        fan_out_techniques,
        ["technique_scout", "resource_agent"],
    )
    graph_builder.add_edge("technique_scout", "resource_agent")
    graph_builder.add_conditional_edges(
        "resource_agent",
        tools_condition,
        {"tools": "resource_tools", END: "teacher_agent"},
    )
    graph_builder.add_edge("resource_tools", "resource_agent")
    graph_builder.add_edge("teacher_agent", "practice_planner_agent")
    graph_builder.add_edge("practice_planner_agent", "check_understanding_agent")
    graph_builder.add_edge("check_understanding_agent", END)
    return graph_builder.compile(checkpointer=checkpointer or MemorySaver())


knitcoach = create_knitcoach()


def initial_state(user_text: str, image_path: str | None = None) -> KnitCoachState:
    return {
        "messages": [HumanMessage(content=user_text)],
        "out_of_scope": False,
        "guardrail_reason": "",
        "journey": JourneyType.START_FROM_ZERO,
        "learner_profile": {},
        "input_type": "text",
        "intent": "learn_technique",
        "task": "tutor",
        "pattern_options": {},
        "pattern_draft": {},
        "original_image_name": "",
        "user_response": "",
        "artifact_source": "",
        "uploaded_image_path": image_path or "",
        "artifact_analysis": "",
        "image_observation": {},
        "model_provider": active_provider_name(),
        "model_note": "",
        "tool_type": "unknown",
        "pattern_type": "unknown",
        "detected_project_type": "",
        "construction_parts": [],
        "pattern_reference_note": "",
        "detected_techniques": [],
        "difficulty_level": "unknown",
        "difficulty_reasons": [],
        "photo_findings": [],
        "mistake_diagnoses": [],
        "recommended_fixes": [],
        "required_tools": [],
        "required_materials": [],
        "accessories": [],
        "technique_resources": [],
        "active_agent": "",
        "conversion_mode": "tutor_only",
        "generated_explanation": "",
        "generated_pattern": "",
        "chart_spec": {},
        "chart_image_path": "",
        "user_feedback": "",
        "goal": "",
        "current_skill": "",
        "blockers": [],
        "learning_path": "diagnose_tool",
        "curriculum_stage": "",
        "lesson_summary": "",
        "practice_plan": "",
        "understanding_check": "",
        "next_action": "",
        "tool_findings": "",
        "learning_program": {},
        "program_turn": False,
        "conversation_action": "",
        "support_modules": [],
        "selected_tool_slugs": [],
        "suggested_curriculum_ids": [],
        "model_reply": "",
        "model_follow_up": "",
        "model_routed": False,
        "project_view": "none",
        "project_suggestions": [],
        "purchase_plan": {},
    }


def invoke_turn(
    agent,
    user_text: str,
    thread_id: str,
    image_path: str | None = None,
    *,
    task: Literal["tutor", "generate_pattern"] = "tutor",
    pattern_options: dict | None = None,
    original_image_name: str = "",
    learning_program: dict | None = None,
) -> KnitCoachState:
    """Run one user turn while keeping graph memory isolated by thread ID."""
    payload = {
        "messages": [HumanMessage(content=user_text)],
        "uploaded_image_path": image_path or "",
        "task": task,
        "pattern_options": pattern_options or {},
        "original_image_name": original_image_name,
    }
    if learning_program is not None:
        payload["learning_program"] = learning_program
    config = {"configurable": {"thread_id": thread_id}}
    return agent.invoke(payload, config=config)


def run_example(user_text: str, thread_id: str | None = None) -> None:
    # checkpointer가 붙어 있으므로 invoke마다 thread_id가 필요하다.
    # 데모마다 새 thread_id를 써서 서로 상태가 섞이지 않게 한다.
    result = invoke_turn(knitcoach, user_text, thread_id or uuid.uuid4().hex)
    print("USER:", user_text)
    print("INTENT:", result["intent"])
    print("ACTIVE_AGENT:", result["active_agent"])
    print("INPUT_TYPE:", result["input_type"])
    print("PATH:", result["learning_path"])
    print("PROJECT:", result["detected_project_type"])
    print("DIFFICULTY:", result["difficulty_level"])
    print("TECHNIQUES:", result["detected_techniques"])
    print("RESOURCES:", [r.get("technique") for r in result["technique_resources"]])
    print("TOOLS:", result["required_tools"])
    if result.get("tool_findings"):
        print("TOOL_FINDINGS:", result["tool_findings"])
    print("ASSISTANT:", result["messages"][-1].content)
    print("-" * 80)


def run_conversation(turns: list[str], thread_id: str = "memory-demo") -> None:
    """같은 thread_id로 여러 턴을 이어 실행해 checkpointer 메모리를 시연한다.

    첫 턴만 전체 initial_state를 넣고, 이후 턴은 새 사용자 메시지만 전달한다.
    checkpointer가 이전 상태(messages 등)를 복원하므로 대화가 누적된다.
    """
    for i, turn in enumerate(turns):
        result = invoke_turn(knitcoach, turn, thread_id)
        print(f"[turn {i + 1}] USER:", turn)
        print(f"[turn {i + 1}] 누적 메시지 수:", len(result["messages"]))
        print(f"[turn {i + 1}] ASSISTANT:", str(result["messages"][-1].content)[:300], "...")
        print("-" * 80)
