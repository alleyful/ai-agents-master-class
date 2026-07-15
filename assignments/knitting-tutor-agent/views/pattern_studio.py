"""Pattern studio: presets pre-fill the form; edit and (re)generate a draft.

The agent requires an image and non-empty size/yarn/tool values, so presets seed
sensible non-empty defaults (editable) and the offline path is the bundled sample
bag. A photo upload takes precedence; without a photo, only the sample preset can
generate offline.
"""

import uuid
from pathlib import Path

import streamlit as st

from common import get_agent, initialize_session, temporary_image, debug_metadata
from content.presets import DEFAULT_PRESET, PRESET_NAMES, PROJECT_PRESETS
from knitcoach import DEBUG_MODE, ENABLE_VISION, HAS_OPENAI_KEY, PatternDraft, invoke_turn

_TOOL_FUNC = {"auto": "자동 감지", "crochet": "코바늘", "needle_knitting": "대바늘"}
_SKILL_FUNC = {"beginner": "초보", "confident_beginner": "기초 경험 있음", "intermediate": "중급"}

# Widget-state keys (set programmatically before widgets render on preset change).
K_PRESET, K_TOOL, K_SIZE, K_YARN = "studio_preset", "studio_tool", "studio_size", "studio_yarn"
K_TOOLSIZE, K_GAUGE, K_SKILL, K_NOTES = "studio_toolsize", "studio_gauge", "studio_skill", "studio_notes"
_SAMPLE_IMAGE = Path(__file__).resolve().parent.parent / "samples" / "crochet-mesh-shoulder-bag.png"


def _apply_preset(name: str) -> None:
    preset = PROJECT_PRESETS[name]
    st.session_state[K_TOOL] = preset["tool_type"]
    st.session_state[K_SIZE] = preset["finished_size"]
    st.session_state[K_YARN] = preset["yarn_weight"]
    st.session_state[K_TOOLSIZE] = preset["tool_size"]
    st.session_state[K_GAUGE] = preset["gauge"]
    st.session_state[K_SKILL] = preset["skill_level"]


def render_pattern_draft(data: dict) -> None:
    draft = PatternDraft.model_validate(data)
    st.success("도안 초안을 만들었습니다. 작은 샘플로 먼저 검증해 주세요.")
    st.markdown(f"## {draft.title}")
    st.write(draft.summary)
    metric_cols = st.columns(3)
    metric_cols[0].metric("도구", "코바늘" if draft.tool_type == "crochet" else "대바늘")
    metric_cols[1].metric("신뢰도", draft.confidence)
    metric_cols[2].metric("기법 수", len(draft.techniques))
    left, right = st.columns([1, 1.5])
    with left:
        st.markdown("### 준비물")
        for item in draft.materials:
            st.markdown(f"- {item}")
        st.markdown("### 게이지")
        st.write(draft.gauge_guidance)
        st.markdown("### 작품 구조")
        for item in draft.construction:
            st.markdown(f"- {item}")
    with right:
        st.markdown("### 도안 초안")
        for instruction in draft.instructions:
            st.markdown(f"- {instruction}")
        st.markdown("### 마무리")
        for item in draft.finishing:
            st.markdown(f"- {item}")
    with st.expander("사진에서 확인할 수 없어 가정한 내용", expanded=True):
        for item in draft.assumptions:
            st.markdown(f"- {item}")
        if draft.additional_photos:
            st.markdown("**정확도를 높이는 추가 사진**")
            st.write(", ".join(draft.additional_photos))


