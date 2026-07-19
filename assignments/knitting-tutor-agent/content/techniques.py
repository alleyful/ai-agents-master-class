"""Knitting/crochet technique content.

Single source of truth shared by the agent core (`knitcoach.py`) and the
Streamlit UI (`views/techniques.py`, `views/home.py`).

- `TECHNIQUE_CATALOG` keeps the original plain-dict shape so the agent logic
  (`knitcoach.py`) that reads `catalog.get(name, {}).get("tool_type")` needs no
  change. `steps` and `mistake_fixes` are EXTRA keys the agent ignores.
- `Technique` / `TECHNIQUES` / `list_techniques()` / `get_technique()` provide a
  validated, typed view for the UI so pages never hardcode technique text.
"""

import re
from typing import Literal

from pydantic import BaseModel, Field

ToolType = Literal["crochet", "needle_knitting"]
Difficulty = Literal["beginner", "confident_beginner", "intermediate"]
Category = Literal["basics", "shaping", "texture", "construction", "finishing"]
SymbolKind = Literal["standard", "modifier", "learning"]


class Technique(BaseModel):
    """A single knitting/crochet technique entry."""

    name: str
    tool_type: ToolType
    difficulty: Difficulty
    description: str
    steps: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    # Fixes are index-aligned with common_mistakes.
    mistake_fixes: list[str] = Field(default_factory=list)
    slug: str
    abbreviation: str
    symbol_key: str
    symbol_standard: bool = True
    symbol_kind: SymbolKind | None = None
    abbreviation_standard: bool = True
    learning_goal: str
    practice: str
    success_check: str
    video_generation_prompt: str
    video_asset_path: str
    video_status: Literal["pilot", "prompt_ready", "ready"] = "prompt_ready"
    reference_video_url: str | None = None
    reference_video_title: str | None = None
    reference_videos: list[dict[str, str]] = Field(default_factory=list)
    reference_card_paths: list[str] = Field(default_factory=list)
    reference_cards: list[dict[str, str]] = Field(default_factory=list)
    reference_board_path: str | None = None
    reference_article_url: str | None = None
    prebuilt_video_asset_path: str | None = None
    custom_video_generation_prompt: str | None = None
    category: Category = "basics"
    aliases: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    related_slugs: list[str] = Field(default_factory=list)
    search_terms: list[str] = Field(default_factory=list)

    @property
    def mistakes_with_fixes(self) -> list[tuple[str, str]]:
        """Pair each common mistake with its fix (missing fixes become '')."""
        fixes = self.mistake_fixes + [""] * (len(self.common_mistakes) - len(self.mistake_fixes))
        return list(zip(self.common_mistakes, fixes))

    @property
    def display_symbol_kind(self) -> SymbolKind:
        """Return the explicit visual role, with compatibility for older packs."""
        return self.symbol_kind or ("standard" if self.symbol_standard else "learning")


