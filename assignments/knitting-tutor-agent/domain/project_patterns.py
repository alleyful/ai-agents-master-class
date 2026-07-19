"""Pre-authored project phases and deterministic chart data.

The model may help explain a pattern, but curated beginner projects use these
reviewable structures for progress and chart rendering.
"""

from pydantic import BaseModel, Field


class ProjectPhase(BaseModel):
    id: str
    title: str
    step_ids: list[str]
    description: str = ""


class CrochetRound(BaseModel):
    number: int
    stitch_count: int
    singles_before_increase: int | None = None
    instruction: str
    notation: str
    techniques: list[str] = Field(default_factory=list)


class RadialCrochetChart(BaseModel):
    project_id: str
    construction: str
    center_stitches: int
    rounds: list[CrochetRound]


PROJECT_PHASES: dict[str, list[ProjectPhase]] = {
    "crochet-round-coaster": [
        ProjectPhase(id="start", title="시작", step_ids=["round-1"], description="매직링과 중심 6코"),
        ProjectPhase(
            id="base",
            title="원형 바탕",
            step_ids=[f"round-{number}" for number in range(2, 9)],
            description="매 단 6코씩 늘리기",
        ),
        ProjectPhase(id="finish", title="마무리", step_ids=["finish"], description="높이 차와 실 끝 정리"),
    ],
    "crochet-mini-hat-keyring": [
        ProjectPhase(id="start", title="시작", step_ids=["top-1-2"], description="매직링과 꼭대기 시작"),
        ProjectPhase(id="crown", title="모자 윗면", step_ids=["top-3-4"], description="평평한 원형 만들기"),
        ProjectPhase(id="side", title="옆면", step_ids=["side-5-8"], description="BLO로 꺾어 높이 만들기"),
        ProjectPhase(id="brim", title="챙", step_ids=["brim-9-10"], description="챙을 고르게 늘리기"),
        ProjectPhase(id="finish", title="마무리", step_ids=["finish-11"], description="챙 정리와 키링 연결"),
    ],
    "crochet-fishbread-keyring": [
        ProjectPhase(id="start", title="시작", step_ids=["round-1"], description="몸통 중심 만들기"),
        ProjectPhase(
            id="body",
            title="몸통",
            step_ids=[f"round-{number}" for number in range(2, 11)],
            description="늘림·평단·줄임으로 형태 만들기",
        ),
        ProjectPhase(id="tail", title="꼬리", step_ids=["round-11", "round-12"], description="꼬리 바탕과 부채꼴"),
        ProjectPhase(id="finish", title="마무리", step_ids=["finish"], description="자수와 키링 연결"),
    ],
    "crochet-flat-pouch": [
        ProjectPhase(id="start", title="바닥", step_ids=["base-round-1"], description="사슬 양쪽을 돌아 시작"),
        ProjectPhase(id="body", title="몸통", step_ids=["body-rounds-2-24"], description="40코 원통을 유지"),
        ProjectPhase(
            id="opening",
            title="입구",
            step_ids=["eyelets-round-25", "edge-round-26"],
            description="조임끈 구멍과 입구 정리",
        ),
        ProjectPhase(id="finish", title="마무리", step_ids=["cord"], description="조임끈 만들기"),
    ],
    "needle-garter-scarf": [
        ProjectPhase(id="start", title="시작", step_ids=["cast-on"], description="코잡기 18코"),
        ProjectPhase(
            id="body",
            title="줄무늬 몸판",
            step_ids=["stripe-1", "stripe-2", "repeat"],
            description="겉뜨기 줄무늬 반복",
        ),
        ProjectPhase(id="finish", title="마무리", step_ids=["bind-off"], description="느슨한 코막음과 실 정리"),
    ],
    "needle-ribbed-muffler": [
        ProjectPhase(id="start", title="시작 준비", step_ids=["swatch"], description="골지 게이지와 28코 시작"),
        ProjectPhase(id="pattern", title="골지 익히기", step_ids=["row-1", "rows-2-12"], description="겉1·안1 골 맞추기"),
        ProjectPhase(id="body", title="몸판 반복", step_ids=["repeat"], description="길이 120cm까지 유지"),
        ProjectPhase(id="finish", title="마무리", step_ids=["bind-off"], description="무늬대로 느슨하게 코막음"),
    ],
}


