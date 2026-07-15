"""Reusable LangGraph core for the KnitCoach Streamlit application."""


import base64
import mimetypes
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
from pydantic import BaseModel, Field

from content.techniques import TECHNIQUE_CATALOG, TECHNIQUES, resolve_techniques

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = os.getenv("KNITTING_AGENT_MODEL", "gpt-4.1-mini")
HAS_OPENAI_KEY = bool(os.getenv("OPENAI_API_KEY"))
ENABLE_VISION = os.getenv("KNITCOACH_ENABLE_VISION") == "1"
DEBUG_MODE = os.getenv("KNITCOACH_DEBUG") == "1"


class PatternRequest(BaseModel):
    tool_type: Literal["auto", "crochet", "needle_knitting"] = "auto"
    finished_size: str = Field(min_length=1)
    yarn_weight: str = Field(min_length=1)
    tool_size: str = Field(min_length=1)
    gauge: str = "미측정"
    skill_level: Literal["beginner", "confident_beginner", "intermediate"] = "beginner"
    notes: str = ""


class PatternDraft(BaseModel):
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
    additional_photos: list[str] = Field(default_factory=list)


class KnitCoachState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
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


CROCHET_KEYWORDS = {
    "코바늘", "crochet", "사슬", "사슬뜨기", "짧은뜨기", "긴뜨기", "빼뜨기", "모티브", "원형뜨기", "컵받침",
    "매직링", "magic ring", "한길긴뜨기", "네트", "망사", "mesh", "shoulder-bag", "ch", "sc", "dc", "sl st", "mr", "amigurumi", "아미구루미"
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
TOOL_QUESTION_KEYWORDS = {"호수", "부자재", "굵기", "제품", "추천", "몇 호", "몇호", "재료"}
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
    "원형뜨기": "5. 원형뜨기에서 늘림 위치 익히기",
}
NEEDLE_CURRICULUM = {
    "코 잡기": "1. 코를 일정한 간격으로 잡기",
    "겉뜨기": "2. 겉뜨기로 garter stitch 만들기",
    "안뜨기": "3. 안뜨기와 겉뜨기 방향 구분하기",
    "고무뜨기": "4. 겉뜨기/안뜨기 반복으로 ribbing 만들기",
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
            "원형뜨기(round crochet)",
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
    chain_count = 12
    row_count = 5
    ch_match = re.search(r"ch\s*(\d+)", lowered)
    if ch_match:
        chain_count = int(ch_match.group(1))
    # 숫자가 마커 앞("5 rows")이든 뒤("rows 5")이든 잡는다.
    row_match = re.search(r"(\d+)\s*rows?\b", lowered) or re.search(r"\brows?\s*(\d+)", lowered)
    if row_match:
        row_count = int(row_match.group(1))
    return (
        f"초보자 설명:\n"
        f"1. 사슬뜨기 {chain_count}코를 만들어 시작합니다.\n"
        f"2. 다음 단부터는 각 사슬코 위에 짧은뜨기를 1번씩 떠서 끝까지 갑니다.\n"
        f"3. 한 단이 끝나면 사슬 1코를 올리고 편물을 돌립니다.\n"
        f"4. 짧은뜨기 단을 총 {row_count}단 반복합니다.\n"
        f"5. 매 단 끝에서 코 수가 {chain_count}코인지 확인합니다.\n"
        f"6. 가장자리가 줄어들지 않게 첫 코와 마지막 코를 빠뜨리지 마세요."
    )


def row_by_row_pattern_from_text(text: str) -> str:
    lowered = normalize_text(text)
    chain_match = re.search(r"(?:사슬|ch)\s*(\d+)", lowered)
    row_match = re.search(r"(\d+)\s*단", lowered) or re.search(r"(\d+)\s*rows?", lowered)
    if not chain_match or not row_match:
        return "시작 코 수와 반복 단 수가 입력에 없어 확정 도안을 만들 수 없습니다. 원하는 크기와 게이지를 알려주세요."
    chain_count = int(chain_match.group(1))
    row_count = int(row_match.group(1))
    return (
        f"1단: 사슬 {chain_count}코.\n"
        f"2–{row_count}단: 각 코에 짧은뜨기 1코, 사슬 1코 후 뒤집기.\n"
        "마무리: 마지막 코를 정리하고 실 끝을 돗바늘로 숨깁니다."
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
    if input_type in {"image_path", "link"} or any(word in text for word in ["분석", "완성품", "사진", "이미지", "난이도"]):
        return "analyze_artifact"
    if input_type in {"pattern_text", "explanation_text"} or any(word in text for word in ["설명글", "도안으로", "변환", "chart", "차트"]):
        return "convert_pattern"
    return "learn_technique"


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
    mapping = {"컵받침": "컵받침/coaster", "coaster": "컵받침/coaster", "목도리": "목도리/scarf", "scarf": "목도리/scarf", "가방": "가방/bag", "bag": "가방/bag", "모자": "모자/hat", "hat": "모자/hat", "비니": "모자/hat", "인형": "아미구루미/amigurumi", "amigurumi": "아미구루미/amigurumi", "도안": "도안/pattern", "chart": "차트 도안/chart"}
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
        techniques.append("코 잡기(casting on)")
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
    if "코가 빠짐" in blockers or "의도하지 않은 구멍" in blockers:
        diagnoses.append("중간에 코를 놓쳤거나 실 위치가 앞뒤로 잘못 이동했을 가능성이 있습니다.")
        fixes.append("문제가 생긴 줄 바로 아래 안정된 줄까지 확인하고, 마커로 위치를 표시한 뒤 한 코씩 복구합니다.")
    if "편물이 말림" in blockers or "가장자리 휘어짐" in blockers:
        diagnoses.append("단 끝 코 누락, 기둥코 처리, 또는 장력 차이 때문에 가장자리가 틀어질 수 있습니다.")
        fixes.append("각 단 마지막 코를 세고, 단 시작/끝에 마커를 걸어 빠뜨린 코가 없는지 확인합니다.")
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
    if tool_type == "crochet":
        tools = ["코바늘: 실 라벨 권장 호수를 우선 확인", "초보 샘플: 4/0-6/0 코바늘 또는 3.0-4.0mm 범위부터 테스트"]
        materials = ["면사 또는 아크릴 중간 굵기: 코 모양이 잘 보여 초보 연습에 적합", "가방/소품은 형태 유지를 위해 너무 흐물거리지 않는 실 선택"]
        accessories = ["단수링/마커", "돗바늘", "가위", "줄자"]
        if any("매직링" in t or "원형뜨기" in t for t in techniques):
            accessories.append("원형 시작점 표시용 잠금 마커")
        if "가방" in project_type:
            accessories.extend(["가방 손잡이 또는 D링", "안감 선택 사항"])
    elif tool_type == "needle_knitting":
        tools = ["대바늘: 실 라벨 권장 mm를 우선 확인", "목도리/평면 샘플: 4.0-5.5mm 직선바늘 또는 줄바늘로 시작"]
        materials = ["밝은 단색 중간 굵기 실: 겉뜨기/안뜨기 구분이 쉽습니다.", "게이지가 중요한 의류는 반드시 10cm 샘플을 먼저 뜹니다."]
        accessories = ["코수 마커", "돗바늘", "가위", "줄자", "단수 카운터 선택 사항"]
    else:
        tools = ["코바늘/대바늘 중 작품 목표에 맞춰 선택: 작은 소품은 코바늘, 평면 반복 편물은 대바늘이 쉽습니다."]
        materials = ["처음에는 밝은 단색 중간 굵기 실을 선택하세요."]
        accessories = ["마커", "돗바늘", "가위", "줄자"]
    return tools, materials, accessories


def build_technique_resources(techniques: list[str]) -> list[dict]:
    resources = []
    for technique in techniques:
        item = TECHNIQUE_CATALOG.get(technique)
        if item:
            resources.append({"technique": technique, **item})
    return resources


def maybe_vision_analysis(image_path: str) -> str:
    if not (ENABLE_VISION and HAS_OPENAI_KEY):
        return ""
    path = Path(image_path)
    if not path.exists() or not path.is_file():
        return ""
    try:
        from langchain_openai import ChatOpenAI
        mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
        image_data = base64.b64encode(path.read_bytes()).decode("utf-8")
        model = ChatOpenAI(model=MODEL_NAME, temperature=0)
        response = model.invoke([
            HumanMessage(content=[
                {"type": "text", "text": "뜨개 작품/도안 이미지를 보고 기법, 난이도, 문제 가능 지점, 필요한 도구를 한국어 bullet로 분석해줘."},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}},
            ])
        ])
        return str(response.content)
    except Exception as exc:
        return f"vision 분석을 시도했지만 fallback으로 전환했습니다: {exc.__class__.__name__}"


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
        techniques=["사슬뜨기", "빼뜨기", "한길긴뜨기", "원형뜨기와 늘림"],
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