# Canonical data kept as a plain dict for backward compatibility with the agent
# core. Keys are the display names used throughout the app.
TECHNIQUE_CATALOG: dict[str, dict] = {
    "사슬뜨기(chain stitch)": {
        "tool_type": "crochet", "difficulty": "beginner",
        "description": "코바늘의 시작 foundation을 만드는 가장 기본 기법입니다.",
        "steps": [
            "실로 시작 고리를 만들어 바늘에 겁니다.",
            "바늘에 실을 감아(yarn over) 고리 사이로 빼냅니다.",
            "원하는 사슬 수만큼 같은 동작을 반복합니다.",
            "사슬 크기가 일정한지 눈으로 확인합니다.",
        ],
        "common_mistakes": ["사슬 크기가 들쭉날쭉함", "시작 실을 너무 세게 당김"],
        "mistake_fixes": [
            "손힘을 일정하게 유지하고, 커진 사슬은 코로 세지 않도록 표시합니다.",
            "시작 매듭을 느슨하게 잡고 첫 두세 코는 의도적으로 여유 있게 뜹니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/crochet-chain-stitch-basics",
        "custom_video_generation_prompt": "손과 코바늘을 클로즈업해 사슬뜨기를 천천히 반복해서 보여주는 초보자용 영상",
    },
    "짧은뜨기(single crochet)": {
        "tool_type": "crochet", "difficulty": "beginner",
        "description": "낮고 단단한 조직을 만드는 기본 코바늘 기법입니다.",
        "steps": [
            "바늘을 다음 코에 넣습니다.",
            "실을 감아 코 사이로 한 번 빼냅니다(고리 2개).",
            "다시 실을 감아 두 고리를 한 번에 빼냅니다.",
            "단 끝까지 반복하고 코 수를 셉니다.",
        ],
        "common_mistakes": ["단 끝 코를 빼먹음", "장력이 너무 조여 사각형이 휘어짐"],
        "mistake_fixes": [
            "매 단 첫 코와 끝 코에 마커를 걸어 코 수를 확인합니다.",
            "손힘을 풀고 한 호수 큰 바늘로 게이지 샘플을 떠 봅니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/single-crochet-row-edges",
        "custom_video_generation_prompt": "짧은뜨기에서 코를 넣는 위치와 단 끝 코 확인을 확대해 보여주는 영상",
    },
    "긴뜨기(half double crochet)": {
        "tool_type": "crochet", "difficulty": "confident_beginner",
        "description": "실을 한 번 감은 뒤 세 고리를 한 번에 빼 중간 높이를 만드는 코바늘 기법입니다.",
        "steps": [
            "바늘에 실을 한 번 감습니다(yarn over).",
            "다음 코에 넣고 실을 감아 빼냅니다(고리 3개).",
            "다시 실을 감아 세 고리를 한 번에 빼냅니다.",
            "단 시작에는 기둥 사슬 2코로 높이를 맞춥니다.",
        ],
        "common_mistakes": ["세 고리를 두 번에 나눠 빼 한길긴뜨기가 됨", "기둥코 높이가 맞지 않음"],
        "mistake_fixes": [
            "바늘 위 고리 3개를 확인한 뒤 한 동작으로 모두 통과합니다.",
            "단 시작의 기둥 사슬 수(보통 2코)를 일정하게 유지합니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/half-double-crochet-basics",
        "custom_video_generation_prompt": "긴뜨기에서 실을 감고 세 고리를 한 번에 빼는 동작을 단계별로 보여주는 영상",
    },
    "빼뜨기(slip stitch)": {
        "tool_type": "crochet", "difficulty": "beginner",
        "description": "단을 연결하거나 위치를 이동할 때 쓰는 낮은 연결 기법입니다.",
        "steps": [
            "바늘을 연결할 코에 넣습니다.",
            "실을 감아 코와 바늘 위 고리를 한 번에 빼냅니다.",
            "원형뜨기에서는 첫 코 머리에 넣어 단을 연결합니다.",
        ],
        "common_mistakes": ["너무 조여 다음 단에 바늘이 안 들어감", "연결 위치를 한 코 옆에 넣음"],
        "mistake_fixes": [
            "빼뜨기는 살짝 느슨하게 떠서 다음 단 진입 공간을 남깁니다.",
            "연결 전 첫 코 머리를 손가락으로 짚어 위치를 확인합니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/slip-stitch-join",
        "custom_video_generation_prompt": "원형뜨기에서 빼뜨기로 단을 연결하는 위치를 표시해 보여주는 영상",
    },
    "매직링(magic ring)": {
        "tool_type": "crochet", "difficulty": "confident_beginner",
        "description": "원형 작품의 중심 구멍을 작게 조일 수 있는 시작 방법입니다.",
        "steps": [
            "실로 고리를 만들고 꼬리실을 아래로 둡니다.",
            "고리 안으로 바늘을 넣어 실을 빼내고 사슬로 고정합니다.",
            "고리 안에 첫 단 코(예: 짧은뜨기)를 필요한 수만큼 넣습니다.",
            "꼬리실을 당겨 중심 구멍을 조입니다.",
        ],
        "common_mistakes": ["꼬리실 방향을 놓침", "첫 단을 조인 뒤 코 수를 세지 않음"],
        "mistake_fixes": [
            "꼬리실을 항상 같은 방향(아래쪽)으로 두고 시작합니다.",
            "조이기 전에 첫 단 코 수를 세어 도안과 맞는지 확인합니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/magic-ring-close-center",
        "custom_video_generation_prompt": "매직링을 만들고 첫 단 짧은뜨기를 넣은 뒤 중심을 조이는 과정을 천천히 보여주는 영상",
    },
    "매직링으로 원형 시작하기(crocheting in the round)": {
        "tool_type": "crochet", "difficulty": "intermediate",
        "description": "독립된 한 코가 아니라 매직링 중심에서 첫 단을 만들고 원을 그리며 이어 가는 작업 방식입니다.",
        "steps": [
            "중심(매직링 등)에서 시작해 첫 단 코를 만듭니다.",
            "도안대로 일정 간격에 늘림코를 넣습니다.",
            "단수링으로 단 시작 위치를 표시합니다.",
            "단마다 코 수가 규칙적으로 늘어나는지 확인합니다.",
        ],
        "common_mistakes": ["늘림 위치가 몰려 육각형처럼 보임", "단 시작 위치를 잃어버림"],
        "mistake_fixes": [
            "늘림코를 단마다 한 코씩 어긋나게 배치해 각을 분산합니다.",
            "단 시작에 대비되는 색 마커를 걸어 매 단 옮깁니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/crochet-round-increase-markers",
        "custom_video_generation_prompt": "매직링 첫 단에서 단수링으로 시작점과 늘림 위치를 관리하는 영상",
    },
    "한길긴뜨기(double crochet)": {
        "tool_type": "crochet", "difficulty": "confident_beginner",
        "description": "도안 기호에서 긴 기둥 모양으로 보이는 코바늘 기법이며, 네트/레이스 가방의 높이와 구멍 패턴을 만드는 데 자주 쓰입니다.",
        "steps": [
            "바늘에 실을 한 번 감습니다.",
            "사슬 공간 또는 코에 넣고 실을 감아 빼냅니다.",
            "실을 감아 두 고리씩 두 번에 나눠 빼냅니다.",
            "구멍무늬는 한길긴뜨기와 사슬을 번갈아 반복합니다.",
        ],
        "common_mistakes": ["실 감기 순서를 놓침", "사슬 공간에 넣는 위치를 헷갈림"],
        "mistake_fixes": [
            "'감기 → 두 고리 빼기 → 두 고리 빼기' 리듬을 유지합니다.",
            "코가 아니라 사슬로 생긴 공간(space)에 넣는지 확인합니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/tall-double-crochet-mesh-pattern",
        "custom_video_generation_prompt": "코바늘 네트 가방에서 한길긴뜨기와 사슬 공간을 반복해 구멍 패턴을 만드는 과정을 보여주는 영상",
    },
    "롱테일 코잡기(long-tail cast on)": {
        "tool_type": "needle_knitting", "difficulty": "beginner",
        "description": "꼬리실과 작업실을 엄지·검지에 걸어 대바늘 첫 단을 빠르게 만드는 대표적인 코잡기입니다.",
        "steps": [
            "꼬리실을 충분히 남겨 시작 고리를 바늘에 겁니다.",
            "엄지에는 꼬리실, 검지에는 작업실이 걸리도록 손가락을 벌립니다.",
            "엄지 고리 아래로 바늘을 넣고 검지 실을 걸어 엄지 고리 사이로 끌어옵니다.",
            "필요한 코 수만큼 반복합니다.",
            "코 간격이 일정한지 확인합니다.",
        ],
        "common_mistakes": ["첫 코가 너무 조임", "코 간격이 일정하지 않음"],
        "mistake_fixes": [
            "첫 코는 느슨하게, 필요하면 한 호수 큰 바늘로 코를 잡습니다.",
            "코를 바늘 몸통까지 밀어 간격을 고르게 맞춥니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/needle-cast-on-basics",
        "custom_video_generation_prompt": "대바늘에 코를 일정한 간격으로 잡는 손동작을 보여주는 영상",
    },
    "겉뜨기(knit stitch)": {
        "tool_type": "needle_knitting", "difficulty": "beginner",
        "description": "대바늘의 가장 기본적인 앞면 뜨기 기법입니다.",
        "steps": [
            "오른바늘을 왼바늘 코 앞에서 뒤로 넣습니다.",
            "실을 시계 반대 방향으로 감습니다.",
            "감은 실을 코 사이로 빼내 새 코를 만듭니다.",
            "왼바늘의 헌 코를 빼냅니다.",
        ],
        "common_mistakes": ["코를 비틀어 뜸", "바늘 끝에서 떠서 코 크기가 작아짐"],
        "mistake_fixes": [
            "코 앞쪽 다리에 바늘을 넣어 비틀림을 방지합니다.",
            "코를 바늘 몸통까지 올려 실제 굵기로 뜹니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/knit-stitch-basics",
        "custom_video_generation_prompt": "겉뜨기에서 오른바늘을 넣는 방향과 실을 감는 동작을 보여주는 영상",
    },
    "안뜨기(purl stitch)": {
        "tool_type": "needle_knitting", "difficulty": "confident_beginner",
        "description": "겉뜨기와 반대 질감을 만드는 대바늘 기본 기법입니다.",
        "steps": [
            "실을 편물 앞쪽에 둡니다.",
            "오른바늘을 코 앞에서(오른쪽에서) 넣습니다.",
            "실을 감아 코 사이로 빼냅니다.",
            "헌 코를 빼내고 실 위치를 확인합니다.",
        ],
        "common_mistakes": ["실 위치를 앞뒤로 옮기는 것을 놓침", "겉뜨기와 섞일 때 코가 늘어남"],
        "mistake_fixes": [
            "안뜨기는 실을 항상 앞에 두고 시작하는지 확인합니다.",
            "겉↔안 전환 시 실을 바늘 사이로만 옮겨 여분 코가 생기지 않게 합니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/purl-stitch-basics",
        "custom_video_generation_prompt": "안뜨기에서 실을 앞에 두고 코를 뜨는 방향을 보여주는 영상",
    },
    "1×1 고무뜨기(1x1 ribbing)": {
        "tool_type": "needle_knitting", "difficulty": "confident_beginner",
        "description": "겉뜨기 1코와 안뜨기 1코를 반복해 탄력 있는 세로 골을 만드는 조직입니다.",
        "steps": [
            "도안대로 겉뜨기와 안뜨기를 정한 수만큼 번갈아 뜹니다(예: 1x1).",
            "겉→안 전환 때 실을 바늘 사이로 옮깁니다.",
            "다음 단도 코의 성질(겉/안)에 맞춰 이어 뜹니다.",
            "패턴이 세로로 곧게 이어지는지 확인합니다.",
        ],
        "common_mistakes": ["실 위치 전환을 빼먹음", "반복 패턴이 한 코씩 밀림"],
        "mistake_fixes": [
            "겉↔안 전환마다 실을 앞뒤로 옮겼는지 습관적으로 확인합니다.",
            "각 코가 아래 코의 성질과 같은지(겉 위 겉, 안 위 안) 보며 뜹니다.",
        ],
        "prebuilt_video_asset_path": "local://videos/ribbing-knit-purl-repeat",
        "custom_video_generation_prompt": "1x1 고무뜨기에서 겉뜨기와 안뜨기 사이 실 위치를 옮기는 장면을 보여주는 영상",
    },
}


def _video_prompt(action: str, *, knitting: bool = False) -> str:
    tool = (
        "two light wooden knitting needles and cream worsted yarn"
        if knitting
        else "one matte 5 mm crochet hook and coral worsted yarn"
    )
    return (
        "Create an 8-second, 16:9 instructional knitting video. Top-down macro view of adult hands only, "
        f"using {tool} on a clean warm-gray work mat. Demonstrate exactly one motion slowly and repeat it: {action}. "
        "Keep the number and position of fingers, needles or hook, yarn strand, loops, and stitches anatomically and "
        "temporally consistent. Keep the active stitch centered and fully visible. End in a pose that can loop back "
        "to the opening frame. No camera movement, cuts that hide the stitch, captions, letters, chart symbols, logos, "
        "jewelry, extra tools, extra fingers, fused fingers, disappearing yarn, or impossible stitch transitions."
    )


# Complete pre-authored lesson packs. Exact chart symbols are rendered from
# `content/symbols.py`; prompts deliberately omit generated text/symbols because
# those details are more accurate as deterministic UI overlays.
def _reference_cards(slug: str, copy: list[tuple[str, str]]) -> list[dict[str, str]]:
    """Build reusable, source-frame review card metadata for a lesson."""
    return [
        {
            "path": f"assets/techniques/{slug}/reference-cards/focus-{index:02d}.jpg",
            "title": title,
            "description": description,
        }
        for index, (title, description) in enumerate(copy, start=1)
    ]


_LESSON_PACKS: dict[str, dict] = {
    "사슬뜨기(chain stitch)": {
        "slug": "crochet-chain-stitch", "abbreviation": "ch", "symbol_key": "chain", "symbol_standard": True,
        "learning_goal": "실을 감아 고리 사이로 빼는 동작을 반복하며 크기가 일정한 기초 사슬을 만듭니다.",
        "practice": "밝은 중간 굵기 실로 사슬 15코를 두 번 만들고 두 줄의 길이와 코 크기를 비교하세요.",
        "success_check": "15개의 V 모양이 빠짐없이 보이고, 바늘이 각 사슬에 무리 없이 들어가나요?",
        "video_generation_prompt": _video_prompt("form a slip knot, yarn over, pull through one loop, and repeat three even chain stitches"),
        "video_asset_path": "assets/techniques/crochet-chain-stitch/reference-guide.mp4", "video_status": "ready",
        "reference_card_paths": [
            f"assets/techniques/crochet-chain-stitch/reference-cards/focus-{index:02d}.jpg"
            for index in range(1, 6)
        ],
        "reference_cards": _reference_cards("crochet-chain-stitch", [
            ("준비", "바늘 위 활성 고리는 아직 코로 세지 않아요."),
            ("실 걸기", "작업실 아래로 바늘 홈을 가져갑니다."),
            ("고리 통과", "잡은 실만 기존 고리 안으로 당깁니다."),
            ("새 고리", "바늘에는 다시 활성 고리 하나만 남습니다."),
            ("코 세기", "바늘 아래 완성된 V 하나를 사슬 1코로 셉니다."),
        ]),
        "reference_board_path": "assets/techniques/crochet-chain-stitch/reference-cards/overview-board.jpg",
        "reference_videos": [
            {
                "url": "https://www.youtube.com/watch?v=lTIWye2ogv8&list=PLqZYtl2pBreV7OSXUrPRe2lB8ateRWBc8",
                "title": "바늘이야기 코바늘 마스터 #1 · 바늘 잡는 법과 실 감는 법",
                "focus": "먼저 코바늘을 쥐는 자세와 왼손에 실을 거는 방법을 따라 합니다.",
            },
            {
                "url": "https://www.youtube.com/watch?v=eCiESFasa0g&list=PLqZYtl2pBreV7OSXUrPRe2lB8ateRWBc8",
                "title": "바늘이야기 코바늘 마스터 #2 · 사슬뜨기",
                "focus": "사슬 한 코가 만들어지는 장면과 완성된 V 모양을 확인합니다.",
            },
        ],
        "reference_article_url": None,
    },
    "짧은뜨기(single crochet)": {
        "slug": "single-crochet", "abbreviation": "sc", "symbol_key": "single_crochet", "symbol_standard": True,
        "learning_goal": "다음 코에 바늘을 넣고 두 번의 실 감기로 낮고 단단한 한 코를 완성합니다.",
        "practice": "사슬 12코 위에 짧은뜨기 3단을 뜨고 각 단의 첫 코와 마지막 코에 마커를 거세요.",
        "success_check": "매 단 코 수가 같고 양쪽 가장자리가 안쪽으로 줄어들지 않았나요?",
        "video_generation_prompt": _video_prompt("insert the hook under both top loops, pull up one loop, yarn over, and pull through both loops to finish one single crochet"),
        "video_asset_path": "assets/techniques/single-crochet/video.mp4", "video_status": "pilot",
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=oZxhaO0dT0A&list=PLqZYtl2pBreV7OSXUrPRe2lB8ateRWBc8", "title": "바늘이야기 코바늘 마스터 #3 · 평면 짧은뜨기", "focus": "사슬에 바늘을 넣는 위치와 첫 코·마지막 코를 확인합니다."}],
        "reference_cards": _reference_cards("single-crochet", [
            ("완성 사슬 준비", "사슬뜨기를 마친 편물을 잡고 짧은뜨기를 시작할 방향으로 돌립니다."),
            ("사슬 뒷산 찾기", "사슬 뒤쪽에서 볼록하게 솟은 한 가닥을 첫 삽입 위치로 찾습니다."),
            ("바늘 넣기", "찾은 사슬 뒷산 아래로 코바늘을 앞에서 뒤로 넣습니다."),
            ("두 고리 만들기", "작업실을 걸어 끌어오면 바늘 위에 고리 두 개가 생깁니다."),
            ("한 코 완성", "다시 실을 걸어 두 고리를 한 번에 통과합니다."),
        ]),
    },
    "긴뜨기(half double crochet)": {
        "slug": "half-double-crochet", "abbreviation": "hdc", "symbol_key": "half_double_crochet", "symbol_standard": True,
        "learning_goal": "실을 한 번 감고 만들어진 세 고리를 한 번에 빼 중간 높이의 코를 만듭니다.",
        "practice": "사슬 12코 위에 긴뜨기 2단을 뜨며 매 코마다 바늘 위 고리 3개를 확인하세요.",
        "success_check": "세 고리를 한 번에 통과했고 한길긴뜨기보다 낮은 높이가 일정한가요?",
        "video_generation_prompt": _video_prompt("yarn over once, insert into the next stitch, pull up a loop to show three loops, then yarn over and pull through all three loops at once"),
        "video_asset_path": "assets/techniques/half-double-crochet/video.mp4", "video_status": "prompt_ready",
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=t_tEB0fpBiM&list=PLqZYtl2pBreV7OSXUrPRe2lB8ateRWBc8", "title": "바늘이야기 코바늘 마스터 #4 · 평면 긴뜨기", "focus": "바늘 위 세 고리와 한 번에 빼는 동작을 확인합니다."}],
        "reference_cards": _reference_cards("half-double-crochet", [
            ("실 한 번 감기", "완성한 사슬을 잡고 코에 넣기 전에 작업실을 바늘에 한 번 감습니다."),
            ("사슬 뒷산에 넣기", "감은 실을 유지한 채 표시한 사슬 뒷산 아래로 바늘을 넣습니다."),
            ("고리 끌어오기", "작업실을 걸어 사슬 밖으로 새 고리를 끌어옵니다."),
            ("세 고리 확인", "활성 고리·감은 실·끌어온 고리, 총 세 고리가 있는지 봅니다."),
            ("한 코 완성", "실을 걸어 세 고리를 한 번에 통과합니다."),
        ]),
    },
    "빼뜨기(slip stitch)": {
        "slug": "slip-stitch", "abbreviation": "sl st", "symbol_key": "slip_stitch", "symbol_standard": True,
        "learning_goal": "새 높이를 만들지 않고 코와 바늘 위 고리를 한 번에 통과해 위치를 연결합니다.",
        "practice": "사슬 10코를 만든 뒤 각 사슬에 빼뜨기를 하고, 마지막 코에도 바늘이 들어가는지 확인하세요.",
        "success_check": "편물이 말리지 않을 만큼 느슨하고 모든 연결 코가 낮게 이어졌나요?",
        "video_generation_prompt": _video_prompt("insert into the next stitch and pull the working yarn through the stitch and the loop already on the hook in one continuous motion"),
        "video_asset_path": "assets/techniques/slip-stitch/video.mp4", "video_status": "prompt_ready",
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=rNC9R7AzZcI", "title": "바늘이야기 손뜨개 강의 · 코바늘 빼뜨기", "focus": "코에 넣은 뒤 작업실을 편물의 코와 활성 고리에 연속해서 통과하는 장면을 확인합니다."}],
        "reference_cards": _reference_cards("slip-stitch", [
            ("연결할 코 찾기", "새 높이를 만들지 않고 연결할 다음 코의 V 머리를 확인합니다."),
            ("바늘 넣기", "바늘 위 활성 고리를 유지한 채 다음 코 아래로 코바늘을 넣습니다."),
            ("작업실 걸기", "코 뒤쪽의 작업실을 바늘 홈으로 잡습니다."),
            ("두 고리 연속 통과", "잡은 실을 편물의 코와 바늘 위 활성 고리까지 한 번에 이어서 통과합니다."),
            ("낮은 연결 확인", "바늘 위에 고리 하나만 남고 새 기둥 없이 코가 낮게 연결됐는지 봅니다."),
        ]),
    },
    "매직링(magic ring)": {
        "slug": "magic-ring", "abbreviation": "MR", "symbol_key": "magic_ring", "symbol_standard": False,
        "symbol_kind": "learning", "abbreviation_standard": False,
        "learning_goal": "조절 가능한 실 고리를 만들고 첫 단의 코를 넣은 뒤 중심을 단단히 닫습니다.",
        "practice": "매직링 안에 짧은뜨기 6코를 넣고 코 수를 확인한 다음 꼬리실을 당겨 닫으세요.",
        "success_check": "6코가 모두 남아 있고 중심 구멍이 벌어지지 않게 닫혔나요?",
        "video_generation_prompt": _video_prompt("wrap yarn into an adjustable ring, secure it with one chain, work two sample stitches into the ring, then pull the tail to close the center"),
        "video_asset_path": "assets/techniques/magic-ring/video.mp4", "video_status": "prompt_ready",
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=qphAHjPhhkU&list=PLqZYtl2pBreV7OSXUrPRe2lB8ateRWBc8", "title": "바늘이야기 코바늘 마스터 #6 · 매직링과 원형 짧은뜨기", "focus": "매직링을 잡는 위치와 첫 단 시작점을 확인합니다."}],
        "reference_cards": _reference_cards("magic-ring", [
            ("손가락에 실 걸기", "꼬리실을 남기고 작업실을 손가락 위에 걸어 넉넉한 원을 준비합니다."),
            ("실을 교차해 링 만들기", "작업실과 꼬리실을 교차하고 교차점을 손가락으로 고정합니다."),
            ("링 안으로 바늘 넣기", "교차점을 놓치지 않은 채 링 안쪽으로 코바늘을 넣습니다."),
            ("작업실 끌어오기", "링 뒤의 작업실을 걸어 링 앞으로 새 고리를 끌어옵니다."),
            ("사슬로 시작 고정", "작업실을 다시 걸어 활성 고리를 통과해 시작 고리를 고정합니다."),
        ]),
    },
    "매직링으로 원형 시작하기(crocheting in the round)": {
        "slug": "round-crochet", "abbreviation": "in rounds", "symbol_key": "round_crochet", "symbol_standard": False,
        "symbol_kind": "learning", "abbreviation_standard": False,
        "learning_goal": "매직링의 첫 코를 표시하고 첫 단을 완성해 평평한 원형 작업을 시작합니다.",
        "practice": "매직링 6코에서 시작해 두 번째 단은 모든 코에 늘림을 넣고 마커를 옮기세요.",
        "success_check": "두 번째 단이 12코이고 마커가 단 시작점에 있으며 원이 편평한가요?",
        "video_generation_prompt": _video_prompt("move a contrasting stitch marker to the first stitch, work one normal stitch and one increase, then show the evenly expanding round lying flat"),
        "video_asset_path": "assets/techniques/round-crochet/video.mp4", "video_status": "prompt_ready",
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=qphAHjPhhkU&list=PLqZYtl2pBreV7OSXUrPRe2lB8ateRWBc8", "title": "바늘이야기 코바늘 마스터 #6 · 매직링과 원형 짧은뜨기", "focus": "단 시작 위치와 원형으로 이어 뜨는 흐름을 확인합니다."}],
        "reference_cards": _reference_cards("round-crochet", [
            ("완성 매직링에 넣기", "매직링 시작 고리를 만든 뒤 바늘을 링의 큰 공간 안으로 넣습니다."),
            ("첫 짧은뜨기 완성", "링과 꼬리실을 함께 감싸며 첫 짧은뜨기 한 코를 완성합니다."),
            ("첫 코 표시", "방금 만든 첫 코의 V 두 가닥에 마커를 걸어 단 시작점을 표시합니다."),
            ("한 바퀴 뜨고 중심 조이기", "정해진 코 수를 링에 넣은 뒤 꼬리실을 당겨 중심 구멍을 닫습니다."),
            ("첫 코에 단 연결", "표시한 첫 코에 빼뜨기해 첫 단의 시작과 끝을 연결합니다."),
        ]),
    },
    "한길긴뜨기(double crochet)": {
        "slug": "double-crochet", "abbreviation": "dc", "symbol_key": "double_crochet", "symbol_standard": True,
        "learning_goal": "실을 한 번 감고 고리를 두 개씩 두 번 빼 높이 있는 코를 만듭니다.",
        "practice": "사슬 12코 위에 한길긴뜨기 2단을 뜨며 ‘두 고리, 두 고리’를 소리 내어 확인하세요.",
        "success_check": "각 코에서 두 고리씩 정확히 두 번 뺐고 높이가 일정한가요?",
        "video_generation_prompt": _video_prompt("yarn over once, insert into the next stitch, pull up a loop, then yarn over and pull through two loops twice to complete one double crochet"),
        "video_asset_path": "assets/techniques/double-crochet/video.mp4", "video_status": "prompt_ready",
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=Cb1EAsgCKqw&list=PLqZYtl2pBreV7OSXUrPRe2lB8ateRWBc8", "title": "바늘이야기 코바늘 마스터 #5 · 평면 한길긴뜨기", "focus": "두 고리씩 두 번 빼는 순서와 코 높이를 확인합니다."}],
        "reference_cards": _reference_cards("double-crochet", [
            ("실 한 번 감기", "완성 사슬 위에서 높이를 만들 작업실을 바늘에 한 번 감습니다."),
            ("사슬 뒷산에 넣기", "감은 실을 유지한 채 다음 사슬 뒷산 아래로 바늘을 넣습니다."),
            ("세 고리 만들기", "작업실을 끌어오면 바늘 위에 고리 세 개가 생깁니다."),
            ("두 고리만 통과", "다시 실을 걸어 앞쪽 두 고리만 먼저 통과합니다."),
            ("남은 두 고리 통과", "실을 다시 걸어 남은 두 고리를 통과해 한 코를 완성합니다."),
        ]),
    },
    "롱테일 코잡기(long-tail cast on)": {
        "slug": "casting-on", "abbreviation": "CO", "symbol_key": "cast_on", "symbol_standard": True,
        "learning_goal": "첫 단을 시작할 코를 바늘 위에 일정한 간격과 장력으로 만듭니다.",
        "practice": "대바늘에 15코를 잡고 바늘 몸통을 따라 코 간격을 고르게 정리하세요.",
        "success_check": "15코가 모두 같은 방향이고 바늘 몸통에서 부드럽게 움직이나요?",
        "video_generation_prompt": _video_prompt("use a long-tail cast-on to place three evenly tensioned stitches onto the left needle, showing the thumb loop and yarn path clearly", knitting=True),
        "video_asset_path": "assets/techniques/casting-on/video.mp4", "video_status": "prompt_ready",
    },
    "겉뜨기(knit stitch)": {
        "slug": "knit-stitch", "abbreviation": "K", "symbol_key": "knit", "symbol_standard": True,
        "learning_goal": "오른바늘을 코 앞에서 뒤로 넣고 새 고리를 만들어 헌 코를 넘깁니다.",
        "practice": "15코를 잡아 겉뜨기 4단을 뜨고 매 단 끝에서 코 수를 확인하세요.",
        "success_check": "코가 비틀리지 않고 15코가 유지되며 V 모양이 일정한가요?",
        "video_generation_prompt": _video_prompt("insert the right needle front-to-back through one stitch, wrap yarn counterclockwise, pull a new loop through, and slide the old stitch off", knitting=True),
        "video_asset_path": "assets/techniques/knit-stitch/video.mp4", "video_status": "pilot",
    },
    "안뜨기(purl stitch)": {
        "slug": "purl-stitch", "abbreviation": "P", "symbol_key": "purl", "symbol_standard": True,
        "learning_goal": "실을 편물 앞에 두고 오른바늘로 새 고리를 만들어 안뜨기 질감을 만듭니다.",
        "practice": "15코를 잡아 안뜨기 3단을 뜨며 시작 전마다 실이 편물 앞에 있는지 확인하세요.",
        "success_check": "가로 마디 질감이 일정하고 실 위치를 옮길 때 여분 코가 생기지 않았나요?",
        "video_generation_prompt": _video_prompt("hold yarn in front, insert the right needle into one stitch from right to left, wrap yarn, pull a new loop through, and slide the old stitch off", knitting=True),
        "video_asset_path": "assets/techniques/purl-stitch/video.mp4", "video_status": "prompt_ready",
    },
    "1×1 고무뜨기(1x1 ribbing)": {
        "slug": "ribbing", "abbreviation": "K1, P1 rep", "symbol_key": "ribbing", "symbol_standard": False,
        "symbol_kind": "learning", "abbreviation_standard": False,
        "learning_goal": "겉뜨기와 안뜨기를 반복하고 실 위치를 바늘 사이로 옮겨 탄력 있는 조직을 만듭니다.",
        "practice": "짝수 16코를 잡고 1×1 고무뜨기를 6단 반복하세요.",
        "success_check": "겉·안 세로 골이 한 코씩 어긋나지 않고 편물이 좌우로 탄력 있게 늘어나나요?",
        "video_generation_prompt": _video_prompt("work one knit stitch, move yarn between the needles to the front, work one purl stitch, then move yarn between the needles to the back", knitting=True),
        "video_asset_path": "assets/techniques/ribbing/video.mp4", "video_status": "prompt_ready",
    },
}


def _expanded_entry(
    *,
    tool_type: ToolType,
    difficulty: Difficulty,
    category: Category,
    description: str,
    steps: list[str],
    mistake: str,
    fix: str,
    slug: str,
    abbreviation: str,
    symbol_key: str,
    learning_goal: str,
    practice: str,
    success_check: str,
    motion: str,
    aliases: list[str],
    prerequisites: list[str],
    related_slugs: list[str],
    symbol_standard: bool = True,
    symbol_kind: SymbolKind | None = None,
    abbreviation_standard: bool = True,
) -> dict:
    """Build a complete catalog entry while keeping authored lesson text explicit."""
    return {
        "tool_type": tool_type,
        "difficulty": difficulty,
        "category": category,
        "description": description,
        "steps": steps,
        "common_mistakes": [mistake],
        "mistake_fixes": [fix],
        "slug": slug,
        "abbreviation": abbreviation,
        "symbol_key": symbol_key,
        "symbol_standard": symbol_standard,
        "symbol_kind": symbol_kind,
        "abbreviation_standard": abbreviation_standard,
        "learning_goal": learning_goal,
        "practice": practice,
        "success_check": success_check,
        "video_generation_prompt": _video_prompt(motion, knitting=tool_type == "needle_knitting"),
        "video_asset_path": f"assets/techniques/{slug}/video.mp4",
        "video_status": "prompt_ready",
        "prebuilt_video_asset_path": f"local://videos/{slug}",
        "custom_video_generation_prompt": f"{description} 손동작을 천천히 보여주는 초보자용 영상",
        "aliases": aliases,
        "prerequisites": prerequisites,
        "related_slugs": related_slugs,
        "search_terms": aliases,
    }


# Additional complete lessons bring the initial library to 20 crochet and
# 20 needle-knitting techniques. Adding future entries here automatically
# extends navigation, search, agent matching, and regression coverage.
_EXPANDED_TECHNIQUES: dict[str, dict] = {
    "시작 고리(slip knot)": _expanded_entry(
        tool_type="crochet", difficulty="beginner", category="basics",
        description="코바늘에 첫 고리를 걸되 크기를 조절할 수 있게 만드는 시작 매듭입니다.",
        steps=["실을 교차해 고리를 만듭니다.", "작업실을 고리 안으로 끌어와 새 고리를 만듭니다.", "바늘에 걸고 꼬리실을 당겨 바늘 굵기에 맞춥니다."],
        mistake="고리가 조절되지 않는 일반 매듭이 됨", fix="꼬리실을 당겼을 때 고리 크기가 변하는지 바늘에 걸기 전에 확인합니다.",
        slug="slip-knot", abbreviation="slip knot", symbol_key="slip_knot", symbol_standard=False,
        symbol_kind="learning", abbreviation_standard=False,
        learning_goal="당기면 조절되는 시작 고리를 만들어 바늘 몸통에서 부드럽게 움직입니다.",
        practice="시작 고리를 5번 만들고 매번 바늘에서 크기를 조절해 보세요.", success_check="꼬리실을 당기면 고리가 작아지고 작업실을 당기면 커지나요?",
        motion="cross the yarn into a loop, pull a bight of working yarn through, place it on the hook, and adjust it",
        aliases=["시작 고리", "시작고리", "slip knot"], prerequisites=[], related_slugs=["crochet-chain-stitch"],
    ),
    "두길긴뜨기(treble crochet)": _expanded_entry(
        tool_type="crochet", difficulty="confident_beginner", category="basics",
        description="실을 두 번 감고 두 고리씩 세 번 빼서 한길긴뜨기보다 높은 기둥코를 만듭니다.",
        steps=["바늘에 실을 두 번 감습니다.", "다음 코에 넣어 실을 끌어오면 고리 4개가 됩니다.", "실을 감아 두 고리씩 세 번 나누어 뺍니다."],
        mistake="첫 실 감기 횟수를 놓쳐 높이가 달라짐", fix="코에 넣기 전에 바늘 몸통의 두 번 감긴 실을 눈으로 확인합니다.",
        slug="treble-crochet", abbreviation="tr", symbol_key="treble_crochet",
        learning_goal="두 번 감기와 세 번의 두 고리 빼기를 일정한 리듬으로 완성합니다.",
        practice="사슬 12코 위에 두길긴뜨기 1단을 뜨세요.", success_check="각 코의 높이가 같고 두 고리 빼기를 세 번 했나요?",
        motion="yarn over twice, insert into one stitch, pull up a loop, then yarn over and pull through two loops three times",
        aliases=["두길긴뜨기", "treble crochet", "tr"], prerequisites=["double-crochet"], related_slugs=["double-crochet"],
    ),
    "짧은뜨기 늘려뜨기(single crochet increase)": _expanded_entry(
        tool_type="crochet", difficulty="confident_beginner", category="shaping",
        description="같은 코에 짧은뜨기 두 코를 넣어 전체 코 수를 하나 늘리는 기법입니다.",
        steps=["늘릴 코에 짧은뜨기 한 코를 뜹니다.", "같은 코에 바늘을 다시 넣습니다.", "짧은뜨기 한 코를 더 완성합니다."],
        mistake="두 번째 코를 다음 코에 떠서 늘림이 되지 않음", fix="두 코가 같은 V 머리 아래에서 나오는지 확인하고 마커를 겁니다.",
        slug="single-crochet-increase", abbreviation="2 sc in next st", symbol_key="sc_increase", symbol_standard=False,
        learning_goal="한 코에 두 코를 정확히 배치해 원하는 위치에서 형태를 넓힙니다.",
        practice="짧은뜨기 6코 원에서 모든 코에 늘림해 12코를 만드세요.", success_check="한 단 뒤 코 수가 정확히 두 배가 되었나요?",
        motion="work one single crochet and a second single crochet into the exact same stitch",
        aliases=["짧은뜨기 늘려뜨기", "짧은뜨기 늘림", "single crochet increase", "sc inc"], prerequisites=["single-crochet"], related_slugs=["single-crochet-decrease", "round-crochet"],
    ),
    "짧은뜨기 2코 모아뜨기(single crochet 2 together)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="shaping",
        description="이웃한 두 코에서 고리를 끌어온 뒤 함께 마무리해 한 코를 줄입니다.",
        steps=["첫 코에서 고리를 끌어옵니다.", "다음 코에서 고리를 끌어와 바늘 위 고리 3개를 만듭니다.", "실을 감아 세 고리를 한 번에 뺍니다."],
        mistake="첫 코를 완성한 뒤 다음 코를 떠서 줄어들지 않음", fix="두 코에서 미완성 고리를 모은 뒤 마지막에 한 번만 마무리합니다.",
        slug="single-crochet-decrease", abbreviation="sc2tog", symbol_key="sc2tog",
        learning_goal="두 코를 하나의 머리로 모아 구멍 없이 완만하게 줄입니다.",
        practice="짧은뜨기 12코에서 sc2tog를 6번 떠 6코로 줄이세요.", success_check="완성 코 수가 6코이고 줄임 위치에 큰 구멍이 없나요?",
        motion="pull up a loop in each of two adjacent stitches, show three loops, then pull through all three together",
        aliases=["짧은뜨기 2코 모아뜨기", "짧은뜨기 줄임", "single crochet decrease", "sc2tog"], prerequisites=["single-crochet"], related_slugs=["single-crochet-increase"],
    ),
    "한길긴뜨기 2코 모아뜨기(double crochet 2 together)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="shaping",
        description="한길긴뜨기 두 코를 각각 미완성으로 뜬 뒤 마지막 고리를 함께 빼 한 코로 줄입니다.",
        steps=["첫 코에 한길긴뜨기를 마지막 두 고리 전까지 뜹니다.", "다음 코도 같은 지점까지 미완성으로 뜹니다.", "남은 세 고리를 한 번에 뺍니다."],
        mistake="각 코를 따로 완성해 코 수가 줄지 않음", fix="첫 미완성 코의 고리를 바늘에 남긴 채 두 번째 코로 이동합니다.",
        slug="double-crochet-decrease", abbreviation="dc2tog", symbol_key="dc2tog",
        learning_goal="두 개의 높은 코를 하나의 꼭짓점으로 모아 자연스럽게 폭을 줄입니다.",
        practice="한길긴뜨기 10코에서 dc2tog를 5번 떠 보세요.", success_check="다음 단에서 셀 수 있는 코 머리가 5개인가요?",
        motion="leave one double crochet unfinished in each of two stitches, then yarn over and pull through the three remaining loops",
        aliases=["한길긴뜨기 2코 모아뜨기", "한길긴뜨기 줄임", "double crochet decrease", "dc2tog"], prerequisites=["double-crochet"], related_slugs=["three-dc-cluster"],
    ),
    "앞고리에만 뜨기(front loop only)": _expanded_entry(
        tool_type="crochet", difficulty="confident_beginner", category="texture",
        description="코 머리의 앞쪽 고리 하나에만 바늘을 넣어 선이 생기는 조직을 만듭니다.",
        steps=["다음 코의 V 머리를 확인합니다.", "몸 쪽 앞고리 하나에만 바늘을 넣습니다.", "도안이 지정한 기본 코를 완성합니다."],
        mistake="두 고리를 모두 잡아 질감선이 사라짐", fix="바늘 아래에 앞고리 한 가닥만 걸렸는지 옆에서 확인합니다.",
        slug="front-loop-only", abbreviation="FLO", symbol_key="front_loop", symbol_kind="modifier",
        learning_goal="앞고리와 뒤고리를 구분해 지정된 한 가닥에만 정확히 뜹니다.",
        practice="짧은뜨기 10코를 FLO로 2단 떠 일반 짧은뜨기와 비교하세요.", success_check="사용하지 않은 뒤고리가 가로선처럼 남아 있나요?",
        motion="identify the front loop of one stitch, insert under that single strand only, and complete one single crochet",
        aliases=["앞고리뜨기", "앞고리만", "front loop only", "FLO"], prerequisites=["single-crochet"], related_slugs=["back-loop-only"],
    ),
    "뒤고리에만 뜨기(back loop only)": _expanded_entry(
        tool_type="crochet", difficulty="confident_beginner", category="texture",
        description="코 머리의 뒤쪽 고리 하나에만 떠 능선과 신축성을 만드는 기법입니다.",
        steps=["다음 코의 V 머리를 확인합니다.", "몸에서 먼 뒤고리 하나에만 바늘을 넣습니다.", "도안이 지정한 기본 코를 완성합니다."],
        mistake="앞고리를 잡거나 두 고리를 모두 잡음", fix="작업 전 남겨질 앞고리가 바늘 앞쪽에 보이는지 확인합니다.",
        slug="back-loop-only", abbreviation="BLO", symbol_key="back_loop", symbol_kind="modifier",
        learning_goal="뒤고리만 사용해 고른 능선이 이어지는 조직을 만듭니다.",
        practice="짧은뜨기 10코를 BLO로 4단 떠 접히는 방향을 관찰하세요.", success_check="각 단에 사용하지 않은 앞고리 능선이 연속으로 보이나요?",
        motion="identify the back loop of one stitch, insert under that single strand only, and complete one single crochet",
        aliases=["뒤고리뜨기", "뒤고리만", "back loop only", "BLO"], prerequisites=["single-crochet"], related_slugs=["front-loop-only", "ribbing"],
    ),
    "앞걸어 한길긴뜨기(front post double crochet)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="코 머리가 아니라 앞쪽에서 기둥을 감싸 입체적으로 솟는 한길긴뜨기를 만듭니다.",
        steps=["실을 감고 앞에서 뒤로 기둥 옆에 바늘을 넣습니다.", "기둥 뒤를 지나 다시 앞으로 바늘을 뺍니다.", "기둥을 감싼 상태로 한길긴뜨기를 완성합니다."],
        mistake="코 머리에 바늘을 넣어 입체감이 사라짐", fix="바늘이 세로 기둥 전체를 가로로 감싸는지 확인합니다.",
        slug="front-post-double-crochet", abbreviation="FPdc", symbol_key="front_post_dc",
        learning_goal="앞에서 기둥을 감싸 도드라진 세로 골을 만듭니다.",
        practice="한길긴뜨기 바탕 10코 위에 FPdc를 한 코씩 떠 보세요.", success_check="감싼 기둥이 편물 앞쪽으로 도드라지나요?",
        motion="yarn over, insert front-to-back and back-to-front around one stitch post, then complete a double crochet",
        aliases=["앞걸어 한길긴뜨기", "앞걸어뜨기", "front post double crochet", "FPdc"], prerequisites=["double-crochet"], related_slugs=["back-post-double-crochet"],
    ),
    "뒤걸어 한길긴뜨기(back post double crochet)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="뒤쪽에서 기둥을 감싸 편물 앞면에서 들어간 세로 골을 만드는 기법입니다.",
        steps=["실을 감고 뒤에서 앞으로 기둥 옆에 바늘을 넣습니다.", "기둥 앞을 지나 다시 뒤로 바늘을 뺍니다.", "기둥을 감싼 상태로 한길긴뜨기를 완성합니다."],
        mistake="바늘 진행 방향이 FPdc와 같아짐", fix="작업 내내 코 기둥이 바늘 앞쪽에 놓이는지 확인합니다.",
        slug="back-post-double-crochet", abbreviation="BPdc", symbol_key="back_post_dc",
        learning_goal="뒤에서 기둥을 감싸 오목한 골과 탄력 있는 조직을 만듭니다.",
        practice="FPdc와 BPdc를 번갈아 10코씩 2단 떠 보세요.", success_check="앞걸어 코와 뒤걸어 코의 높낮이가 번갈아 보이나요?",
        motion="yarn over, insert back-to-front and front-to-back around one stitch post, then complete a double crochet",
        aliases=["뒤걸어 한길긴뜨기", "뒤걸어뜨기", "back post double crochet", "BPdc"], prerequisites=["double-crochet"], related_slugs=["front-post-double-crochet"],
    ),
    "한길긴뜨기 3코 구슬뜨기(3-dc cluster)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="세 개의 한길긴뜨기를 미완성으로 모아 하나의 꼭짓점으로 닫는 장식 기법입니다.",
        steps=["지정 위치에 미완성 한길긴뜨기를 세 번 만듭니다.", "바늘 위에 남은 네 고리를 확인합니다.", "실을 감아 모든 고리를 한 번에 뺍니다."],
        mistake="중간 코를 완성해 클러스터가 갈라짐", fix="세 기둥을 모두 미완성 상태로 바늘에 보관한 뒤 한 번에 닫습니다.",
        slug="three-dc-cluster", abbreviation="3-dc CL", symbol_key="dc3_cluster",
        learning_goal="세 기둥을 한 꼭짓점으로 모아 균일한 클러스터를 만듭니다.",
        practice="사슬 공간 세 곳에 3-dc 클러스터를 하나씩 만드세요.", success_check="각 클러스터에 기둥 3개와 꼭짓점 1개가 보이나요?",
        motion="make three unfinished double crochets into one space, show four loops, then close all loops together",
        aliases=["한길긴뜨기 3코 구슬뜨기", "한길긴뜨기 3코 클러스터", "클러스터뜨기", "3-dc cluster", "cluster"], prerequisites=["double-crochet"], related_slugs=["puff-stitch", "popcorn-stitch"],
    ),
    "긴 고리 구슬뜨기(puff stitch)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="같은 위치에서 긴 고리를 여러 번 끌어올려 폭신한 한 덩어리로 닫는 기법입니다.",
        steps=["실을 감고 같은 위치에서 긴 고리를 끌어올리는 동작을 반복합니다.", "모든 고리 높이를 같게 맞춥니다.", "실을 감아 고리를 함께 빼고 사슬로 고정합니다."],
        mistake="끌어올린 고리 높이가 달라 퍼프가 기울어짐", fix="각 고리를 기존 코 높이까지 충분히 끌어올린 뒤 다음 반복을 시작합니다.",
        slug="puff-stitch", abbreviation="puff", symbol_key="puff_stitch", symbol_kind="learning", abbreviation_standard=False,
        learning_goal="긴 고리의 높이와 수를 일정하게 유지해 폭신한 질감을 만듭니다.",
        practice="같은 사슬 공간에 5회 감아 올리는 퍼프를 3개 만드세요.", success_check="세 퍼프의 크기와 높이가 비슷한가요?",
        motion="yarn over and pull up five equally tall loops from one space, then close them together and secure with one chain",
        aliases=["긴 고리 구슬뜨기", "퍼프뜨기", "퍼프", "puff stitch", "puff"], prerequisites=["half-double-crochet"], related_slugs=["three-dc-cluster", "popcorn-stitch"],
    ),
    "팝콘뜨기(popcorn stitch)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="같은 위치에 완성한 여러 한길긴뜨기의 첫 코와 끝 코를 연결해 앞으로 튀어나오게 합니다.",
        steps=["같은 위치에 한길긴뜨기 5코를 완성합니다.", "바늘을 빼 첫 번째 코 머리에 앞에서 넣습니다.", "마지막 고리를 끌어와 첫 코 사이로 통과시킵니다."],
        mistake="미완성 코를 모아 클러스터처럼 뜸", fix="한길긴뜨기 5코를 각각 완전히 마친 뒤 첫 코와 마지막 코를 연결합니다.",
        slug="popcorn-stitch", abbreviation="5-dc pc", symbol_key="popcorn_stitch",
        learning_goal="완성된 다섯 기둥을 연결해 단단하고 둥근 입체 무늬를 만듭니다.",
        practice="한길긴뜨기 바탕에 팝콘 3개를 같은 간격으로 배치하세요.", success_check="무늬가 앞면으로 둥글게 돌출되고 다섯 기둥이 보이나요?",
        motion="complete five double crochets in one space, remove hook, insert into the first stitch, and pull the final loop through",
        aliases=["팝콘뜨기", "팝콘", "popcorn stitch", "popcorn", "pc"], prerequisites=["double-crochet"], related_slugs=["puff-stitch", "shell-stitch"],
    ),
    "조개뜨기(shell stitch)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="같은 위치에 한길긴뜨기 2코, 사슬 1코, 한길긴뜨기 2코를 넣어 조개 모양을 만드는 변형입니다. 조개뜨기의 코 구성은 도안마다 달라질 수 있습니다.",
        steps=["도안이 지정한 사슬 공간이나 코를 찾습니다.", "같은 위치에 한길긴뜨기 2코를 완성하고 사슬 1코를 뜹니다.", "같은 위치에 한길긴뜨기 2코를 더 완성합니다."],
        mistake="양쪽 한길긴뜨기를 서로 다른 코에 나누어 떠 조개 모양이 사라짐", fix="네 기둥의 밑부분이 모두 같은 한 점에서 시작하고 가운데 사슬 공간이 있는지 확인합니다.",
        slug="shell-stitch", abbreviation="2 dc, ch 1, 2 dc", symbol_key="shell_stitch", symbol_kind="learning", abbreviation_standard=False,
        learning_goal="한 지점에서 양쪽으로 펼쳐지고 가운데 사슬 공간이 있는 조개무늬를 만듭니다.",
        practice="사슬 바탕에 (한길긴뜨기 2코, 사슬 1코, 한길긴뜨기 2코) 조개를 3개 배치하세요.", success_check="각 조개의 네 기둥이 한 밑점에서 시작하고 가운데 사슬 공간이 보이나요?",
        motion="work two double crochets, chain one, and two more double crochets into the same stitch or chain space",
        aliases=["조개뜨기", "쉘뜨기", "조개무늬", "shell stitch", "2 dc ch 1 2 dc shell", "5-dc shell"], prerequisites=["double-crochet"], related_slugs=["popcorn-stitch"],
    ),
    "덮어씌워 코막음(basic bind off)": _expanded_entry(
        tool_type="needle_knitting", difficulty="beginner", category="finishing",
        description="새 코를 하나 뜬 뒤 앞의 코를 덮어씌우는 동작을 반복해 풀리지 않는 가장자리를 만드는 기본 코막음입니다.",
        steps=["첫 두 코를 도안대로 뜹니다.", "오른바늘의 첫 코를 두 번째 코 위로 넘깁니다.", "한 코를 더 뜨고 넘기는 동작을 끝까지 반복합니다."],
        mistake="너무 조여 가장자리가 오므라듦", fix="코를 바늘 몸통에서 크게 만들고 필요하면 한 호수 큰 바늘을 사용합니다.",
        slug="bind-off", abbreviation="BO", symbol_key="bind_off", symbol_standard=False,
        learning_goal="편물 폭을 유지하면서 탄력이 고른 마감 가장자리를 만듭니다.",
        practice="15코 샘플을 느슨하게 코 막음하고 편물 폭과 비교하세요.", success_check="마감선이 당기지 않고 편물 폭만큼 자연스럽게 늘어나나요?",
        motion="knit two stitches, lift the first stitch over the second and off the needle, then knit one more stitch and repeat",
        aliases=["덮어씌워 코막음", "코 막음", "코막음", "basic bind off", "bind off", "cast off", "BO"], prerequisites=["knit-stitch"], related_slugs=["casting-on"],
    ),
    "메리야스뜨기(stockinette stitch)": _expanded_entry(
        tool_type="needle_knitting", difficulty="beginner", category="texture",
        description="평면에서 겉면은 겉뜨기, 뒷면은 안뜨기로 반복해 매끈한 V 조직을 만듭니다.",
        steps=["겉면 한 단을 모두 겉뜨기합니다.", "편물을 돌려 뒷면 한 단을 모두 안뜨기합니다.", "두 단을 반복합니다."],
        mistake="단의 앞뒷면을 놓쳐 가터 능선이 생김", fix="겉면의 V와 뒷면의 가로 마디를 확인한 뒤 단을 시작합니다.",
        slug="stockinette-stitch", abbreviation="St st", symbol_key="stockinette", symbol_standard=False,
        learning_goal="앞뒷면을 구분해 매끈한 V가 이어지는 기본 편물을 만듭니다.",
        practice="16코로 메리야스뜨기 10단을 뜨세요.", success_check="겉면에 V가 세로로 이어지고 홀수·짝수 단이 섞이지 않았나요?",
        motion="knit one full right-side row, turn the work, then purl the wrong-side row to reveal stockinette fabric",
        aliases=["메리야스뜨기", "메리야스", "stockinette stitch", "stockinette", "St st"], prerequisites=["knit-stitch", "purl-stitch"], related_slugs=["garter-stitch"],
    ),
    "가터뜨기(garter stitch)": _expanded_entry(
        tool_type="needle_knitting", difficulty="beginner", category="texture",
        description="평면의 모든 단을 겉뜨기해 양면에 고른 가로 능선을 만드는 조직입니다.",
        steps=["첫 단을 끝까지 겉뜨기합니다.", "편물을 돌리고 다음 단도 겉뜨기합니다.", "원하는 길이까지 같은 동작을 반복합니다."],
        mistake="단을 빠뜨려 능선 간격이 달라짐", fix="가터 능선 하나가 두 단이라는 점을 기억하고 단수 마커를 사용합니다.",
        slug="garter-stitch", abbreviation="Garter st", symbol_key="garter", symbol_standard=False,
        learning_goal="양면이 같고 가장자리가 말리지 않는 균일한 능선 조직을 만듭니다.",
        practice="15코로 가터뜨기 10단을 뜨고 능선 수를 세세요.", success_check="앞뒤 모두 같은 질감이며 가터 능선이 5줄 보이나요?",
        motion="knit every stitch across, turn the fabric, and knit every stitch back to form two garter ridges",
        aliases=["가터뜨기", "가터", "garter stitch", "garter"], prerequisites=["knit-stitch"], related_slugs=["stockinette-stitch"],
    ),
    "멍석뜨기(seed stitch)": _expanded_entry(
        tool_type="needle_knitting", difficulty="confident_beginner", category="texture",
        description="겉뜨기와 안뜨기를 한 코씩 번갈아 배치하고 다음 단에서 반대로 떠 오톨도톨한 조직을 만듭니다.",
        steps=["첫 단에서 겉뜨기 1코와 안뜨기 1코를 반복합니다.", "다음 단에서는 겉코 위에 안뜨기, 안코 위에 겉뜨기를 합니다.", "실을 바늘 사이로 옮기며 반복합니다."],
        mistake="아래 코와 같은 성질로 떠 고무뜨기 골이 생김", fix="V 모양 겉코에는 안뜨기, 마디 모양 안코에는 겉뜨기를 합니다.",
        slug="seed-stitch", abbreviation="Seed st", symbol_key="seed_stitch", symbol_standard=False,
        learning_goal="매 단 코의 성질을 반대로 떠 균일한 점 질감을 만듭니다.",
        practice="짝수 16코로 멍석뜨기 8단을 뜨세요.", success_check="세로 골 없이 겉·안 코가 바둑판처럼 번갈아 보이나요?",
        motion="knit one, move yarn between needles, purl one, turn, then work the opposite stitch over each stitch",
        aliases=["멍석뜨기", "씨드뜨기", "seed stitch", "moss stitch"], prerequisites=["knit-stitch", "purl-stitch"], related_slugs=["ribbing"],
    ),
    "바늘비우기(yarn over)": _expanded_entry(
        tool_type="needle_knitting", difficulty="confident_beginner", category="shaping",
        description="작업실을 바늘에 한 번 감아 다음 단에 구멍이 있는 새 코를 만드는 늘림 기법입니다.",
        steps=["도안의 YO 위치까지 뜹니다.", "작업실을 오른바늘 위로 한 번 감습니다.", "다음 코를 뜨며 감긴 실을 새 코로 유지합니다."],
        mistake="다음 코를 뜰 때 감긴 실이 풀려 늘림이 사라짐", fix="감긴 실을 오른바늘 몸통에 유지한 채 다음 코에 바늘을 넣습니다.",
        slug="yarn-over", abbreviation="YO", symbol_key="yarn_over",
        learning_goal="의도적인 구멍과 한 코 늘림을 동시에 만듭니다.",
        practice="겉뜨기 사이에 YO를 5번 넣고 다음 단에서 모두 떠 보세요.", success_check="다음 단에 구멍 5개와 새 코 5개가 생겼나요?",
        motion="bring the working yarn over the right needle once and keep the wrap in place while knitting the next stitch",
        aliases=["바늘비우기", "바늘 비우기", "yarn over", "YO"], prerequisites=["knit-stitch"], related_slugs=["k2tog", "ssk"],
    ),
    "KFB 늘림(knit front and back)": _expanded_entry(
        tool_type="needle_knitting", difficulty="confident_beginner", category="shaping",
        description="한 코의 앞고리와 뒤고리를 차례로 겉뜨기해 한 코를 두 코로 늘립니다.",
        steps=["한 코의 앞고리로 겉뜨기하되 헌 코를 빼지 않습니다.", "오른바늘을 같은 코의 뒤고리에 넣어 다시 겉뜨기합니다.", "헌 코를 왼바늘에서 뺍니다."],
        mistake="첫 코 뒤에 헌 코를 빼 두 번째 코를 만들지 못함", fix="앞고리 코를 만든 뒤 헌 코가 왼바늘에 남아 있는지 확인합니다.",
        slug="knit-front-back", abbreviation="kfb", symbol_key="kfb",
        learning_goal="한 코를 유지한 채 앞뒤 고리에서 두 코를 만들어 안정적으로 늘립니다.",
        practice="10코 샘플에서 매 두 코마다 kfb를 해 코 수를 세세요.", success_check="늘림 한 번마다 전체 코 수가 정확히 하나씩 증가했나요?",
        motion="knit into the front of one stitch without dropping it, knit into its back loop, then slide the old stitch off",
        aliases=["KFB 늘림", "앞뒤뜨기 늘림", "knit front and back", "kfb"], prerequisites=["knit-stitch"], related_slugs=["make-one-left", "make-one-right"],
    ),
    "왼코 늘림(make one left)": _expanded_entry(
        tool_type="needle_knitting", difficulty="intermediate", category="shaping",
        description="두 코 사이 가로실을 앞에서 들어 올려 뒤고리로 떠 왼쪽으로 기우는 새 코를 만듭니다.",
        steps=["왼바늘로 두 코 사이 가로실을 앞에서 뒤로 들어 올립니다.", "들어 올린 가로실의 뒤고리에 오른바늘을 넣습니다.", "겉뜨기해 한 코를 만듭니다."],
        mistake="가로실을 열린 방향으로 떠 큰 구멍이 생김", fix="뒤고리를 떠 가로실이 비틀리며 닫히는지 확인합니다.",
        slug="make-one-left", abbreviation="M1L", symbol_key="m1l",
        learning_goal="구멍을 최소화하며 왼쪽 기울기의 한 코 늘림을 만듭니다.",
        practice="중앙 마커 양옆 중 왼쪽 위치에 M1L을 4단 반복하세요.", success_check="늘림선이 왼쪽으로 기울고 큰 구멍이 없나요?",
        motion="lift the bar between stitches from front to back with the left needle and knit through its back loop",
        aliases=["왼코 늘림", "왼쪽 늘림", "make one left", "M1L"], prerequisites=["knit-stitch"], related_slugs=["make-one-right"],
    ),
    "오른코 늘림(make one right)": _expanded_entry(
        tool_type="needle_knitting", difficulty="intermediate", category="shaping",
        description="두 코 사이 가로실을 뒤에서 들어 올려 앞고리로 떠 오른쪽으로 기우는 새 코를 만듭니다.",
        steps=["왼바늘로 두 코 사이 가로실을 뒤에서 앞으로 들어 올립니다.", "들어 올린 가로실의 앞고리에 오른바늘을 넣습니다.", "겉뜨기해 한 코를 만듭니다."],
        mistake="M1L과 같은 방향으로 가로실을 들어 올림", fix="M1R은 왼바늘이 가로실 뒤에서 앞으로 들어오는지 확인합니다.",
        slug="make-one-right", abbreviation="M1R", symbol_key="m1r",
        learning_goal="구멍을 최소화하며 오른쪽 기울기의 한 코 늘림을 만듭니다.",
        practice="중앙 마커 양옆 중 오른쪽 위치에 M1R을 4단 반복하세요.", success_check="늘림선이 오른쪽으로 기울고 M1L과 대칭인가요?",
        motion="lift the bar between stitches from back to front with the left needle and knit through its front loop",
        aliases=["오른코 늘림", "오른쪽 늘림", "make one right", "M1R"], prerequisites=["knit-stitch"], related_slugs=["make-one-left"],
    ),
    "겉뜨기 2코 모아뜨기(knit 2 together)": _expanded_entry(
        tool_type="needle_knitting", difficulty="confident_beginner", category="shaping",
        description="두 코를 동시에 겉뜨기해 오른쪽으로 기우는 한 코 줄임을 만듭니다.",
        steps=["오른바늘을 왼바늘의 앞쪽 두 코에 함께 넣습니다.", "두 코를 한 코처럼 겉뜨기합니다.", "헌 코 두 개를 함께 왼바늘에서 뺍니다."],
        mistake="한 코만 바늘에 걸려 줄어들지 않음", fix="뜨기 전 오른바늘 위에 두 코의 앞고리가 모두 걸렸는지 확인합니다.",
        slug="k2tog", abbreviation="k2tog", symbol_key="k2tog",
        learning_goal="두 코를 한 번에 떠 오른쪽 기울기의 깔끔한 줄임선을 만듭니다.",
        practice="12코에서 k2tog를 6번 떠 코 수를 확인하세요.", success_check="6코가 남고 줄임선이 오른쪽으로 기울었나요?",
        motion="insert the right needle through the front of two adjacent stitches together and knit them as one stitch",
        aliases=["겉뜨기 2코 모아뜨기", "두 코 모아 겉뜨기", "knit 2 together", "k2tog"], prerequisites=["knit-stitch"], related_slugs=["ssk", "yarn-over"],
    ),
    "걸러 겉뜨기 2코 모아뜨기(slip slip knit)": _expanded_entry(
        tool_type="needle_knitting", difficulty="intermediate", category="shaping",
        description="두 코를 하나씩 걸러 방향을 바꾼 뒤 함께 떠 왼쪽으로 기우는 줄임을 만듭니다.",
        steps=["첫 코와 둘째 코를 각각 겉뜨기 방향으로 오른바늘에 옮깁니다.", "왼바늘을 두 코 앞쪽에 넣습니다.", "두 코를 뒤고리 방향으로 함께 겉뜨기합니다."],
        mistake="두 코를 한 번에 걸러 코 방향이 고르지 않음", fix="각 코를 하나씩 따로 겉뜨기 방향으로 옮깁니다.",
        slug="ssk", abbreviation="SSK", symbol_key="ssk",
        learning_goal="코 방향을 정리해 왼쪽으로 기우는 대칭 줄임선을 만듭니다.",
        practice="YO-K2tog와 YO-SSK를 좌우에 배치해 대칭 레이스 샘플을 만드세요.", success_check="SSK 줄임이 왼쪽으로 기울며 K2tog와 대칭인가요?",
        motion="slip two stitches one at a time knitwise, insert the left needle into their fronts, and knit them together through the back",
        aliases=["걸러 겉뜨기 2코 모아뜨기", "왼코 줄임", "slip slip knit", "SSK"], prerequisites=["knit-stitch"], related_slugs=["k2tog", "yarn-over"],
    ),
    "안뜨기 2코 모아뜨기(purl 2 together)": _expanded_entry(
        tool_type="needle_knitting", difficulty="confident_beginner", category="shaping",
        description="실을 앞에 두고 두 코를 동시에 안뜨기해 한 코를 줄입니다.",
        steps=["작업실을 편물 앞에 둡니다.", "오른바늘을 두 코에 함께 안뜨기 방향으로 넣습니다.", "두 코를 한 코처럼 안뜨기하고 함께 뺍니다."],
        mistake="첫 코만 잡거나 작업실이 뒤에 남음", fix="바늘을 넣기 전 실이 앞에 있고 두 코가 모두 바늘에 걸렸는지 확인합니다.",
        slug="p2tog", abbreviation="p2tog", symbol_key="p2tog",
        learning_goal="안뜨기 면에서 두 코를 하나로 모아 자연스럽게 줄입니다.",
        practice="안뜨기 12코에서 p2tog를 6번 반복하세요.", success_check="6코가 남고 안뜨기 질감이 끊기지 않았나요?",
        motion="hold yarn in front, insert the right needle purlwise through two adjacent stitches, and purl them together",
        aliases=["안뜨기 2코 모아뜨기", "두 코 모아 안뜨기", "purl 2 together", "p2tog"], prerequisites=["purl-stitch"], related_slugs=["k2tog"],
    ),
    "안뜨기 방향 걸러뜨기(slip 1 purlwise wyib)": _expanded_entry(
        tool_type="needle_knitting", difficulty="confident_beginner", category="texture",
        description="작업실을 뒤에 두고 코를 안뜨기 방향으로 옮기는 구체적인 걸러뜨기 방법입니다.",
        steps=["작업실을 편물 뒤에 둡니다(wyib).", "오른바늘을 다음 코에 안뜨기 방향으로 넣습니다.", "실을 감지 않고 코만 오른바늘로 옮깁니다."],
        mistake="실 위치가 달라 편물 앞에 불필요한 가로실이 생김", fix="wyif·wyib 지시를 확인하고 코를 옮기기 전에 실부터 배치합니다.",
        slug="slip-stitch-knitting", abbreviation="sl1p wyib", symbol_key="slip_knit", symbol_standard=False,
        symbol_kind="learning",
        learning_goal="코 방향과 실 위치를 유지하며 한 코를 안전하게 옮깁니다.",
        practice="가터 바탕에서 매 단 첫 코를 안뜨기 방향으로 걸러 가장자리를 비교하세요.", success_check="걸러진 코가 꼬이지 않고 가장자리 사슬이 고르게 보이나요?",
        motion="hold yarn in back and transfer one stitch purlwise from the left needle to the right needle without knitting it",
        aliases=["걸러뜨기", "코 걸러뜨기", "안뜨기 방향 걸러뜨기", "slip stitch knitting", "sl 1", "sl1p", "wyib"], prerequisites=["knit-stitch"], related_slugs=["seed-stitch"],
    ),
    "코 줍기(pick up stitches)": _expanded_entry(
        tool_type="needle_knitting", difficulty="intermediate", category="construction",
        description="완성된 편물 가장자리에서 새 고리를 끌어올려 칼라나 소매를 이어 뜨는 기법입니다.",
        steps=["가장자리에서 코를 주울 간격을 표시합니다.", "오른바늘을 가장자리 코 아래에 넣습니다.", "작업실을 걸어 앞쪽으로 끌어와 새 코를 만듭니다."],
        mistake="간격이 고르지 않아 가장자리가 울거나 당김", fix="전체 구간을 먼저 4등분해 각 구간의 코 수를 균등하게 배치합니다.",
        slug="pick-up-stitches", abbreviation="pu", symbol_key="pick_up", symbol_standard=False,
        learning_goal="가장자리 길이에 맞는 비율로 코를 고르게 주워 연결부를 평평하게 만듭니다.",
        practice="가터 샘플 옆선 10cm에 8코를 같은 간격으로 주워 보세요.", success_check="주운 코 사이 간격이 같고 가장자리가 울지 않나요?",
        motion="insert the right needle under an edge strand, wrap working yarn, and pull a new loop through onto the needle",
        aliases=["코 줍기", "코줍기", "pick up stitches", "pick up", "pu"], prerequisites=["knit-stitch"], related_slugs=["join-in-round"],
    ),
    "원형 연결(join in the round)": _expanded_entry(
        tool_type="needle_knitting", difficulty="intermediate", category="construction",
        description="잡은 코가 꼬이지 않게 정렬한 뒤 첫 코와 마지막 코를 연결해 원통형 편물을 시작합니다.",
        steps=["모든 코의 밑단이 바늘 안쪽을 향하게 정렬합니다.", "첫 코 앞에 단 시작 마커를 놓습니다.", "첫 코를 떠 마지막 코와 연결하고 작업실을 조입니다."],
        mistake="코잡기 가장자리가 한 번 비틀린 채 연결됨", fix="연결 전 케이블 전체를 따라 코 밑단 방향을 한 바퀴 확인합니다.",
        slug="join-in-round", abbreviation="join rnd", symbol_key="join_round", symbol_standard=False,
        learning_goal="코가 비틀리지 않은 원형 편물을 만들고 단 시작점을 유지합니다.",
        practice="원형바늘에 24코를 잡아 비틀림 없이 연결하고 3단 뜨세요.", success_check="코잡기 가장자리가 한 방향이고 마커가 단 시작에 있나요?",
        motion="spread cast-on stitches around a circular needle, confirm the edge faces inward, place a marker, and knit the first stitch",
        aliases=["원형 연결", "원형뜨기 연결", "join in the round", "join rnd"], prerequisites=["casting-on", "knit-stitch"], related_slugs=["pick-up-stitches"],
    ),
    "2×2 오른쪽 케이블(2/2 right cross)": _expanded_entry(
        tool_type="needle_knitting", difficulty="intermediate", category="texture",
        description="두 코를 보조바늘에 뒤로 두고 다음 두 코를 먼저 떠 네 코가 오른쪽으로 교차하게 합니다.",
        steps=["앞의 두 코를 보조바늘에 옮겨 편물 뒤에 둡니다.", "왼바늘의 다음 두 코를 겉뜨기합니다.", "보조바늘의 두 코를 겉뜨기합니다."],
        mistake="보조바늘을 앞에 두어 교차 방향이 반대가 됨", fix="오른쪽 교차는 보조바늘을 편물 뒤에 둔다는 규칙을 확인합니다.",
        slug="two-by-two-right-cable", abbreviation="2/2 RC", symbol_key="cable_right",
        learning_goal="네 코를 빠뜨리지 않고 오른쪽으로 선명하게 교차시킵니다.",
        practice="메리야스 바탕 중앙 4코에 6단마다 2/2 RC를 두 번 만드세요.", success_check="케이블이 오른쪽 위로 기울고 전체 코 수가 유지되나요?",
        motion="slip two stitches to a cable needle held in back, knit the next two, then knit the two from the cable needle",
        aliases=["오른쪽 케이블", "오른코 교차", "2/2 right cross", "2/2 RC", "C4B"], prerequisites=["knit-stitch"], related_slugs=["two-by-two-left-cable"],
    ),
    "2×2 왼쪽 케이블(2/2 left cross)": _expanded_entry(
        tool_type="needle_knitting", difficulty="intermediate", category="texture",
        description="두 코를 보조바늘에 앞으로 두고 다음 두 코를 먼저 떠 네 코가 왼쪽으로 교차하게 합니다.",
        steps=["앞의 두 코를 보조바늘에 옮겨 편물 앞에 둡니다.", "왼바늘의 다음 두 코를 겉뜨기합니다.", "보조바늘의 두 코를 겉뜨기합니다."],
        mistake="보조바늘을 뒤에 두어 교차 방향이 반대가 됨", fix="왼쪽 교차는 보조바늘을 편물 앞에 둔다는 규칙을 확인합니다.",
        slug="two-by-two-left-cable", abbreviation="2/2 LC", symbol_key="cable_left",
        learning_goal="네 코를 빠뜨리지 않고 왼쪽으로 선명하게 교차시킵니다.",
        practice="메리야스 바탕 중앙 4코에 6단마다 2/2 LC를 두 번 만드세요.", success_check="케이블이 왼쪽 위로 기울고 전체 코 수가 유지되나요?",
        motion="slip two stitches to a cable needle held in front, knit the next two, then knit the two from the cable needle",
        aliases=["왼쪽 케이블", "왼코 교차", "2/2 left cross", "2/2 LC", "C4F"], prerequisites=["knit-stitch"], related_slugs=["two-by-two-right-cable"],
    ),
}

_EXPANDED_TECHNIQUE_REFERENCES: dict[str, dict] = {
    "시작 고리(slip knot)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=3WTjfJ2bohk", "title": "쎄비 코바늘 기초 · 실과 바늘 잡는 법부터 시작하기", "focus": "초반의 시작 고리에서 교차점과 당기면 조절되는 고리를 확인합니다."}],
        "reference_cards": _reference_cards("slip-knot", [
            ("실로 원 만들기", "꼬리실을 충분히 남기고 작업실을 둥글게 말아 원을 만듭니다."),
            ("실 교차하기", "꼬리실과 작업실이 만나는 지점을 교차해 손가락으로 고정합니다."),
            ("고리 안으로 바늘 넣기", "교차점이 풀리지 않게 잡은 채 코바늘을 원 안으로 넣습니다."),
            ("작업실 잡기", "원 뒤쪽의 작업실 한 가닥을 바늘 홈으로 잡습니다."),
            ("새 고리 끌어오기", "잡은 작업실을 원 안으로 끌어와 조절 가능한 새 고리를 만듭니다."),
            ("바늘 굵기에 맞추기", "꼬리실을 당겨 고리를 바늘 몸통에 맞추되 부드럽게 움직일 여유를 남깁니다."),
        ]),
    },
    "두길긴뜨기(treble crochet)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=1vj-XcZVSTQ", "title": "쎄비 코바늘 기초 · 두길긴뜨기", "focus": "실을 두 번 감아 네 고리를 만든 뒤 두 고리씩 세 번 빼는 순서를 확인합니다."}],
        "reference_cards": _reference_cards("treble-crochet", [
            ("기둥 높이 준비", "완성 사슬 또는 앞 단을 잡고 다음 코의 삽입 위치를 확인합니다."),
            ("실 두 번 감기", "코에 넣기 전에 작업실을 바늘 몸통에 정확히 두 번 감습니다."),
            ("다음 코에 넣기", "두 번 감은 실이 풀리지 않도록 잡고 다음 코 아래로 바늘을 넣습니다."),
            ("네 고리 만들기", "작업실을 끌어오면 활성 고리를 포함해 바늘 위에 고리 네 개가 생깁니다."),
            ("첫 두 고리 통과", "실을 걸어 앞쪽 두 고리만 통과하고 나머지 고리는 바늘에 남깁니다."),
            ("둘째 두 고리 통과", "다시 실을 걸어 앞쪽 두 고리를 한 번 더 통과합니다."),
            ("마지막 두 고리 통과", "실을 다시 걸어 남은 두 고리를 통과해 높은 기둥코를 완성합니다."),
            ("높이와 머리 확인", "바늘 위에는 활성 고리 하나만 남고 긴 기둥과 V 머리가 생겼는지 봅니다."),
        ]),
    },
    "짧은뜨기 늘려뜨기(single crochet increase)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=SUFDWzzYE9I", "title": "쎄비 코바늘 기초 · 짧은뜨기 코 늘리기와 줄이기", "focus": "한 밑코에 짧은뜨기 두 코를 넣어 V 머리 두 개가 생기는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("single-crochet-increase", [
            ("늘릴 한 코 찾기", "짧은뜨기 두 개를 함께 넣을 같은 V 머리를 확인합니다."),
            ("첫 짧은뜨기 완성", "선택한 코에 평소처럼 짧은뜨기 한 코를 완성합니다."),
            ("같은 코에 다시 넣기", "다음 코로 이동하지 않고 방금 사용한 동일한 구멍에 바늘을 다시 넣습니다."),
            ("두 고리 만들기", "작업실을 끌어와 바늘 위에 고리 두 개를 만듭니다."),
            ("둘째 짧은뜨기 완성", "실을 걸어 두 고리를 통과해 같은 밑코의 두 번째 짧은뜨기를 완성합니다."),
            ("두 V 머리 확인", "하나의 밑코에서 두 개의 V 머리가 갈라져 나오는지 확인합니다."),
        ]),
    },
    "짧은뜨기 2코 모아뜨기(single crochet 2 together)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=SUFDWzzYE9I", "title": "쎄비 코바늘 기초 · 짧은뜨기 코 늘리기와 줄이기", "focus": "이웃한 두 코에서 고리를 차례로 끌어와 세 고리를 함께 빼는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("single-crochet-decrease", [
            ("모을 두 코 찾기", "하나로 합칠 이웃한 두 코의 V 머리를 차례로 확인합니다."),
            ("첫 코에 넣기", "첫 번째 코 아래로 바늘을 넣습니다."),
            ("첫 고리 끌어오기", "작업실을 끌어오되 짧은뜨기를 끝내지 않고 고리 두 개를 남깁니다."),
            ("다음 코에 넣기", "미완성 고리를 바늘에 둔 채 바로 다음 코 아래로 바늘을 넣습니다."),
            ("세 고리 만들기", "두 번째 코에서 작업실을 끌어와 바늘 위 고리 세 개를 확인합니다."),
            ("세 고리 함께 통과", "실을 걸어 바늘 위 세 고리를 한 번에 통과합니다."),
            ("한 V 머리 확인", "두 밑코 위에 완성된 코 머리가 하나만 남아 코 수가 하나 줄었는지 봅니다."),
        ]),
    },
    "한길긴뜨기 2코 모아뜨기(double crochet 2 together)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=1SIkM7Mh150", "title": "쎄비 코바늘 기초 · 한길긴뜨기 코 늘리기와 줄이기", "focus": "두 기둥을 각각 미완성으로 남긴 뒤 마지막 세 고리를 함께 빼는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("double-crochet-decrease", [
            ("모을 두 코 준비", "이웃한 두 코를 확인하고 첫 한길긴뜨기를 위해 실을 한 번 감습니다."),
            ("첫 코에 넣기", "첫 번째 코 아래로 바늘을 넣고 작업실을 끌어옵니다."),
            ("첫 세 고리 확인", "바늘 위에 생긴 세 고리에서 첫 한길긴뜨기를 시작합니다."),
            ("첫 코 미완성으로 남기기", "실을 걸어 두 고리만 빼고 마지막 고리는 바늘에 남깁니다."),
            ("둘째 코에 넣기", "다시 실을 감아 바로 다음 코에 바늘을 넣습니다."),
            ("둘째 고리 끌어오기", "작업실을 끌어와 두 번째 한길긴뜨기의 고리를 만듭니다."),
            ("둘째 코도 미완성", "실을 걸어 앞쪽 두 고리만 빼면 바늘 위에 마지막 고리 세 개가 남습니다."),
            ("세 고리 함께 마무리", "실을 걸어 남은 세 고리를 한 번에 통과해 두 기둥을 한 머리로 모읍니다."),
        ]),
    },
    "앞고리에만 뜨기(front loop only)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=0sq_Zw96qAE", "title": "앵콜스 코바늘 왕초보 · 앞이랑뜨기(FLO)와 뒤이랑뜨기(BLO)", "focus": "V 머리의 몸 쪽 앞고리 한 가닥에만 바늘을 넣고 남은 뒤고리가 선으로 이어지는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("front-loop-only", [
            ("V 머리 두 가닥 확인", "다음 코의 V 머리를 이루는 앞고리와 뒤고리 두 가닥을 먼저 구분합니다."),
            ("앞고리 한 가닥에 넣기", "몸 쪽 앞고리 한 가닥 아래에만 바늘을 넣고 뒤고리는 남겨 둡니다."),
            ("작업실 끌어오기", "앞고리만 잡은 상태에서 작업실을 걸어 고리 하나를 끌어옵니다."),
            ("짧은뜨기 완성", "실을 다시 걸어 바늘 위 두 고리를 통과해 짧은뜨기를 완성합니다."),
            ("남은 뒤고리 선 확인", "여러 코를 뜬 뒤 사용하지 않은 뒤고리가 가로선처럼 이어지는지 확인합니다."),
        ]),
    },
    "뒤고리에만 뜨기(back loop only)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=0sq_Zw96qAE", "title": "앵콜스 코바늘 왕초보 · 앞이랑뜨기(FLO)와 뒤이랑뜨기(BLO)", "focus": "V 머리의 몸에서 먼 뒤고리 한 가닥에만 바늘을 넣고 남은 앞고리가 능선을 만드는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("back-loop-only", [
            ("V 머리 두 가닥 확인", "다음 코의 V 머리를 이루는 앞고리와 뒤고리 두 가닥을 먼저 구분합니다."),
            ("뒤고리 한 가닥에 넣기", "몸에서 먼 뒤고리 한 가닥 아래에만 바늘을 넣고 앞고리는 남겨 둡니다."),
            ("작업실 끌어오기", "뒤고리만 잡은 상태에서 작업실을 걸어 고리 하나를 끌어옵니다."),
            ("짧은뜨기 완성", "실을 다시 걸어 바늘 위 두 고리를 통과해 짧은뜨기를 완성합니다."),
            ("남은 앞고리 능선 확인", "여러 코를 뜬 뒤 사용하지 않은 앞고리가 도드라진 능선으로 이어지는지 확인합니다."),
        ]),
    },
    "앞걸어 한길긴뜨기(front post double crochet)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=Yo4Fh1INwVQ", "title": "뜨개하는엘 코바늘 기초 · 앞걸어뜨기와 뒤걸어뜨기", "focus": "코 머리가 아닌 기둥을 앞→뒤→앞으로 감싸 한길긴뜨기를 완성하는 손동작을 확인합니다."}],
        "reference_cards": _reference_cards("front-post-double-crochet", [
            ("실 한 번 감기", "한길긴뜨기 높이를 만들기 위해 작업실을 바늘에 한 번 감습니다."),
            ("감쌀 기둥 찾기", "코 머리 아래에서 세로로 내려오는 다음 코의 기둥을 찾습니다."),
            ("앞에서 뒤로 넣기", "기둥 오른쪽에서 바늘을 편물 앞면에서 뒷면으로 넣습니다."),
            ("뒤에서 다시 앞으로", "기둥 뒤를 지나 왼쪽 틈으로 바늘을 다시 앞면에 뺍니다."),
            ("기둥 둘레로 고리 끌기", "기둥을 감싼 채 작업실을 끌어와 바늘 위 고리 세 개를 만듭니다."),
            ("솟은 기둥코 완성", "한길긴뜨기처럼 두 고리씩 두 번 빼 기둥이 앞쪽으로 도드라지는지 확인합니다."),
        ]),
    },
    "뒤걸어 한길긴뜨기(back post double crochet)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=Yo4Fh1INwVQ", "title": "뜨개하는엘 코바늘 기초 · 앞걸어뜨기와 뒤걸어뜨기", "focus": "편물 뒤에서 기둥을 뒤→앞→뒤로 감싸 한길긴뜨기를 완성하는 손동작을 확인합니다."}],
        "reference_cards": _reference_cards("back-post-double-crochet", [
            ("실 한 번 감기", "한길긴뜨기 높이를 만들기 위해 작업실을 바늘에 한 번 감습니다."),
            ("감쌀 기둥 찾기", "편물 뒤쪽에서 감쌀 코 기둥과 양옆 틈을 확인합니다."),
            ("뒤에서 앞으로 넣기", "기둥 오른쪽 틈으로 바늘을 편물 뒷면에서 앞면으로 넣습니다."),
            ("기둥을 바늘 뒤에 두기", "기둥 앞을 가로지르며 기둥이 바늘 몸통 뒤에 놓이게 합니다."),
            ("앞에서 다시 뒤로", "기둥 왼쪽 틈을 통해 바늘 끝을 편물 뒷면으로 되돌립니다."),
            ("기둥 둘레로 고리 끌기", "작업실을 걸어 기둥 둘레로 고리를 끌어와 바늘 위 고리 세 개를 만듭니다."),
            ("들어간 기둥코 완성", "한길긴뜨기처럼 두 고리씩 두 번 빼 앞면에서 기둥이 들어가 보이는지 확인합니다."),
        ]),
    },
    "한길긴뜨기 3코 구슬뜨기(3-dc cluster)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=XtA-E7_oZyw", "title": "하다코바늘 코바늘 기초 · 한길긴뜨기 3코 구슬뜨기", "focus": "한길긴뜨기 세 코를 각각 미완성으로 남겨 네 고리를 한 번에 닫는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("three-dc-cluster", [
            ("첫 코를 시작할 위치", "세 기둥을 함께 넣을 한 코 또는 사슬 공간을 확인하고 실을 한 번 감습니다."),
            ("첫 기둥 미완성", "첫 한길긴뜨기에서 두 고리만 빼고 마지막 고리를 바늘에 남깁니다."),
            ("둘째 기둥 시작", "실을 다시 감아 같은 위치에 넣고 두 번째 고리를 끌어옵니다."),
            ("둘째 기둥도 미완성", "앞쪽 두 고리만 빼 두 기둥의 마지막 고리를 바늘에 남깁니다."),
            ("셋째 기둥 시작", "같은 위치에서 세 번째 한길긴뜨기를 시작합니다."),
            ("기둥 3개·고리 4개 확인", "세 기둥은 미완성이고 바늘 위에는 닫을 고리 네 개가 남았는지 봅니다."),
            ("모든 고리 닫기", "실을 걸어 남은 네 고리를 한 번에 통과시킵니다."),
            ("꼭짓점 하나 확인", "세 기둥이 하나의 코 머리로 모여 구슬 모양을 만드는지 확인합니다."),
        ]),
    },
    "긴 고리 구슬뜨기(puff stitch)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=G9Mt6p81MiM", "title": "쎄비 코바늘 기초과정 · 구슬뜨기(puff stitch)", "focus": "같은 위치에서 긴 고리를 반복해 끌어올리고 높이를 맞춘 뒤 한 번에 닫는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("puff-stitch", [
            ("실 한 번 감기", "긴 고리를 끌어올릴 준비로 작업실을 바늘에 감습니다."),
            ("같은 공간에 넣기", "도안이 지정한 한 코 또는 사슬 공간에 바늘을 넣습니다."),
            ("긴 고리 끌어올리기", "작업실을 걸어 기존 코 높이만큼 길고 느슨하게 고리를 끌어올립니다."),
            ("같은 위치에서 반복", "실 감기와 긴 고리 끌어올리기를 같은 위치에서 정해진 횟수만큼 반복합니다."),
            ("고리 높이 맞추기", "바늘에 모인 긴 고리들이 모두 같은 높이인지 확인합니다."),
            ("모인 고리 한 번에 닫기", "실을 걸어 모인 긴 고리 전체를 한 번에 통과시킵니다."),
            ("사슬로 고정", "사슬 1코로 퍼프를 고정하고 폭신한 덩어리가 고르게 솟았는지 봅니다."),
        ]),
    },
    "팝콘뜨기(popcorn stitch)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=bcwtWzCeHeI", "title": "쎄비 코바늘 기초과정 · 한길긴뜨기 5코 팝콘뜨기", "focus": "한길긴뜨기 다섯 코를 각각 완성한 뒤 첫 코 머리로 마지막 고리를 당겨 돌출시키는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("popcorn-stitch", [
            ("다섯 코를 넣을 위치", "한길긴뜨기 다섯 코를 모두 넣을 같은 코 또는 사슬 공간을 확인합니다."),
            ("첫 한길긴뜨기 완성", "선택한 위치에 첫 한길긴뜨기를 끝까지 완성합니다."),
            ("같은 위치에 계속 뜨기", "다음 코로 이동하지 않고 같은 위치에 완성된 한길긴뜨기를 더 만듭니다."),
            ("다섯 번째 코 완성", "같은 밑점에서 한길긴뜨기 다섯 코가 모두 완성됐는지 셉니다."),
            ("다섯 V 머리 확인", "미완성 고리가 아니라 서로 분리된 완성 코 머리 다섯 개가 있는지 확인합니다."),
            ("바늘을 빼 첫 코에 넣기", "활성 고리를 유지한 채 바늘을 빼고 첫 한길긴뜨기 머리에 앞에서 넣습니다."),
            ("마지막 고리 다시 걸기", "바늘에 마지막 활성 고리를 다시 걸어 빠지지 않게 잡습니다."),
            ("첫 코 사이로 당겨 완성", "마지막 고리를 첫 코 머리 사이로 당겨 무늬가 편물 앞쪽으로 둥글게 솟게 합니다."),
        ]),
    },
    "조개뜨기(shell stitch)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=Q9EDqOXGW_c", "title": "니뜨TV 코바늘 기초강좌 · 조개뜨기(쉘뜨기)", "focus": "같은 위치에 한길긴뜨기 2코, 사슬 1코, 한길긴뜨기 2코를 넣어 조개 모양을 만드는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("shell-stitch", [
            ("조개를 넣을 한 코", "네 기둥과 가운데 사슬을 모두 넣을 같은 밑코를 확인합니다."),
            ("첫 한길긴뜨기", "선택한 밑코에 첫 한길긴뜨기를 완성합니다."),
            ("같은 밑코에 둘째 코", "다음 코로 이동하지 않고 같은 밑코에 한길긴뜨기를 하나 더 완성합니다."),
            ("왼쪽 기둥 두 코 확인", "한 밑점에서 한길긴뜨기 두 기둥이 나란히 나오는지 봅니다."),
            ("가운데 사슬 1코", "사슬 1코를 떠 조개의 가운데 공간과 높이를 만듭니다."),
            ("같은 밑코로 돌아가기", "여전히 같은 밑코에 바늘을 넣어 반대쪽 기둥을 시작합니다."),
            ("한길긴뜨기 두 코 더", "같은 밑코에 한길긴뜨기 두 코를 차례로 완성합니다."),
            ("2코·사슬·2코 확인", "네 기둥이 한 밑점에서 펼쳐지고 가운데 사슬 공간이 보이는지 확인합니다."),
        ]),
    },
    "롱테일 코잡기(long-tail cast on)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=Sq4tSh4Kc7Y", "title": "쎄비 대바늘 기초 · 롱테일 코잡기", "focus": "엄지의 꼬리실 고리와 검지의 작업실을 이용해 같은 방향의 코를 반복해 만드는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("casting-on", [
            ("꼬리실 길이 준비", "필요한 코 수에 맞춰 꼬리실을 충분히 남기고 시작 고리를 바늘에 겁니다."),
            ("엄지·검지에 실 걸기", "엄지에는 꼬리실, 검지에는 작업실이 걸리도록 두 실을 벌려 잡습니다."),
            ("엄지 고리 아래로 넣기", "바늘을 엄지 바깥쪽 실 아래에서 엄지 고리 안으로 넣습니다."),
            ("검지 작업실 걸기", "바늘 끝으로 검지에 걸린 작업실을 위에서 아래로 잡습니다."),
            ("엄지 고리로 끌어오기", "잡은 작업실을 엄지 고리 사이로 끌어온 뒤 엄지를 고리에서 뺍니다."),
            ("새 코 조이기", "엄지로 꼬리실을 당겨 새 코를 바늘 몸통 굵기에 맞게 조입니다."),
            ("같은 방향의 코 확인", "필요한 수만큼 반복하고 모든 코의 밑단과 간격이 같은 방향인지 확인합니다."),
        ]),
    },
    "겉뜨기(knit stitch)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=tmTFQU-Pl6I", "title": "쎄비 대바늘 기초 · 겉뜨기", "focus": "오른바늘을 앞에서 뒤로 넣고 작업실을 감아 새 고리를 끌어온 뒤 헌 코를 빼는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("knit-stitch", [
            ("작업실을 뒤에 두기", "겉뜨기를 시작하기 전에 작업실이 편물 뒤쪽에 있는지 확인합니다."),
            ("앞에서 뒤로 바늘 넣기", "오른바늘을 왼바늘 첫 코의 앞고리에 앞에서 뒤로 넣어 두 바늘이 X가 되게 합니다."),
            ("작업실 감기", "작업실을 오른바늘 둘레에 반시계 방향으로 감습니다."),
            ("새 고리 끌어오기", "오른바늘 끝으로 감은 실을 헌 코 사이를 통해 앞쪽으로 끌어옵니다."),
            ("헌 코 빼기", "새 고리를 오른바늘에 유지한 채 헌 코를 왼바늘 끝에서 뺍니다."),
            ("V 방향 확인", "새 코가 비틀리지 않았고 오른바늘에 같은 방향으로 놓였는지 확인합니다."),
        ]),
    },
    "안뜨기(purl stitch)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=D-Z_s0AiHrg", "title": "쎄비 대바늘 기초 · 안뜨기", "focus": "작업실을 앞에 두고 오른바늘을 안뜨기 방향으로 넣어 고리를 뒤쪽으로 빼는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("purl-stitch", [
            ("작업실을 앞으로 옮기기", "안뜨기를 시작하기 전에 작업실을 두 바늘 사이로 편물 앞쪽에 둡니다."),
            ("오른쪽에서 왼쪽으로 넣기", "오른바늘을 첫 코의 앞에서 오른쪽에서 왼쪽 방향으로 넣습니다."),
            ("앞쪽에서 실 감기", "편물 앞에 있는 작업실을 오른바늘 끝 둘레에 감습니다."),
            ("새 고리를 뒤로 빼기", "감은 실을 헌 코 사이로 밀어 편물 뒤쪽에 새 고리를 만듭니다."),
            ("헌 코 빼기", "새 고리를 오른바늘에 유지한 채 헌 코를 왼바늘에서 뺍니다."),
            ("가로 마디 확인", "완성 코 앞쪽에 안뜨기 특유의 가로 마디가 고르게 생겼는지 봅니다."),
        ]),
    },
    "1×1 고무뜨기(1x1 ribbing)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=HKQkQhJED9k", "title": "쎄비 대바늘 기초 · 1코 고무뜨기", "focus": "겉뜨기 1코와 안뜨기 1코 사이에서 작업실을 바늘 사이로 앞뒤 이동하는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("ribbing", [
            ("겉뜨기 1코", "작업실을 뒤에 두고 첫 코를 겉뜨기합니다."),
            ("실을 바늘 사이로 앞으로", "여분 코가 생기지 않도록 작업실을 두 바늘 사이로 앞쪽에 옮깁니다."),
            ("안뜨기 1코", "작업실을 앞에 둔 채 다음 코를 안뜨기합니다."),
            ("실을 바늘 사이로 뒤로", "다음 겉뜨기를 위해 작업실을 두 바늘 사이로 뒤쪽에 옮깁니다."),
            ("K1·P1 반복", "겉뜨기 1코와 안뜨기 1코를 단 끝까지 같은 순서로 반복합니다."),
            ("세로 골 확인", "다음 단에서는 보이는 코의 성질대로 떠 겉·안 세로 골이 이어지는지 확인합니다."),
        ]),
    },
    "덮어씌워 코막음(basic bind off)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=Rouh02M-eVg", "title": "쎄비 대바늘 기초 · 덮어씌워 코막음", "focus": "오른바늘의 앞 코를 뒤 코 위로 덮어씌우고 한 코만 남기는 동작을 확인합니다."}],
        "reference_cards": _reference_cards("bind-off", [
            ("첫 두 코 겉뜨기", "오른바늘에 완성 코 두 개가 놓이도록 첫 두 코를 겉뜨기합니다."),
            ("앞 코와 뒤 코 구분", "바늘 끝에 가까운 뒤 코와 그 뒤에 있는 먼저 뜬 앞 코를 구분합니다."),
            ("왼바늘로 앞 코 잡기", "왼바늘 끝을 먼저 뜬 앞 코에 넣어 빠지지 않게 잡습니다."),
            ("뒤 코 위로 덮어씌우기", "잡은 앞 코를 바늘 끝과 뒤 코 위로 넘겨 오른바늘에서 뺍니다."),
            ("오른바늘 한 코 확인", "덮어씌운 뒤 오른바늘에 한 코만 남았는지 확인합니다."),
            ("다음 코 뜨고 반복", "다음 코를 떠 다시 두 코를 만든 뒤 앞 코를 덮어씌우는 동작을 반복합니다."),
            ("느슨한 마감선 확인", "마감선이 편물 폭을 당기지 않고 각 사슬 고리가 고르게 이어지는지 봅니다."),
        ]),
    },
    "메리야스뜨기(stockinette stitch)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=UWabsY0k7BA", "title": "쎄비 대바늘 기초 · 메리야스뜨기", "focus": "평면 편물의 겉면은 겉뜨기, 뒤집은 뒷면은 안뜨기로 한 단씩 반복하는 흐름을 확인합니다."}],
        "reference_cards": _reference_cards("stockinette-stitch", [
            ("겉면에서 겉뜨기", "편물의 겉면 한 단을 모든 코 겉뜨기로 진행합니다."),
            ("겉면 단 끝 확인", "한 단을 마친 뒤 코 수를 확인하고 편물을 뒤집습니다."),
            ("뒷면에서 실 앞으로", "뒷면 단을 시작하며 작업실을 편물 앞쪽에 둡니다."),
            ("뒷면에서 안뜨기", "뒷면 한 단을 모든 코 안뜨기로 진행합니다."),
            ("앞뒤 한 단씩 반복", "겉면 겉뜨기와 뒷면 안뜨기를 한 쌍으로 반복합니다."),
            ("겉면 V 조직 확인", "겉면에 V가 세로로 이어지고 뒷면에는 가로 마디가 보이는지 확인합니다."),
        ]),
    },
    "가터뜨기(garter stitch)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=7doUAokE6I0", "title": "쎄비 대바늘 기초 · 가터뜨기", "focus": "평면 편물의 앞면과 뒤집은 뒷면을 모두 겉뜨기해 가로 능선을 만드는 흐름을 확인합니다."}],
        "reference_cards": _reference_cards("garter-stitch", [
            ("첫 단 모두 겉뜨기", "첫 단의 모든 코를 겉뜨기로 진행합니다."),
            ("단 끝에서 편물 돌리기", "코 수를 확인한 뒤 편물을 뒤집어 작업 바늘을 다시 오른손에 듭니다."),
            ("뒷면도 모두 겉뜨기", "뒤집은 면에서도 모든 코를 겉뜨기로 진행합니다."),
            ("두 단을 한 쌍으로 반복", "앞뒤 구분 없이 모든 단 겉뜨기를 원하는 길이까지 반복합니다."),
            ("가로 능선 세기", "겉뜨기 두 단마다 가터 능선 한 줄이 생기는지 확인합니다."),
            ("양면 조직 확인", "편물 양면의 질감이 같고 가장자리가 심하게 말리지 않는지 봅니다."),
        ]),
    },
    "멍석뜨기(seed stitch)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=D73v0mtcNB8", "title": "쎄비 대바늘 기초과정 · 1코 1단 멍석뜨기", "focus": "겉뜨기와 안뜨기를 한 코씩 번갈아 뜨고 다음 단에서 아래 코와 반대로 뜨는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("seed-stitch", [
            ("1코 1단 배열 확인", "차트에서 겉뜨기와 안뜨기가 가로·세로로 번갈아 배치되는지 확인합니다."),
            ("첫 단 겉뜨기 1코", "첫 코를 겉뜨기하고 다음 안뜨기를 위해 실을 앞으로 옮깁니다."),
            ("안뜨기 1코와 반복", "다음 코를 안뜨기한 뒤 실을 뒤로 옮겨 K1·P1을 단 끝까지 반복합니다."),
            ("편물을 돌려 아래 코 읽기", "다음 단에서 V 모양 겉코와 가로 마디 안코를 하나씩 확인합니다."),
            ("겉코 위에는 안뜨기", "아래에 겉코가 보이면 이번 단에서는 안뜨기합니다."),
            ("안코 위에는 겉뜨기", "아래에 안코가 보이면 이번 단에서는 겉뜨기합니다."),
            ("바둑판 질감 확인", "세로 골이 생기지 않고 오톨도톨한 점이 번갈아 나타나는지 확인합니다."),
        ]),
    },
    "바늘비우기(yarn over)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=2EdTH7KEba0", "title": "바늘이야기 대바늘 마스터 · 바늘비우기(YO)", "focus": "작업실을 오른바늘 위로 넘겨 새 코를 유지하고 다음 단에서 구멍을 확인합니다."}],
        "reference_cards": _reference_cards("yarn-over", [
            ("YO 위치 확인", "도안에서 바늘비우기를 넣을 두 코 사이 위치를 확인합니다."),
            ("작업실을 앞으로", "겉뜨기 사이 YO라면 작업실을 두 바늘 사이로 앞쪽에 둡니다."),
            ("오른바늘 위로 넘기기", "작업실을 오른바늘 위를 지나 뒤쪽으로 한 번 넘깁니다."),
            ("다음 코 뜨기", "감긴 실을 오른바늘에 유지한 채 다음 코를 겉뜨기합니다."),
            ("새 고리 한 코 확인", "오른바늘 위 감긴 실이 독립된 새 코 하나로 남았는지 확인합니다."),
            ("다음 단 구멍 확인", "다음 단에서 감긴 고리를 떠 의도한 구멍과 한 코 늘림이 생겼는지 봅니다."),
        ]),
    },
    "KFB 늘림(knit front and back)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=LjMzNcVKHpA", "title": "쎄비 대바늘 기초 · KFB 늘리기", "focus": "한 코의 앞고리를 뜬 뒤 헌 코를 빼지 않고 뒤고리까지 떠 두 코로 만드는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("knit-front-back", [
            ("한 코 앞고리에 넣기", "오른바늘을 늘릴 코의 앞고리에 겉뜨기 방향으로 넣습니다."),
            ("앞고리 겉뜨기", "새 고리를 끌어오되 헌 코는 왼바늘에서 빼지 않습니다."),
            ("헌 코를 돌려 뒤고리 찾기", "오른바늘을 같은 헌 코의 뒤쪽 다리로 이동합니다."),
            ("뒤고리에 다시 넣기", "같은 코의 뒤고리에 오른바늘을 넣어 두 번째 겉뜨기를 시작합니다."),
            ("둘째 고리 끌어오기", "뒤고리에서 새 고리를 하나 더 만들어 오른바늘에 둡니다."),
            ("헌 코 빼고 두 코 확인", "헌 코를 왼바늘에서 빼 한 밑코에서 새 코 두 개가 나왔는지 확인합니다."),
        ]),
    },
    "오른코 늘림(make one right)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=5vc4rrM6Jao", "title": "쎄비 대바늘 기초 · 오른코 늘리기(M1R)", "focus": "두 코 사이 가로실을 뒤에서 앞으로 들어 올리고 앞고리로 떠 오른쪽 기울기를 만드는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("make-one-right", [
            ("두 코 사이 가로실 찾기", "왼바늘과 오른바늘 사이의 가로실 한 가닥을 찾습니다."),
            ("뒤에서 앞으로 들어 올리기", "왼바늘 끝을 가로실 뒤에서 앞으로 넣어 바늘 위에 올립니다."),
            ("앞고리 삽입 위치 확인", "들어 올린 가로실의 앞쪽 다리에 오른바늘을 넣을 위치를 확인합니다."),
            ("앞고리로 겉뜨기", "가로실이 비틀려 구멍이 닫히도록 앞고리를 겉뜨기합니다."),
            ("새 코 조이기", "새 코를 바늘 몸통에 맞추되 주변 코보다 과하게 조이지 않습니다."),
            ("오른쪽 기울기 확인", "새 코의 다리가 오른쪽으로 기울고 큰 구멍이 없는지 확인합니다."),
        ]),
    },
    "왼코 늘림(make one left)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=5viq_QqxKUA", "title": "쎄비 대바늘 기초 · 왼코 늘리기(M1L)", "focus": "두 코 사이 가로실을 앞에서 뒤로 들어 올리고 뒤고리로 떠 왼쪽 기울기를 만드는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("make-one-left", [
            ("두 코 사이 가로실 찾기", "왼바늘과 오른바늘 사이의 가로실 한 가닥을 찾습니다."),
            ("앞에서 뒤로 들어 올리기", "왼바늘 끝을 가로실 앞에서 뒤로 넣어 바늘 위에 올립니다."),
            ("뒤고리 삽입 위치 확인", "들어 올린 가로실의 뒤쪽 다리에 오른바늘을 넣을 위치를 확인합니다."),
            ("뒤고리로 겉뜨기", "가로실이 비틀려 구멍이 닫히도록 뒤고리를 겉뜨기합니다."),
            ("새 코 조이기", "새 코를 바늘 몸통에 맞추되 주변 코보다 과하게 조이지 않습니다."),
            ("왼쪽 기울기 확인", "새 코의 다리가 왼쪽으로 기울고 큰 구멍이 없는지 확인합니다."),
        ]),
    },
    "겉뜨기 2코 모아뜨기(knit 2 together)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=4hADmZkp8Ig", "title": "바늘이야기 대바늘 기초 · K2tog와 SSK", "focus": "이웃한 두 코를 동시에 겉뜨기해 한 코로 줄이고 오른쪽 기울기를 확인합니다."}],
        "reference_cards": _reference_cards("k2tog", [
            ("줄일 두 코 확인", "함께 모을 이웃한 두 코를 왼바늘 끝에서 확인합니다."),
            ("두 코 앞고리에 함께 넣기", "오른바늘을 두 코의 앞고리에 동시에 겉뜨기 방향으로 넣습니다."),
            ("작업실 감기", "두 코를 한 코처럼 잡은 상태에서 작업실을 감습니다."),
            ("새 고리 하나 끌어오기", "감은 실을 두 헌 코 사이로 한 번에 끌어옵니다."),
            ("헌 코 두 개 함께 빼기", "두 헌 코를 왼바늘에서 동시에 빼 오른바늘에 한 코만 남깁니다."),
            ("오른쪽 기울기 확인", "코 수가 하나 줄고 줄임선이 오른쪽으로 기울었는지 봅니다."),
        ]),
    },
    "걸러 겉뜨기 2코 모아뜨기(slip slip knit)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=4hADmZkp8Ig", "title": "바늘이야기 대바늘 기초 · K2tog와 SSK", "focus": "두 코를 하나씩 겉뜨기 방향으로 옮겨 방향을 바꾼 뒤 함께 떠 왼쪽 기울기를 만듭니다."}],
        "reference_cards": _reference_cards("ssk", [
            ("첫 코 겉뜨기 방향으로 걸러뜨기", "첫 코를 겉뜨기 방향으로 오른바늘에 옮깁니다."),
            ("둘째 코도 따로 걸러뜨기", "둘째 코도 하나씩 겉뜨기 방향으로 오른바늘에 옮깁니다."),
            ("왼바늘을 두 코 앞에 넣기", "왼바늘을 옮긴 두 코의 앞쪽 다리에 함께 넣습니다."),
            ("두 코 뒤고리로 겉뜨기", "오른바늘로 두 코를 뒤고리 방향에서 함께 겉뜨기합니다."),
            ("헌 코 두 개 빼기", "두 헌 코를 바늘에서 함께 빼 새 코 하나만 남깁니다."),
            ("왼쪽 기울기 확인", "코 수가 하나 줄고 K2tog와 반대인 왼쪽 기울기가 생겼는지 봅니다."),
        ]),
    },
    "안뜨기 2코 모아뜨기(purl 2 together)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=FDVoSMGOQI4", "title": "붉은모래의 니팅랜드 · 안뜨기 2코 모아뜨기", "focus": "실을 앞에 두고 두 코를 동시에 안뜨기해 한 코로 줄이는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("p2tog", [
            ("작업실을 앞에 두기", "안뜨기 줄임을 위해 작업실을 편물 앞쪽에 둡니다."),
            ("줄일 두 코 확인", "왼바늘 끝의 이웃한 두 코를 함께 잡을 준비를 합니다."),
            ("두 코에 안뜨기 방향으로 넣기", "오른바늘을 두 코에 동시에 오른쪽에서 왼쪽으로 넣습니다."),
            ("작업실 감기", "두 코를 함께 잡은 상태에서 앞쪽 작업실을 오른바늘에 감습니다."),
            ("새 고리 하나 빼기", "감은 실을 두 헌 코 사이로 한 번에 빼 새 고리 하나를 만듭니다."),
            ("두 코 함께 빼기", "두 헌 코를 왼바늘에서 함께 빼 코 수가 하나 줄었는지 확인합니다."),
        ]),
    },
    "안뜨기 방향 걸러뜨기(slip 1 purlwise wyib)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=7AUow_HZh_o", "title": "쎄비 대바늘 기초과정 · 걸러뜨기", "focus": "작업실을 뒤에 둔 채 코를 안뜨기 방향으로 옮겨 코 방향을 유지하는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("slip-stitch-knitting", [
            ("작업실을 뒤에 두기", "wyib 지시에 맞춰 작업실이 편물 뒤쪽에 있는지 확인합니다."),
            ("안뜨기 방향으로 넣기", "오른바늘을 다음 코에 안뜨기할 때와 같은 방향으로 넣습니다."),
            ("실을 감지 않기", "새 고리를 만들지 않도록 작업실을 바늘에 감지 않습니다."),
            ("코만 오른바늘로 옮기기", "헌 코를 그대로 왼바늘에서 오른바늘로 이동합니다."),
            ("코 방향 유지 확인", "옮긴 코의 앞뒤 다리가 바뀌거나 꼬이지 않았는지 확인합니다."),
            ("뒤쪽 가로실 확인", "작업실이 편물 뒤에 지나가고 앞면에 불필요한 가로실이 없는지 봅니다."),
        ]),
    },
    "코 줍기(pick up stitches)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=tz1RwL60XvY", "title": "쎄비 대바늘 기초 · 코 줍기", "focus": "완성 편물 가장자리의 일정한 간격에서 바늘을 넣고 새 고리를 끌어올리는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("pick-up-stitches", [
            ("주울 가장자리와 간격 확인", "코를 주울 가장자리의 기둥과 전체 배치 간격을 먼저 확인합니다."),
            ("가장자리 가닥 아래로 넣기", "오른바늘을 선택한 가장자리 가닥 아래에 앞에서 뒤로 넣습니다."),
            ("작업실 걸기", "편물 뒤쪽의 새 작업실을 오른바늘 끝으로 잡습니다."),
            ("새 고리 앞으로 끌어오기", "잡은 실을 가장자리 가닥 아래로 통과시켜 앞쪽에 새 고리를 만듭니다."),
            ("오른바늘에 새 코 놓기", "끌어온 고리를 오른바늘 몸통에 올려 한 코로 유지합니다."),
            ("같은 간격으로 반복", "표시한 간격을 따라 같은 깊이에서 코를 차례로 줍습니다."),
            ("연결부 평평함 확인", "주운 코가 고르게 분포하고 가장자리가 울거나 당기지 않는지 확인합니다."),
        ]),
    },
    "원형 연결(join in the round)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=KM754o8ERAE", "title": "공방장 · 라운드뜨기 시작 코 연결 팁", "focus": "잡은 코의 밑단이 꼬이지 않았는지 확인하고 첫 코와 마지막 코를 연결하는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("join-in-round", [
            ("코잡기 밑단 방향 정렬", "케이블을 따라 모든 코의 밑단이 원 안쪽을 향하도록 정렬합니다."),
            ("한 바퀴 비틀림 확인", "첫 코부터 마지막 코까지 코잡기 가장자리가 한 번도 뒤집히지 않았는지 봅니다."),
            ("첫 코와 마지막 코 가까이 두기", "양쪽 바늘 끝을 맞대고 코 사이 간격이 벌어지지 않게 잡습니다."),
            ("단 시작 마커 놓기", "첫 코 앞에 마커를 놓아 원형 단의 시작점을 표시합니다."),
            ("첫 코 떠서 연결", "작업실을 당겨 장력을 유지하며 첫 코를 겉뜨기합니다."),
            ("연결부 조이기", "첫 몇 코를 뜬 뒤 시작과 끝 사이의 늘어진 실을 부드럽게 조입니다."),
            ("꼬이지 않은 원 확인", "한 단 후 코잡기 밑단이 한 방향으로 이어지고 마커가 시작점에 있는지 확인합니다."),
        ]),
    },
    "2×2 오른쪽 케이블(2/2 right cross)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=xGJ0EKHUMPY", "title": "앵콜스 대바늘 왕초보 · 2/2 RC 왼코 위 2코 교차뜨기", "focus": "앞 두 코를 보조바늘에 옮겨 뒤에 두고 다음 두 코를 먼저 떠 오른쪽 교차를 만드는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("two-by-two-right-cable", [
            ("교차할 네 코 확인", "케이블 무늬에 사용할 앞의 네 코를 왼바늘 끝에서 확인합니다."),
            ("앞 두 코 보조바늘로", "앞 두 코를 뜨지 않고 보조바늘에 옮깁니다."),
            ("보조바늘을 편물 뒤에", "2/2 RC 방향에 맞춰 보조바늘과 두 코를 편물 뒤에 둡니다."),
            ("왼바늘 다음 두 코 겉뜨기", "왼바늘에 남은 다음 두 코를 먼저 겉뜨기합니다."),
            ("보조바늘 두 코 겉뜨기", "뒤에 둔 보조바늘의 두 코를 차례로 겉뜨기합니다."),
            ("오른쪽 교차 확인", "네 코가 빠짐없이 유지되고 케이블이 오른쪽으로 교차했는지 봅니다."),
        ]),
    },
    "2×2 왼쪽 케이블(2/2 left cross)": {
        "reference_videos": [{"url": "https://www.youtube.com/watch?v=wVGY3wKh2eo", "title": "앵콜스 대바늘 왕초보 · 2/2 LC 오른코 위 2코 교차뜨기", "focus": "앞 두 코를 보조바늘에 옮겨 앞에 두고 다음 두 코를 먼저 떠 왼쪽 교차를 만드는 구간을 확인합니다."}],
        "reference_cards": _reference_cards("two-by-two-left-cable", [
            ("교차할 네 코 확인", "케이블 무늬에 사용할 앞의 네 코를 왼바늘 끝에서 확인합니다."),
            ("앞 두 코 보조바늘로", "앞 두 코를 뜨지 않고 보조바늘에 옮깁니다."),
            ("보조바늘을 편물 앞에", "2/2 LC 방향에 맞춰 보조바늘과 두 코를 편물 앞에 둡니다."),
            ("왼바늘 다음 두 코 겉뜨기", "왼바늘에 남은 다음 두 코를 먼저 겉뜨기합니다."),
            ("보조바늘 두 코 겉뜨기", "앞에 둔 보조바늘의 두 코를 차례로 겉뜨기합니다."),
            ("왼쪽 교차 확인", "네 코가 빠짐없이 유지되고 케이블이 왼쪽으로 교차했는지 봅니다."),
        ]),
    },
}