COASTER_CHART = RadialCrochetChart(
    project_id="crochet-round-coaster",
    construction="continuous_spiral",
    center_stitches=6,
    rounds=[
        CrochetRound(
            number=1,
            stitch_count=6,
            instruction="매직링 안에 짧은뜨기 6코를 뜨고 첫 코에 표시링을 거세요.",
            notation="MR 안에 X 6",
            techniques=["매직링", "짧은뜨기"],
        ),
        *[
            CrochetRound(
                number=number,
                stitch_count=number * 6,
                singles_before_increase=number - 2,
                instruction=(
                    "앞 단의 각 코에 짧은뜨기 2코씩 떠서 12코로 늘리세요."
                    if number == 2
                    else f"짧은뜨기 {number - 2}코와 늘려뜨기 1회를 여섯 번 반복하세요."
                ),
                notation=("V × 6" if number == 2 else f"({number - 2}X, V) × 6"),
                techniques=["짧은뜨기", "짧은뜨기 늘려뜨기"],
            )
            for number in range(2, 9)
        ],
    ],
)


MINI_HAT_CHART = RadialCrochetChart(
    project_id="crochet-mini-hat-keyring",
    construction="crown_to_brim",
    center_stitches=6,
    rounds=[
        CrochetRound(number=1, stitch_count=6, instruction="매직링 안에 짧은뜨기 6코", notation="MR 안에 X 6", techniques=["매직링", "짧은뜨기"]),
        CrochetRound(number=2, stitch_count=12, instruction="모든 코에 늘려뜨기", notation="V × 6", techniques=["짧은뜨기 늘려뜨기"]),
        CrochetRound(number=3, stitch_count=18, instruction="짧은뜨기 1코와 늘려뜨기 1회 반복", notation="(X, V) × 6", techniques=["짧은뜨기", "짧은뜨기 늘려뜨기"]),
        CrochetRound(number=4, stitch_count=24, instruction="짧은뜨기 2코와 늘려뜨기 1회 반복", notation="(2X, V) × 6", techniques=["짧은뜨기", "짧은뜨기 늘려뜨기"]),
        CrochetRound(number=5, stitch_count=24, instruction="뒤 고리 한 가닥에만 짧은뜨기 24코", notation="BLO X 24", techniques=["짧은뜨기"]),
        *[
            CrochetRound(number=number, stitch_count=24, instruction="짧은뜨기 24코", notation="X 24", techniques=["짧은뜨기"])
            for number in range(6, 9)
        ],
        CrochetRound(number=9, stitch_count=30, instruction="짧은뜨기 3코와 늘려뜨기 1회 반복", notation="(3X, V) × 6", techniques=["짧은뜨기", "짧은뜨기 늘려뜨기"]),
        CrochetRound(number=10, stitch_count=36, instruction="짧은뜨기 4코와 늘려뜨기 1회 반복", notation="(4X, V) × 6", techniques=["짧은뜨기", "짧은뜨기 늘려뜨기"]),
        CrochetRound(number=11, stitch_count=36, instruction="짧은뜨기 36코 뒤 다음 코에 빼뜨기", notation="X 36, SLST", techniques=["짧은뜨기", "빼뜨기"]),
    ],
)


RADIAL_CROCHET_CHARTS: dict[str, RadialCrochetChart] = {
    COASTER_CHART.project_id: COASTER_CHART,
}


def phases_for_project(project_id: str) -> list[ProjectPhase]:
    return PROJECT_PHASES.get(project_id, [])


def phase_index_for_step(project_id: str, step_id: str) -> int:
    for index, phase in enumerate(phases_for_project(project_id)):
        if step_id in phase.step_ids:
            return index
    return 0


def phase_progress(project_id: str, step_id: str) -> tuple[int, int]:
    phases = phases_for_project(project_id)
    if not phases:
        return (1, 1)
    phase = phases[phase_index_for_step(project_id, step_id)]
    try:
        return (phase.step_ids.index(step_id) + 1, len(phase.step_ids))
    except ValueError:
        return (1, len(phase.step_ids) or 1)
