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
    learning_goal: str
    practice: str
    success_check: str
    video_generation_prompt: str
    video_asset_path: str
    video_status: Literal["pilot", "prompt_ready", "ready"] = "prompt_ready"
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
    "원형뜨기(round crochet)": {
        "tool_type": "crochet", "difficulty": "intermediate",
        "description": "중심에서 바깥쪽으로 늘림 위치를 관리하며 둥글게 뜨는 방식입니다.",
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
        "custom_video_generation_prompt": "단수링을 사용해 원형뜨기 시작점과 늘림 위치를 관리하는 영상",
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
    "코 잡기(casting on)": {
        "tool_type": "needle_knitting", "difficulty": "beginner",
        "description": "대바늘 첫 단의 코를 만드는 시작 기법입니다.",
        "steps": [
            "첫 코가 될 고리를 오른바늘에 겁니다.",
            "손가락에 실을 걸어 새 코를 만들어 바늘에 올립니다.",
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
    "고무뜨기(ribbing)": {
        "tool_type": "needle_knitting", "difficulty": "confident_beginner",
        "description": "겉뜨기와 안뜨기를 반복해 탄력 있는 조직을 만드는 방식입니다.",
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
_LESSON_PACKS: dict[str, dict] = {
    "사슬뜨기(chain stitch)": {
        "slug": "crochet-chain-stitch", "abbreviation": "ch", "symbol_key": "chain", "symbol_standard": True,
        "learning_goal": "실을 감아 고리 사이로 빼는 동작을 반복하며 크기가 일정한 기초 사슬을 만듭니다.",
        "practice": "밝은 중간 굵기 실로 사슬 15코를 두 번 만들고 두 줄의 길이와 코 크기를 비교하세요.",
        "success_check": "15개의 V 모양이 빠짐없이 보이고, 바늘이 각 사슬에 무리 없이 들어가나요?",
        "video_generation_prompt": _video_prompt("form a slip knot, yarn over, pull through one loop, and repeat three even chain stitches"),
        "video_asset_path": "assets/techniques/crochet-chain-stitch/video.mp4", "video_status": "pilot",
    },
    "짧은뜨기(single crochet)": {
        "slug": "single-crochet", "abbreviation": "sc", "symbol_key": "single_crochet", "symbol_standard": True,
        "learning_goal": "다음 코에 바늘을 넣고 두 번의 실 감기로 낮고 단단한 한 코를 완성합니다.",
        "practice": "사슬 12코 위에 짧은뜨기 3단을 뜨고 각 단의 첫 코와 마지막 코에 마커를 거세요.",
        "success_check": "매 단 코 수가 같고 양쪽 가장자리가 안쪽으로 줄어들지 않았나요?",
        "video_generation_prompt": _video_prompt("insert the hook under both top loops, pull up one loop, yarn over, and pull through both loops to finish one single crochet"),
        "video_asset_path": "assets/techniques/single-crochet/video.mp4", "video_status": "pilot",
    },
    "긴뜨기(half double crochet)": {
        "slug": "half-double-crochet", "abbreviation": "hdc", "symbol_key": "half_double_crochet", "symbol_standard": True,
        "learning_goal": "실을 한 번 감고 만들어진 세 고리를 한 번에 빼 중간 높이의 코를 만듭니다.",
        "practice": "사슬 12코 위에 긴뜨기 2단을 뜨며 매 코마다 바늘 위 고리 3개를 확인하세요.",
        "success_check": "세 고리를 한 번에 통과했고 한길긴뜨기보다 낮은 높이가 일정한가요?",
        "video_generation_prompt": _video_prompt("yarn over once, insert into the next stitch, pull up a loop to show three loops, then yarn over and pull through all three loops at once"),
        "video_asset_path": "assets/techniques/half-double-crochet/video.mp4", "video_status": "prompt_ready",
    },
    "빼뜨기(slip stitch)": {
        "slug": "slip-stitch", "abbreviation": "sl st", "symbol_key": "slip_stitch", "symbol_standard": True,
        "learning_goal": "새 높이를 만들지 않고 코와 바늘 위 고리를 한 번에 통과해 위치를 연결합니다.",
        "practice": "사슬 10코를 만든 뒤 각 사슬에 빼뜨기를 하고, 마지막 코에도 바늘이 들어가는지 확인하세요.",
        "success_check": "편물이 말리지 않을 만큼 느슨하고 모든 연결 코가 낮게 이어졌나요?",
        "video_generation_prompt": _video_prompt("insert into the next stitch and pull the working yarn through the stitch and the loop already on the hook in one continuous motion"),
        "video_asset_path": "assets/techniques/slip-stitch/video.mp4", "video_status": "prompt_ready",
    },
    "매직링(magic ring)": {
        "slug": "magic-ring", "abbreviation": "MR", "symbol_key": "magic_ring", "symbol_standard": False,
        "learning_goal": "조절 가능한 실 고리를 만들고 첫 단의 코를 넣은 뒤 중심을 단단히 닫습니다.",
        "practice": "매직링 안에 짧은뜨기 6코를 넣고 코 수를 확인한 다음 꼬리실을 당겨 닫으세요.",
        "success_check": "6코가 모두 남아 있고 중심 구멍이 벌어지지 않게 닫혔나요?",
        "video_generation_prompt": _video_prompt("wrap yarn into an adjustable ring, secure it with one chain, work two sample stitches into the ring, then pull the tail to close the center"),
        "video_asset_path": "assets/techniques/magic-ring/video.mp4", "video_status": "prompt_ready",
    },
    "원형뜨기(round crochet)": {
        "slug": "round-crochet", "abbreviation": "rnd", "symbol_key": "round_crochet", "symbol_standard": False,
        "learning_goal": "단 시작점을 표시하고 일정한 간격으로 늘림을 배치해 평평한 원을 만듭니다.",
        "practice": "매직링 6코에서 시작해 두 번째 단은 모든 코에 늘림을 넣고 마커를 옮기세요.",
        "success_check": "두 번째 단이 12코이고 마커가 단 시작점에 있으며 원이 편평한가요?",
        "video_generation_prompt": _video_prompt("move a contrasting stitch marker to the first stitch, work one normal stitch and one increase, then show the evenly expanding round lying flat"),
        "video_asset_path": "assets/techniques/round-crochet/video.mp4", "video_status": "prompt_ready",
    },
    "한길긴뜨기(double crochet)": {
        "slug": "double-crochet", "abbreviation": "dc", "symbol_key": "double_crochet", "symbol_standard": True,
        "learning_goal": "실을 한 번 감고 고리를 두 개씩 두 번 빼 높이 있는 코를 만듭니다.",
        "practice": "사슬 12코 위에 한길긴뜨기 2단을 뜨며 ‘두 고리, 두 고리’를 소리 내어 확인하세요.",
        "success_check": "각 코에서 두 고리씩 정확히 두 번 뺐고 높이가 일정한가요?",
        "video_generation_prompt": _video_prompt("yarn over once, insert into the next stitch, pull up a loop, then yarn over and pull through two loops twice to complete one double crochet"),
        "video_asset_path": "assets/techniques/double-crochet/video.mp4", "video_status": "prompt_ready",
    },
    "코 잡기(casting on)": {
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
    "고무뜨기(ribbing)": {
        "slug": "ribbing", "abbreviation": "K1, P1", "symbol_key": "ribbing", "symbol_standard": False,
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
    "앞고리뜨기(front loop only)": _expanded_entry(
        tool_type="crochet", difficulty="confident_beginner", category="texture",
        description="코 머리의 앞쪽 고리 하나에만 바늘을 넣어 선이 생기는 조직을 만듭니다.",
        steps=["다음 코의 V 머리를 확인합니다.", "몸 쪽 앞고리 하나에만 바늘을 넣습니다.", "도안이 지정한 기본 코를 완성합니다."],
        mistake="두 고리를 모두 잡아 질감선이 사라짐", fix="바늘 아래에 앞고리 한 가닥만 걸렸는지 옆에서 확인합니다.",
        slug="front-loop-only", abbreviation="FLO", symbol_key="front_loop",
        learning_goal="앞고리와 뒤고리를 구분해 지정된 한 가닥에만 정확히 뜹니다.",
        practice="짧은뜨기 10코를 FLO로 2단 떠 일반 짧은뜨기와 비교하세요.", success_check="사용하지 않은 뒤고리가 가로선처럼 남아 있나요?",
        motion="identify the front loop of one stitch, insert under that single strand only, and complete one single crochet",
        aliases=["앞고리뜨기", "앞고리만", "front loop only", "FLO"], prerequisites=["single-crochet"], related_slugs=["back-loop-only"],
    ),
    "뒤고리뜨기(back loop only)": _expanded_entry(
        tool_type="crochet", difficulty="confident_beginner", category="texture",
        description="코 머리의 뒤쪽 고리 하나에만 떠 능선과 신축성을 만드는 기법입니다.",
        steps=["다음 코의 V 머리를 확인합니다.", "몸에서 먼 뒤고리 하나에만 바늘을 넣습니다.", "도안이 지정한 기본 코를 완성합니다."],
        mistake="앞고리를 잡거나 두 고리를 모두 잡음", fix="작업 전 남겨질 앞고리가 바늘 앞쪽에 보이는지 확인합니다.",
        slug="back-loop-only", abbreviation="BLO", symbol_key="back_loop",
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
    "한길긴뜨기 3코 클러스터(3-dc cluster)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="세 개의 한길긴뜨기를 미완성으로 모아 하나의 꼭짓점으로 닫는 장식 기법입니다.",
        steps=["지정 위치에 미완성 한길긴뜨기를 세 번 만듭니다.", "바늘 위에 남은 네 고리를 확인합니다.", "실을 감아 모든 고리를 한 번에 뺍니다."],
        mistake="중간 코를 완성해 클러스터가 갈라짐", fix="세 기둥을 모두 미완성 상태로 바늘에 보관한 뒤 한 번에 닫습니다.",
        slug="three-dc-cluster", abbreviation="3-dc CL", symbol_key="dc3_cluster",
        learning_goal="세 기둥을 한 꼭짓점으로 모아 균일한 클러스터를 만듭니다.",
        practice="사슬 공간 세 곳에 3-dc 클러스터를 하나씩 만드세요.", success_check="각 클러스터에 기둥 3개와 꼭짓점 1개가 보이나요?",
        motion="make three unfinished double crochets into one space, show four loops, then close all loops together",
        aliases=["한길긴뜨기 3코 클러스터", "클러스터뜨기", "3-dc cluster", "cluster"], prerequisites=["double-crochet"], related_slugs=["puff-stitch", "popcorn-stitch"],
    ),
    "퍼프뜨기(puff stitch)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="같은 위치에서 긴 고리를 여러 번 끌어올려 폭신한 한 덩어리로 닫는 기법입니다.",
        steps=["실을 감고 같은 위치에서 긴 고리를 끌어올리는 동작을 반복합니다.", "모든 고리 높이를 같게 맞춥니다.", "실을 감아 고리를 함께 빼고 사슬로 고정합니다."],
        mistake="끌어올린 고리 높이가 달라 퍼프가 기울어짐", fix="각 고리를 기존 코 높이까지 충분히 끌어올린 뒤 다음 반복을 시작합니다.",
        slug="puff-stitch", abbreviation="puff", symbol_key="puff_stitch",
        learning_goal="긴 고리의 높이와 수를 일정하게 유지해 폭신한 질감을 만듭니다.",
        practice="같은 사슬 공간에 5회 감아 올리는 퍼프를 3개 만드세요.", success_check="세 퍼프의 크기와 높이가 비슷한가요?",
        motion="yarn over and pull up five equally tall loops from one space, then close them together and secure with one chain",
        aliases=["퍼프뜨기", "퍼프", "puff stitch", "puff"], prerequisites=["half-double-crochet"], related_slugs=["three-dc-cluster", "popcorn-stitch"],
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
    "쉘뜨기(shell stitch)": _expanded_entry(
        tool_type="crochet", difficulty="intermediate", category="texture",
        description="같은 위치에 여러 개의 긴 코를 부채처럼 펼쳐 조개 모양을 만드는 기법입니다.",
        steps=["도안이 지정한 사슬 공간이나 코를 찾습니다.", "같은 위치에 한길긴뜨기 5코를 차례로 완성합니다.", "다음 쉘까지 지정된 코를 건너 간격을 맞춥니다."],
        mistake="서로 다른 코에 나누어 떠 부채 모양이 사라짐", fix="다섯 기둥의 밑부분이 한 점에서 시작하는지 확인합니다.",
        slug="shell-stitch", abbreviation="5-dc shell", symbol_key="shell_stitch",
        learning_goal="한 지점에서 고르게 펼쳐지는 부채형 무늬를 만듭니다.",
        practice="사슬 바탕에 5-dc 쉘을 3개 같은 간격으로 배치하세요.", success_check="각 쉘의 다섯 기둥이 한 밑점에서 대칭으로 펼쳐지나요?",
        motion="work five complete double crochets into one chain space and spread them into an even fan",
        aliases=["쉘뜨기", "조개무늬", "shell stitch", "5-dc shell"], prerequisites=["double-crochet"], related_slugs=["popcorn-stitch"],
    ),
    "코 막음(bind off)": _expanded_entry(
        tool_type="needle_knitting", difficulty="beginner", category="finishing",
        description="마지막 단의 코를 차례로 넘겨 풀리지 않는 가장자리를 만드는 마무리 기법입니다.",
        steps=["첫 두 코를 도안대로 뜹니다.", "오른바늘의 첫 코를 두 번째 코 위로 넘깁니다.", "한 코를 더 뜨고 넘기는 동작을 끝까지 반복합니다."],
        mistake="너무 조여 가장자리가 오므라듦", fix="코를 바늘 몸통에서 크게 만들고 필요하면 한 호수 큰 바늘을 사용합니다.",
        slug="bind-off", abbreviation="BO", symbol_key="bind_off", symbol_standard=False,
        learning_goal="편물 폭을 유지하면서 탄력이 고른 마감 가장자리를 만듭니다.",
        practice="15코 샘플을 느슨하게 코 막음하고 편물 폭과 비교하세요.", success_check="마감선이 당기지 않고 편물 폭만큼 자연스럽게 늘어나나요?",
        motion="knit two stitches, lift the first stitch over the second and off the needle, then knit one more stitch and repeat",
        aliases=["코 막음", "코막음", "bind off", "cast off", "BO"], prerequisites=["knit-stitch"], related_slugs=["casting-on"],
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
    "걸러뜨기(slip stitch knitting)": _expanded_entry(
        tool_type="needle_knitting", difficulty="confident_beginner", category="texture",
        description="코를 뜨지 않고 왼바늘에서 오른바늘로 옮겨 길어진 코나 가장자리 질감을 만드는 기법입니다.",
        steps=["도안에서 겉뜨기 방향인지 안뜨기 방향인지 확인합니다.", "작업실 위치를 지시대로 앞이나 뒤에 둡니다.", "코를 뜨지 않고 오른바늘로 옮깁니다."],
        mistake="실 위치가 달라 편물 앞에 불필요한 가로실이 생김", fix="wyif·wyib 지시를 확인하고 코를 옮기기 전에 실부터 배치합니다.",
        slug="slip-stitch-knitting", abbreviation="sl 1", symbol_key="slip_knit",
        learning_goal="코 방향과 실 위치를 유지하며 한 코를 안전하게 옮깁니다.",
        practice="가터 바탕에서 매 단 첫 코를 안뜨기 방향으로 걸러 가장자리를 비교하세요.", success_check="걸러진 코가 꼬이지 않고 가장자리 사슬이 고르게 보이나요?",
        motion="hold yarn in back and transfer one stitch purlwise from the left needle to the right needle without knitting it",
        aliases=["걸러뜨기", "코 걸러뜨기", "slip stitch knitting", "sl 1"], prerequisites=["knit-stitch"], related_slugs=["seed-stitch"],
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


_EXISTING_METADATA: dict[str, dict] = {
    "사슬뜨기(chain stitch)": {"category": "basics", "aliases": ["사슬뜨기", "사슬", "chain stitch", "ch"], "prerequisites": ["slip-knot"], "related_slugs": ["single-crochet"]},
    "짧은뜨기(single crochet)": {"category": "basics", "aliases": ["짧은뜨기", "single crochet", "sc"], "prerequisites": ["crochet-chain-stitch"], "related_slugs": ["half-double-crochet", "single-crochet-increase"]},
    "긴뜨기(half double crochet)": {"category": "basics", "aliases": ["긴뜨기", "half double crochet", "hdc"], "prerequisites": ["single-crochet"], "related_slugs": ["double-crochet"]},
    "빼뜨기(slip stitch)": {"category": "basics", "aliases": ["빼뜨기", "slip stitch crochet", "sl st"], "prerequisites": ["crochet-chain-stitch"], "related_slugs": ["round-crochet"]},
    "매직링(magic ring)": {"category": "construction", "aliases": ["매직링", "magic ring", "magic circle", "MR"], "prerequisites": ["crochet-chain-stitch"], "related_slugs": ["round-crochet"]},
    "원형뜨기(round crochet)": {"category": "construction", "aliases": ["코바늘 원형뜨기", "원형뜨기", "round crochet", "crochet in the round"], "prerequisites": ["magic-ring", "single-crochet"], "related_slugs": ["single-crochet-increase"]},
    "한길긴뜨기(double crochet)": {"category": "basics", "aliases": ["한길긴뜨기", "double crochet", "dc"], "prerequisites": ["half-double-crochet"], "related_slugs": ["treble-crochet", "double-crochet-decrease"]},
    "코 잡기(casting on)": {"category": "basics", "aliases": ["코 잡기", "코잡기", "casting on", "cast on", "CO"], "prerequisites": [], "related_slugs": ["knit-stitch", "bind-off"]},
    "겉뜨기(knit stitch)": {"category": "basics", "aliases": ["겉뜨기", "knit stitch", "knit", "K"], "prerequisites": ["casting-on"], "related_slugs": ["purl-stitch", "garter-stitch"]},
    "안뜨기(purl stitch)": {"category": "basics", "aliases": ["안뜨기", "purl stitch", "purl", "P"], "prerequisites": ["casting-on"], "related_slugs": ["knit-stitch", "stockinette-stitch"]},
    "고무뜨기(ribbing)": {"category": "texture", "aliases": ["고무뜨기", "ribbing", "rib stitch", "K1 P1"], "prerequisites": ["knit-stitch", "purl-stitch"], "related_slugs": ["seed-stitch"]},
}

for _name, _lesson in _LESSON_PACKS.items():
    TECHNIQUE_CATALOG[_name].update(_lesson)
for _name, _metadata in _EXISTING_METADATA.items():
    TECHNIQUE_CATALOG[_name].update(_metadata, search_terms=_metadata["aliases"])
TECHNIQUE_CATALOG.update(_EXPANDED_TECHNIQUES)


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