for _name, _references in _EXPANDED_TECHNIQUE_REFERENCES.items():
    _target_pack = _EXPANDED_TECHNIQUES.get(_name) or _LESSON_PACKS.get(_name)
    if _target_pack is None:
        raise KeyError(f"Reference pack has no matching technique: {_name}")
    _target_pack.update(_references)


_EXISTING_METADATA: dict[str, dict] = {
    "사슬뜨기(chain stitch)": {"category": "basics", "aliases": ["사슬뜨기", "사슬", "chain stitch", "ch"], "prerequisites": ["slip-knot"], "related_slugs": ["single-crochet"]},
    "짧은뜨기(single crochet)": {"category": "basics", "aliases": ["짧은뜨기", "single crochet", "sc"], "prerequisites": ["crochet-chain-stitch"], "related_slugs": ["half-double-crochet", "single-crochet-increase"]},
    "긴뜨기(half double crochet)": {"category": "basics", "aliases": ["긴뜨기", "half double crochet", "hdc"], "prerequisites": ["single-crochet"], "related_slugs": ["double-crochet"]},
    "빼뜨기(slip stitch)": {"category": "basics", "aliases": ["빼뜨기", "slip stitch crochet", "sl st"], "prerequisites": ["crochet-chain-stitch"], "related_slugs": ["round-crochet"]},
    "매직링(magic ring)": {"category": "construction", "aliases": ["매직링", "magic ring", "magic circle", "MR"], "prerequisites": ["crochet-chain-stitch"], "related_slugs": ["round-crochet"]},
    "매직링으로 원형 시작하기(crocheting in the round)": {"category": "construction", "aliases": ["매직링으로 원형 시작하기", "코바늘 원형뜨기", "원형뜨기", "round crochet", "crochet in the round", "working in rounds"], "prerequisites": ["magic-ring", "single-crochet"], "related_slugs": ["single-crochet-increase"]},
    "한길긴뜨기(double crochet)": {"category": "basics", "aliases": ["한길긴뜨기", "double crochet", "dc"], "prerequisites": ["half-double-crochet"], "related_slugs": ["treble-crochet", "double-crochet-decrease"]},
    "롱테일 코잡기(long-tail cast on)": {"category": "basics", "aliases": ["롱테일 코잡기", "코 잡기", "코잡기", "long-tail cast on", "casting on", "cast on", "CO"], "prerequisites": [], "related_slugs": ["knit-stitch", "bind-off"]},
    "겉뜨기(knit stitch)": {"category": "basics", "aliases": ["겉뜨기", "knit stitch", "knit", "K"], "prerequisites": ["casting-on"], "related_slugs": ["purl-stitch", "garter-stitch"]},
    "안뜨기(purl stitch)": {"category": "basics", "aliases": ["안뜨기", "purl stitch", "purl", "P"], "prerequisites": ["casting-on"], "related_slugs": ["knit-stitch", "stockinette-stitch"]},
    "1×1 고무뜨기(1x1 ribbing)": {"category": "texture", "aliases": ["1×1 고무뜨기", "1x1 고무뜨기", "고무뜨기", "ribbing", "rib stitch", "K1 P1"], "prerequisites": ["knit-stitch", "purl-stitch"], "related_slugs": ["seed-stitch"]},
}

