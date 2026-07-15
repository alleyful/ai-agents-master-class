"""Browsable technique library backed by the canonical lesson-pack catalog."""

from collections.abc import Callable
from pathlib import Path

import streamlit as st

import ui
from content.symbols import technique_symbol_svg
from content.techniques import TECHNIQUES, get_technique, list_techniques

_BASE_DIR = Path(__file__).resolve().parent.parent
_TOOL_MAP = {"코바늘": "crochet", "대바늘": "needle_knitting"}
_TOOL_LABEL = {"crochet": "코바늘", "needle_knitting": "대바늘"}
_LEVEL_LABEL = {
    "beginner": "입문",
    "confident_beginner": "기초 경험",
    "intermediate": "중급",
}
_LEVEL_FILTER = {"전체 난이도": None, "입문": "beginner", "기초 경험": "confident_beginner", "중급": "intermediate"}
_CATEGORY_FILTER = {
    "전체 카테고리": None,
    "기초": "basics",
    "늘림·줄임": "shaping",
    "무늬·질감": "texture",
    "구성·연결": "construction",
    "마무리": "finishing",
}
_CATEGORY_LABEL = {value: label for label, value in _CATEGORY_FILTER.items() if value is not None}


def _render_detail(name: str, on_ask: Callable[[str], None] | None) -> None:
    technique = get_technique(name)
    if technique is None:
        st.session_state.pop("selected_technique", None)
        st.rerun()
        return

    if st.button("← 전체 기법", key="tech_back"):
        st.session_state.pop("selected_technique", None)
        st.rerun()

    symbol, heading = st.columns([1, 4], vertical_alignment="center")
    with symbol:
        st.markdown(
            technique_symbol_svg(technique.symbol_key, technique.abbreviation),
            unsafe_allow_html=True,
        )
    with heading:
        st.markdown(
            ui.tag(f"{_TOOL_LABEL[technique.tool_type]} · {_LEVEL_LABEL[technique.difficulty]}"),
            unsafe_allow_html=True,
        )
        st.markdown(f"# {technique.name.split('(')[0]}")
        st.caption(f"도안 약어 {technique.abbreviation}")

    if not technique.symbol_standard:
        st.caption("이 기호는 복합 기법을 이해하기 위한 학습용 미니 차트입니다. 실제 도안의 범례를 우선하세요.")
    else:
        st.caption("일반적인 도안 기호를 단순화해 표시했습니다. 출판 도안에서는 반드시 해당 범례를 함께 확인하세요.")

    st.markdown("### 무엇을 배우나요?")
    st.write(technique.description)
    st.info(technique.learning_goal)

    if technique.prerequisites:
        prerequisite_names = [
            item.name.split("(")[0]
            for slug in technique.prerequisites
            if (item := get_technique(slug)) is not None
        ]
        if prerequisite_names:
            st.caption(f"먼저 알면 좋아요 · {' · '.join(prerequisite_names)}")

    st.markdown("### 손동작 순서")
    for index, step in enumerate(technique.steps, start=1):
        st.markdown(f"**{index:02d}**　{step}")

    st.markdown("### 자주 하는 실수와 교정")
    for mistake, fix in technique.mistakes_with_fixes:
        with st.container(border=True):
            st.markdown(f"**{mistake}**")
            st.caption(f"교정 · {fix}")

    practice, check = st.columns(2)
    with practice.container(border=True):
        st.markdown("#### 짧은 연습")
        st.write(technique.practice)
    with check.container(border=True):
        st.markdown("#### 성공 체크")
        st.write(technique.success_check)

    st.markdown("### 영상 가이드")
    asset_path = _BASE_DIR / technique.video_asset_path
    if asset_path.is_file():
        st.video(str(asset_path))
    else:
        status = "파일럿 생성 대상" if technique.video_status == "pilot" else "프롬프트 준비 완료"
        st.info(f"{status} · 생성한 MP4를 `{technique.video_asset_path}`에 넣으면 여기에 표시됩니다.")
    with st.expander("AI 영상 생성 프롬프트", expanded=not asset_path.is_file()):
        st.code(technique.video_generation_prompt, language=None, wrap_lines=True)

    if on_ask is not None:
        st.button(
            "이 기법을 선생님에게 질문하기",
            key=f"ask_{technique.slug}",
            on_click=on_ask,
            args=(technique.name,),
            use_container_width=True,
            type="primary",
        )


def _render_grid() -> None:
    st.markdown(
        f'<span class="library-kicker">TECHNIQUE LIBRARY · {len(TECHNIQUES)} LESSON PACKS</span>',
        unsafe_allow_html=True,
    )
    st.markdown("# 기법 찾아보기")
    st.write("기호를 먼저 익히고, 손동작과 실수 교정까지 한 세트로 살펴보세요.")

    query = st.text_input(
        "기법 검색",
        placeholder="기법명, 영문명 또는 도안 약어로 검색",
        label_visibility="collapsed",
    )
    filter_col, level_col, category_col = st.columns(3)
    tool_filter = filter_col.segmented_control("도구", ["전체", "코바늘", "대바늘"], default="전체")
    level_filter = level_col.selectbox("난이도", list(_LEVEL_FILTER), label_visibility="collapsed")
    category_filter = category_col.selectbox("카테고리", list(_CATEGORY_FILTER), label_visibility="collapsed")
    tool = _TOOL_MAP.get(tool_filter)
    items = list_techniques(
        tool=tool,
        level=_LEVEL_FILTER[level_filter],
        category=_CATEGORY_FILTER[category_filter],
        query=query,
    )

    st.caption(f"{len(items)}개의 기법")

    if not items:
        st.info("조건에 맞는 기법이 없습니다.")
        return

    for start in range(0, len(items), 2):
        for col, technique in zip(st.columns(2), items[start:start + 2]):
            with col.container(border=True):
                symbol, copy = st.columns([1, 3], vertical_alignment="center")
                with symbol:
                    st.markdown(
                        technique_symbol_svg(technique.symbol_key, technique.abbreviation, compact=True),
                        unsafe_allow_html=True,
                    )
                with copy:
                    st.caption(
                        f"{_TOOL_LABEL[technique.tool_type]} · {_LEVEL_LABEL[technique.difficulty]} · "
                        f"{_CATEGORY_LABEL[technique.category]}"
                    )
                    st.markdown(f"### {technique.name.split('(')[0]}")
                    st.caption(technique.learning_goal)
                if st.button("설명 세트 보기 →", key=f"tech_{technique.slug}", use_container_width=True):
                    st.session_state.selected_technique = technique.name
                    st.rerun()


def render(on_ask: Callable[[str], None] | None = None) -> None:
    selected = st.session_state.get("selected_technique")
    if selected:
        _render_detail(selected, on_ask)
    else:
        _render_grid()