def vision_pattern_draft(image_path: str, request: PatternRequest) -> PatternDraft:
    """Create a structured, explicitly provisional pattern from one reference image."""
    from langchain_openai import ChatOpenAI

    path = Path(image_path)
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    image_data = base64.b64encode(path.read_bytes()).decode("utf-8")
    model = ChatOpenAI(model=MODEL_NAME, temperature=0).with_structured_output(PatternDraft)
    prompt = (
        "너는 뜨개 도안 설계자다. 첨부 이미지를 관찰하고 사용자의 제작 조건에 맞는 한국어 텍스트 도안 초안을 작성하라. "
        "사진에서 보이지 않는 코 수, 뒷면 구조, 게이지를 확정적으로 말하지 말고 assumptions에 기록하라. "
        "instructions는 초보자가 시험 샘플을 만들 수 있는 row/round 순서로 작성하라. "
        f"사용자 조건: {request.model_dump_json()}"
    )
    return model.invoke([
        HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}},
        ])
    ])


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
        if ENABLE_VISION and HAS_OPENAI_KEY:
            draft = vision_pattern_draft(image_path, request)
        elif is_sample:
            draft = sample_bag_pattern(request)
        else:
            response = (
                "이 이미지에서 실제 도안 초안을 만들려면 `OPENAI_API_KEY`와 "
                "`KNITCOACH_ENABLE_VISION=1` 설정이 필요합니다. 지금은 임의 이미지를 추측해 도안을 만들지 않습니다."
            )
            return {"active_agent": "pattern_draft_agent", "pattern_draft": {}, "user_response": response}
    except Exception as exc:
        response = f"이미지 도안 분석을 완료하지 못했습니다. 설정과 이미지를 확인해 주세요. ({exc.__class__.__name__})"
        return {"active_agent": "pattern_draft_agent", "pattern_draft": {}, "user_response": response}

    return {
        "active_agent": "pattern_draft_agent",
        "pattern_draft": draft.model_dump(),
        "tool_type": draft.tool_type,
        "detected_techniques": draft.techniques,
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
    input_type = "image_path" if state["uploaded_image_path"] else detect_input_type(text)
    tool_type = detect_tool_type(text)
    current_skill = detect_current_skill(text, tool_type)
    pattern_request_words = ["도안 만들어", "도안을 만들어", "도안으로", "패턴 만들어", "pattern 만들어"]
    wants_image_pattern = state["task"] == "generate_pattern" or (
        bool(state["uploaded_image_path"]) and any(word in text.lower() for word in pattern_request_words)
    )
    intent = "generate_pattern" if wants_image_pattern else detect_intent(text, input_type)
    learner_level = "beginner" if any(word in text for word in ["처음", "초보", "입문"]) else "unknown"
    learner_profile = {"level": learner_level, "preferred_style": "hands_on" if "연습" in text else "unknown", "goal": detect_goal(text, tool_type)}
    techniques = detect_techniques(text, tool_type, current_skill)
    sample_reference = get_sample_reference(text)
    if sample_reference:
        techniques = merge_unique(techniques, sample_reference["techniques"])
        tool_type = sample_reference["tool_type"]
    tool_type = infer_tool_type_from_techniques(tool_type, techniques)
    return {
        "input_type": input_type,
        "intent": intent,
        "artifact_source": state["uploaded_image_path"] or text,
        "tool_type": tool_type,
        "learner_profile": learner_profile,
        "goal": learner_profile["goal"],
        "current_skill": current_skill,
        "blockers": detect_blockers(text),
        "detected_project_type": sample_reference.get("project_type", detect_project_type(text)),
        "construction_parts": sample_reference.get("construction_parts", []),
        "pattern_reference_note": sample_reference.get("pattern_reference_note", ""),
        "pattern_type": detect_pattern_type(text, input_type),
        "detected_techniques": techniques,
        "user_feedback": text if intent == "revise_output" else "",
    }


def route_by_intent(state: KnitCoachState) -> str:
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
    difficulty_level, difficulty_reasons = infer_difficulty(pattern_type, project_type, techniques, state["blockers"])
    photo_findings, mistake_diagnoses, recommended_fixes = build_photo_findings(text, pattern_type, techniques, state["blockers"])
    sample_reference = get_sample_reference(text)
    if sample_reference:
        difficulty_level = sample_reference["difficulty_level"]
        difficulty_reasons = merge_unique(difficulty_reasons, sample_reference["difficulty_reasons"])
        photo_findings = merge_unique(photo_findings, sample_reference["photo_findings"])
        mistake_diagnoses = merge_unique(mistake_diagnoses, sample_reference["mistake_diagnoses"])
        recommended_fixes = merge_unique(recommended_fixes, sample_reference["recommended_fixes"])
    vision_note = ""
    if state["input_type"] == "image_path":
        image_path = state["uploaded_image_path"] or state["artifact_source"]
        vision_note = maybe_vision_analysis(image_path)
    if pattern_type in {"photo", "finished_object"}:
        analysis = "완성품/사진 입력을 기준으로 작품 유형, 기법, 난이도, 문제 가능 지점을 분석했습니다."
    elif pattern_type in {"symbol_chart", "diagram_chart", "written_pattern"}:
        analysis = "도안 입력을 기준으로 반복 구조, 필요한 기법, 초보자가 막힐 지점을 분석했습니다."
    else:
        analysis = "사용자 설명을 기준으로 필요한 기법과 학습 순서를 분석했습니다."
    if vision_note:
        analysis += f"\nVision note: {vision_note}"
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
        "construction_parts": sample_reference.get("construction_parts", state["construction_parts"]),
        "pattern_reference_note": sample_reference.get("pattern_reference_note", state["pattern_reference_note"]),
    }