for _name, _lesson in _LESSON_PACKS.items():
    TECHNIQUE_CATALOG[_name].update(_lesson)
for _name, _metadata in _EXISTING_METADATA.items():
    TECHNIQUE_CATALOG[_name].update(_metadata, search_terms=_metadata["aliases"])
TECHNIQUE_CATALOG.update(_EXPANDED_TECHNIQUES)

# The current needle-knitting SVGs are explanatory mini diagrams, not exact
# reproductions of one publisher's chart key. Keep the standard abbreviations,
# but label the visuals honestly as learning icons until exact licensed/source
# symbols replace them.
for _lesson in TECHNIQUE_CATALOG.values():
    if _lesson["tool_type"] == "needle_knitting":
        _lesson["symbol_standard"] = False
        _lesson["symbol_kind"] = "learning"

for _slug in {"single-crochet-increase", "join-in-round"}:
    next(_lesson for _lesson in TECHNIQUE_CATALOG.values() if _lesson["slug"] == _slug)["abbreviation_standard"] = False


# Validated, typed view for the UI. Order follows TECHNIQUE_CATALOG.
TECHNIQUES: list[Technique] = [
    Technique(name=name, **data) for name, data in TECHNIQUE_CATALOG.items()
]
_BY_NAME: dict[str, Technique] = {t.name: t for t in TECHNIQUES}
_BY_SLUG: dict[str, Technique] = {t.slug: t for t in TECHNIQUES}


