"""User-journey catalog and deterministic journey inference."""

from .models import JourneyDefinition, JourneyType


JOURNEY_DEFINITIONS: dict[JourneyType, JourneyDefinition] = {
    JourneyType.START_FROM_ZERO: JourneyDefinition(
        title="처음부터 배우기",
        description="도구가 없어도 괜찮아요",
        prompt="무엇을 만들어 보고 싶나요?",
        placeholder="예: 뜨개질은 처음인데 작은 가방을 만들어 보고 싶어요",
        mode="start",
        steps=("목표 확인", "도구 선택", "첫 연습"),
        icon="○",
    ),
    JourneyType.CONTINUE_LEARNING: JourneyDefinition(
        title="배운 내용 이어가기",
        description="지난 연습 다음 단계로",
        prompt="지난 연습에서 어땠나요?",
        placeholder="예: 사슬뜨기는 되는데 코 크기가 들쭉날쭉해요",
        mode="continue",
        steps=("진도 확인", "성공 체크", "다음 기법"),
        icon="↗",
    ),
    JourneyType.DIAGNOSE_PROJECT: JourneyDefinition(
        title="작품 문제 해결하기",
        description="사진으로 원인을 좁혀요",
        prompt="어디에서 문제가 생겼나요?",
        placeholder="예: 코스터 가장자리가 자꾸 휘고 코 수가 늘어나요",
        mode="diagnose",
        steps=("사진 확인", "원인 좁히기", "한 가지 수정"),
        icon="◇",
    ),
    JourneyType.RECREATE_FROM_PHOTO: JourneyDefinition(
        title="사진 속 작품 만들기",
        description="구조와 필요한 기법부터",
        prompt="어떤 작품을 만들어 보고 싶나요?",
        placeholder="예: 이 네트 가방을 조금 작은 크기로 만들고 싶어요",
        mode="pattern",
        steps=("구조 분석", "조건 확인", "테스트 도안"),
        icon="▧",
    ),
    JourneyType.EXPLAIN_PATTERN: JourneyDefinition(
        title="도안 풀어 읽기",
        description="약어와 반복 구간을 쉽게",
        prompt="어느 부분부터 어려운가요?",
        placeholder="예: ch 12, sc in each ch가 무슨 뜻인지 모르겠어요",
        mode="pattern_read",
        steps=("약어 찾기", "한 단씩 설명", "기법 연결"),
        icon="≡",
    ),
    JourneyType.START_FROM_MATERIALS: JourneyDefinition(
        title="가진 재료로 시작하기",
        description="실과 바늘에 맞는 작품 찾기",
        prompt="가지고 있는 실과 바늘을 알려주세요",
        placeholder="예: 중간 굵기 실 두 타래와 5mm 코바늘이 있어요",
        mode="tools",
        steps=("재료 확인", "작품 추천", "준비물 점검"),
        icon="⌁",
    ),
}


def infer_journey(
    text: str,
    *,
    input_type: str,
    intent: str,
    has_image: bool = False,
    task: str = "tutor",
) -> JourneyType:
    """Map a turn to one of the six product journeys without a model call."""
    lowered = text.casefold()
    if task == "generate_pattern" or intent == "generate_pattern":
        return JourneyType.RECREATE_FROM_PHOTO
    if input_type in {"pattern_text", "explanation_text"} or intent == "convert_pattern":
        return JourneyType.EXPLAIN_PATTERN
    if input_type == "tool_question" or intent == "advise_tools":
        return JourneyType.START_FROM_MATERIALS
    if any(
        word in lowered
        for word in ("가지고 있는 실", "가진 실", "실 두 타래", "실 한 타래", "실 라벨", "이 실로", "이 바늘로")
    ):
        return JourneyType.START_FROM_MATERIALS
    if input_type == "feedback" or intent == "revise_output" or any(
        word in lowered for word in ("지난", "이어서", "연습 결과", "다음 단계", "배웠")
    ):
        return JourneyType.CONTINUE_LEARNING
    if any(
        word in lowered
        for word in ("처음", "아무것도 몰", "입문", "시작하고 싶", "처음부터")
    ):
        return JourneyType.START_FROM_ZERO
    if has_image and any(
        word in lowered for word in ("만들", "도안", "따라", "비슷하게", "어떻게 뜨")
    ):
        return JourneyType.RECREATE_FROM_PHOTO
    if intent == "analyze_artifact" or any(
        word in lowered
        for word in ("문제", "막혔", "안 돼", "왜", "늘어나", "줄어", "휘어", "말려", "빠져")
    ):
        return JourneyType.DIAGNOSE_PROJECT
    return JourneyType.CONTINUE_LEARNING