def pattern_converter_agent(state: KnitCoachState) -> dict:
    text = latest_user_text(state)
    lowered = normalize_text(text)
    should_convert = state["intent"] in {"convert_pattern", "revise_output"} or state["input_type"] in {"pattern_text", "explanation_text"}
    if not should_convert:
        return {}
    if state["input_type"] == "pattern_text" or has_pattern_abbrev(lowered):
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
    techniques = list(state["detected_techniques"])
    if not techniques and state["learning_path"] == "crochet_beginner":
        techniques = ["사슬뜨기(chain stitch)", "짧은뜨기(single crochet)"]
    elif not techniques and state["learning_path"] == "needle_knitting_beginner":
        techniques = ["코 잡기(casting on)", "겉뜨기(knit stitch)"]
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
    for name in state["detected_techniques"]:
        item = TECHNIQUE_CATALOG.get(name)
        if item:
            return name, item
    return None, None


def teacher_agent(state: KnitCoachState) -> dict:
    techniques = ", ".join(state["detected_techniques"]) if state["detected_techniques"] else state["current_skill"]
    blockers = ", ".join(state["blockers"]) if state["blockers"] else "아직 뚜렷한 막힘은 없음"
    difficulty = state["difficulty_level"]
    reasons = "; ".join(state["difficulty_reasons"]) if state["difficulty_reasons"] else "난이도 판단 근거가 아직 부족합니다."
    technique_name, technique = _primary_technique_content(state)
    if state["intent"] == "learn_technique" and technique:
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
    elif state["learning_path"] == "crochet_beginner":
        lesson = f"코바늘(crochet) 분석입니다. 작품 유형은 {state['detected_project_type']}이고, 감지된 기법은 {techniques}입니다. 난이도는 {difficulty}로 판단했습니다. 이유: {reasons}. 실을 너무 세게 당기지 말고, 바늘이 코 안을 편하게 지나갈 정도의 장력을 유지하세요. 현재 blocker: {blockers}."
    elif state["learning_path"] == "needle_knitting_beginner":
        lesson = f"대바늘(needle knitting) 분석입니다. 작품 유형은 {state['detected_project_type']}이고, 감지된 기법은 {techniques}입니다. 난이도는 {difficulty}로 판단했습니다. 이유: {reasons}. 바늘 끝이 아니라 몸통 부분에서 코 크기를 맞추고, 매 단 끝에서 코 수를 확인하세요. 현재 blocker: {blockers}."
    else:
        lesson = f"아직 코바늘/대바늘 path가 확정되지 않았습니다. 작품 유형은 {state['detected_project_type']}로 보이며, 작은 소품이나 모티브를 빨리 만들고 싶다면 코바늘, 목도리처럼 평평한 편물을 반복하고 싶다면 대바늘이 적합합니다."
    if state["artifact_analysis"]:
        lesson += f"\n\n분석 메모: {state['artifact_analysis']}"
    if state["generated_explanation"]:
        lesson += f"\n\n변환된 설명: {state['generated_explanation']}"
    return {"lesson_summary": lesson}