def list_techniques(
    tool: ToolType | None = None,
    level: Difficulty | None = None,
    category: Category | None = None,
    query: str | None = None,
) -> list[Technique]:
    """Return techniques filtered by tool, difficulty, category, and search text."""
    result = TECHNIQUES
    if tool is not None:
        result = [t for t in result if t.tool_type == tool]
    if level is not None:
        result = [t for t in result if t.difficulty == level]
    if category is not None:
        result = [t for t in result if t.category == category]
    if query and query.strip():
        needle = query.strip().casefold()
        result = [
            t for t in result
            if any(
                needle in value.casefold()
                for value in [t.name, t.description, t.abbreviation, *t.aliases, *t.search_terms]
            )
        ]
    return result


def get_technique(name_or_slug: str) -> Technique | None:
    """Look up a single technique by its display name or stable slug."""
    return _BY_NAME.get(name_or_slug) or _BY_SLUG.get(name_or_slug)


def _alias_pattern(alias: str) -> re.Pattern[str]:
    escaped = re.escape(alias.casefold())
    if re.fullmatch(r"[a-z0-9 /×-]+", alias.casefold()):
        return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


def resolve_techniques(text: str, tool: ToolType | None = None) -> list[Technique]:
    """Resolve authored names/aliases, preferring longer non-overlapping matches."""
    lowered = text.casefold()
    candidates: list[tuple[int, int, Technique]] = []
    for technique in TECHNIQUES:
        if tool is not None and technique.tool_type != tool:
            continue
        aliases = [technique.name.split("(")[0], technique.abbreviation, *technique.aliases]
        for alias in sorted(set(aliases), key=len, reverse=True):
            match = _alias_pattern(alias).search(lowered)
            if match:
                candidates.append((match.start(), match.end(), technique))
                break

    selected: list[tuple[int, int, Technique]] = []
    for start, end, technique in sorted(candidates, key=lambda item: (-(item[1] - item[0]), item[0])):
        if any(start >= kept_start and end <= kept_end for kept_start, kept_end, _ in selected):
            continue
        selected.append((start, end, technique))
    return [item[2] for item in sorted(selected, key=lambda item: item[0])]
