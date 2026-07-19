"""Data-driven first-purchase plans for the curated beginner projects."""

from copy import deepcopy

from content.tools import TOOL_IMAGE_PATHS, get_tool
from domain.curricula import CURRICULA


STORE_GUIDES = [
    {
        "name": "다이소·가까운 생활용품점",
        "best_for": "코바늘 한 개, 표시링, 돗바늘, 가위처럼 먼저 시험할 기본 도구",
        "note": "지점마다 규격과 재고가 달라요. 바늘 몸통의 mm를 확인하고, 없으면 억지로 비슷한 규격을 사지 마세요.",
        "url": "https://www.daisomall.co.kr/",
    },
    {
        "name": "바늘이야기",
        "best_for": "실과 정확한 규격의 바늘을 함께 고르고 싶을 때",
        "note": "실 상세 페이지의 권장 바늘 mm와 필요 수량을 먼저 확인하세요.",
        "url": "https://www.banul.co.kr/",
    },
    {
        "name": "쎄비",
        "best_for": "뜨개실·바늘·키링 고리 같은 부자재를 한곳에서 비교할 때",
        "note": "색상보다 실 굵기와 권장 바늘 mm를 먼저 맞추세요.",
        "url": "https://www.sevy.co.kr/",
    },
]


PROJECT_PURCHASE_SPECS = {
    "crochet-round-coaster": {
        "yarn": {
            "name": "밝은 단색의 중간 굵기 면사",
            "quantity": "작품에는 약 20g · 50g 1볼이면 충분",
            "check": "4번 중간 굵기 · 라벨에 코바늘 4mm 안팎이 권장된 실",
            "avoid": "검정색·털이 긴 실·수세미실은 첫 코를 보기 어려워요.",
        },
        "needle_spec": "4.0mm 기본 코바늘 1개 · 게이지가 너무 빡빡하면 4.5mm",
        "tool_slugs": ["single-crochet-hook", "stitch-markers", "tapestry-needle", "scissors"],
        "extras": [],
    },
    "crochet-mini-hat-keyring": {
        "yarn": {"name": "밝은 단색 3번 DK 면사", "quantity": "작품에는 약 15g · 자투리실도 가능", "check": "라벨 권장 코바늘 3.5mm 안팎", "avoid": "어두운색·복슬한 실은 코 위치를 보기 어려워요."},
        "needle_spec": "3.5mm 기본 코바늘 1개",
        "tool_slugs": ["single-crochet-hook", "stitch-markers", "tapestry-needle", "scissors", "project-notions"],
        "extras": ["키링 고리 1개"],
    },
    "crochet-fishbread-keyring": {
        "yarn": {"name": "밝은색 3번 DK 면사 + 비늘·눈용 자투리실", "quantity": "본체 약 10–15g + 자수용 실 약 1m", "check": "라벨 권장 코바늘 3.0–3.5mm 안팎", "avoid": "솜이 비치는 느슨한 조직과 털이 긴 실은 피하세요."},
        "needle_spec": "3.0–3.5mm 기본 코바늘 1개 · 솜이 비치면 0.5mm 작은 쪽",
        "tool_slugs": ["single-crochet-hook", "stitch-markers", "tapestry-needle", "scissors", "project-notions"],
        "extras": ["키링 고리 1개", "충전솜 소량"],
    },
    "crochet-flat-pouch": {
        "yarn": {"name": "밝은 단색 4번 중간 굵기 면사", "quantity": "80–100g", "check": "라벨 권장 코바늘 4mm 안팎", "avoid": "너무 늘어지는 실은 첫 파우치 형태를 잡기 어려워요."},
        "needle_spec": "4.0mm 기본 코바늘 1개 · 18코/10cm 게이지 확인",
        "tool_slugs": ["single-crochet-hook", "stitch-markers", "tapestry-needle", "scissors", "measure-gauge"],
        "extras": ["조임끈은 같은 실로 만들 수 있어요."],
    },
    "needle-garter-scarf": {
        "yarn": {"name": "밝은 두 색의 5번 굵은 실", "quantity": "두 색 합계 220m 이상", "check": "라벨 권장 대바늘 6–7mm 안팎", "avoid": "검정색·모헤어처럼 코가 묻히는 실은 피하세요."},
        "needle_spec": "6.5mm 직선 대바늘 또는 60cm 줄바늘 · 몇 단 뜬 뒤 18코 폭이 13–15cm인지 확인",
        "tool_slugs": ["straight-needles", "tapestry-needle", "scissors", "measure-gauge"],
        "extras": [],
    },
    "needle-ribbed-muffler": {
        "yarn": {"name": "밝은 단색 4번 중간 굵기 울 혼방실", "quantity": "같은 로트 합계 350–400m", "check": "라벨 권장 대바늘 5mm 안팎", "avoid": "첫 고무뜨기에는 질감이 복잡한 실보다 코가 선명한 실이 좋아요."},
        "needle_spec": "5.0mm 직선 대바늘 또는 60cm 줄바늘 · 20코/10cm 골지 게이지 확인",
        "tool_slugs": ["straight-needles", "stitch-markers", "tapestry-needle", "scissors", "measure-gauge"],
        "extras": [],
    },
}


def build_purchase_plan(curriculum_id: str) -> dict:
    """Combine project-specific specs with the canonical tool catalog."""
    curriculum = CURRICULA[curriculum_id]
    spec = deepcopy(PROJECT_PURCHASE_SPECS.get(curriculum_id, {}))
    if not spec:
        crochet = curriculum.tool_type == "crochet"
        spec = {
            "yarn": {"name": curriculum.starter_kit[0], "quantity": "작품 1개 분량", "check": "실 라벨의 권장 바늘 mm", "avoid": "첫 작품은 코가 잘 보이는 밝은 단색이 편해요."},
            "needle_spec": curriculum.starter_kit[1],
            "tool_slugs": (["single-crochet-hook"] if crochet else ["straight-needles"]) + ["stitch-markers", "tapestry-needle", "scissors", "measure-gauge"],
            "extras": [],
        }
    tools = []
    for index, slug in enumerate(spec.pop("tool_slugs")):
        tool = get_tool(slug)
        if not tool:
            continue
        tools.append({
            "slug": slug,
            "name": tool.name,
            "spec": spec["needle_spec"] if index == 0 else tool.budget_choice,
            "image": TOOL_IMAGE_PATHS.get(slug, ""),
            "required": index < 4,
        })
    return {
        "curriculum_id": curriculum_id,
        "title": curriculum.title,
        "outcome": curriculum.outcome,
        "cover_image": curriculum.cover_image,
        "yarn": spec["yarn"],
        "tools": tools,
        "extras": spec.get("extras", []),
        "stores": deepcopy(STORE_GUIDES),
        "project_guide": curriculum.project_guide,
        "written_pattern": curriculum.written_pattern,
        "beginner_pattern": curriculum.beginner_pattern or curriculum.written_pattern,
        "pattern_format": curriculum.pattern_format,
        "yarn_requirement": curriculum.yarn_requirement,
        "needle_size": curriculum.needle_size,
        "gauge": curriculum.gauge,
        "finished_size": curriculum.finished_size,
        "construction": curriculum.construction,
        "reference_video_url": curriculum.reference_video_url,
        "reference_video_title": curriculum.reference_video_title,
        "symbol_legend": curriculum.symbol_legend,
        "techniques": curriculum.pattern_techniques or list(dict.fromkeys(step.technique.split("(")[0].strip() for step in curriculum.steps)),
    }