def _generate(preset_name: str, image, options: dict) -> None:
    preset_is_sample = PROJECT_PRESETS[preset_name]["sample"]
    if image is not None:
        temp_path = temporary_image(image.getvalue(), Path(image.name).suffix.lower())
        source, image_name = temp_path, image.name
    elif preset_is_sample:
        temp_path, source, image_name = None, _SAMPLE_IMAGE, _SAMPLE_IMAGE.name
    else:
        st.warning("사진을 첨부하거나 '네트 숄더백 (샘플·오프라인)' 프리셋을 선택해 주세요.")
        return
    try:
        with st.spinner("작품 구조를 살펴보고 도안 초안을 만드는 중이에요..."):
            result = invoke_turn(
                get_agent(), "이 이미지로 도안을 만들어줘", uuid.uuid4().hex,
                str(source), task="generate_pattern", pattern_options=options,
                original_image_name=image_name,
            )
        st.session_state.pattern_result = result
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def render() -> None:
    initialize_session()
    st.markdown("# 도안 만들기")
    st.write("프리셋을 고르면 크기·실·바늘이 기본값으로 채워집니다. 값을 바꾸면 그대로 반영돼요.")
    if not (ENABLE_VISION and HAS_OPENAI_KEY):
        st.markdown(
            '<div class="notice">현재 Vision이 꺼져 있어 임의 사진은 분석하지 않습니다. '
            "'네트 숄더백 (샘플)' 프리셋은 API 없이 체험할 수 있습니다.</div>",
            unsafe_allow_html=True,
        )

    if K_TOOL not in st.session_state:
        _apply_preset(DEFAULT_PRESET)
        st.session_state["studio_last_preset"] = DEFAULT_PRESET
        st.session_state.setdefault(K_NOTES, "")

    preset_name = st.selectbox("시작 프리셋", PRESET_NAMES, key=K_PRESET)
    if preset_name != st.session_state["studio_last_preset"]:
        _apply_preset(preset_name)  # runs before the field widgets below render
        st.session_state["studio_last_preset"] = preset_name

    image = st.file_uploader("참고할 뜨개 작품 사진 (선택)", type=["png", "jpg", "jpeg", "webp"])

    with st.expander("세부 조정 (기본값 자동 입력됨)", expanded=True):
        first, second = st.columns(2)
        with first:
            st.selectbox("뜨개 방식", ["auto", "crochet", "needle_knitting"], key=K_TOOL, format_func=_TOOL_FUNC.get)
            st.text_input("원하는 완성 크기", key=K_SIZE)
            st.text_input("실 굵기·종류", key=K_YARN)
        with second:
            st.text_input("바늘 크기", key=K_TOOLSIZE)
            st.text_input("게이지 (선택)", key=K_GAUGE)
            st.selectbox("나의 수준", ["beginner", "confident_beginner", "intermediate"], key=K_SKILL, format_func=_SKILL_FUNC.get)
        st.text_area("추가 요청", key=K_NOTES, placeholder="예: 안감 없이 만들고 손잡이는 짧게 하고 싶어요.")

    submitted = st.button("도안 초안 만들기", type="primary", use_container_width=True)

    if submitted:
        if not all([st.session_state[K_SIZE].strip(), st.session_state[K_YARN].strip(), st.session_state[K_TOOLSIZE].strip()]):
            st.warning("완성 크기, 실 굵기와 바늘 크기는 비워둘 수 없어요.")
        else:
            options = {
                "tool_type": st.session_state[K_TOOL],
                "finished_size": st.session_state[K_SIZE],
                "yarn_weight": st.session_state[K_YARN],
                "tool_size": st.session_state[K_TOOLSIZE],
                "gauge": st.session_state[K_GAUGE] or "미측정",
                "skill_level": st.session_state[K_SKILL],
                "notes": st.session_state[K_NOTES],
            }
            _generate(preset_name, image, options)

    result = st.session_state.pattern_result
    if result:
        st.divider()
        if result.get("pattern_draft"):
            render_pattern_draft(result["pattern_draft"])
            st.caption("값을 바꾸고 '도안 초안 만들기'를 다시 누르면 조정된 초안을 만듭니다.")
        else:
            st.info(result.get("user_response", "도안 초안을 만들지 못했습니다."))
        if DEBUG_MODE:
            with st.expander("개발자 정보"):
                st.json(debug_metadata(result))
