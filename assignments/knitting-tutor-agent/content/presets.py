"""Starter presets for the pattern studio.

Each preset pre-fills the pattern form with sensible, non-empty defaults so a
beginner isn't faced with blank required fields. Every value is editable in the
UI, and always non-empty so the agent's PatternRequest validation passes.

`sample=True` maps to the offline sample bag (samples/crochet-mesh-shoulder-bag.png),
the only project that produces a deterministic draft without an API key.
"""

PROJECT_PRESETS: dict[str, dict] = {
    "코스터 (초보)": {
        "tool_type": "crochet",
        "finished_size": "지름 10cm 원형",
        "yarn_weight": "worsted 면사",
        "tool_size": "코바늘 5mm",
        "gauge": "10cm = 16코 × 12단",
        "skill_level": "beginner",
        "sample": False,
    },
    "네트 숄더백 (샘플·오프라인)": {
        "tool_type": "crochet",
        "finished_size": "가로 28cm × 세로 24cm",
        "yarn_weight": "worsted 면사",
        "tool_size": "코바늘 5mm",
        "gauge": "미측정",
        "skill_level": "intermediate",
        "sample": True,
    },
    "목도리 (초보)": {
        "tool_type": "needle_knitting",
        "finished_size": "가로 18cm × 길이 120cm",
        "yarn_weight": "worsted 울",
        "tool_size": "대바늘 6mm",
        "gauge": "미측정",
        "skill_level": "beginner",
        "sample": False,
    },
    "비니 모자": {
        "tool_type": "needle_knitting",
        "finished_size": "머리둘레 54cm",
        "yarn_weight": "worsted 울",
        "tool_size": "대바늘 5mm",
        "gauge": "미측정",
        "skill_level": "confident_beginner",
        "sample": False,
    },
    "직접 입력": {
        "tool_type": "crochet",
        "finished_size": "가로 20cm × 세로 20cm",
        "yarn_weight": "worsted 면사",
        "tool_size": "코바늘 5mm",
        "gauge": "미측정",
        "skill_level": "beginner",
        "sample": False,
    },
}

PRESET_NAMES: list[str] = list(PROJECT_PRESETS)
DEFAULT_PRESET = "코스터 (초보)"