def practice_planner_agent(state: KnitCoachState) -> dict:
    _, technique = _primary_technique_content(state)
    if state["intent"] == "learn_technique" and technique:
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
    if state["intent"] == "learn_technique" and technique:
        understanding_check = technique["success_check"]
    elif state["generated_pattern"]:
        understanding_check = "변환된 pattern에서 반복되는 row/round와 필요한 기법을 표시해 보세요."
    elif state["input_type"] == "image_path":
        understanding_check = "다음 사진은 전체 정면, 단 끝 클로즈업, 문제 부위 클로즈업 순서로 찍어 주세요."
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
        response = f"사진에서 확인되는 주요 기법은 **{techniques}**입니다."
        if state["photo_findings"]:
            response += "\n\n" + "\n".join(f"- {item}" for item in state["photo_findings"][:3])
        if state["recommended_fixes"]:
            response += "\n\n### 먼저 해볼 것\n" + "\n".join(f"- {item}" for item in state["recommended_fixes"][:2])
        response += "\n\n이 작품을 재현하는 도안이 필요하면 ‘이 사진으로 도안을 만들어줘’라고 말해 주세요."
    else:
        response = state["lesson_summary"]
        if state["practice_plan"]:
            response += f"\n\n### 짧게 연습해 보기\n{state['practice_plan']}"
        response += f"\n\n{understanding_check}"
    return {
        "understanding_check": understanding_check,
        "user_response": response,
        "messages": [AIMessage(content=response)],
    }

def reset_turn_state(_: KnitCoachState) -> dict:
    """Clear derived values while preserving conversation memory and the upload input."""
    return {
        "learner_profile": {},
        "input_type": "text",
        "intent": "learn_technique",
        "pattern_draft": {},
        "user_response": "",
        "artifact_source": "",
        "artifact_analysis": "",
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
        "technique_resources": Overwrite([]),
        "tool_findings": "",
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
    }


def create_knitcoach(checkpointer=None):
    """Compile the KnitCoach orchestrator-worker graph."""
    graph_builder = StateGraph(KnitCoachState)
    graph_builder.add_node("reset_turn_state", reset_turn_state)
    graph_builder.add_node("classifier_agent", classifier_agent)
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
            "pattern_draft_agent": "pattern_draft_agent",
            "artifact_analyzer_agent": "artifact_analyzer_agent",
            "pattern_converter_agent": "pattern_converter_agent",
            "technique_planner_agent": "technique_planner_agent",
        },
    )
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
) -> KnitCoachState:
    """Run one user turn while keeping graph memory isolated by thread ID."""
    payload = {
        "messages": [HumanMessage(content=user_text)],
        "uploaded_image_path": image_path or "",
        "task": task,
        "pattern_options": pattern_options or {},
        "original_image_name": original_image_name,
    }
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
