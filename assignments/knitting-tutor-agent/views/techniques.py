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


def _symbol_presentation(technique) -> tuple[str, str]:
    if technique.display_symbol_kind == "standard":
        return "표준 도안 기호", "CYC 계열의 일반적인 도안 기호입니다. 출판 도안에서는 해당 범례를 함께 확인하세요."
    if technique.display_symbol_kind == "modifier":
        return "도안 보조 표시", "독립된 코 기호가 아니라 실제로 뜰 코의 기호에 붙여 사용하는 보조 표시입니다."
    return "학습 아이콘", "동작과 구조를 설명하기 위한 학습 아이콘이며 범용 도안 기호가 아닙니다."


def _render_reference_cards(technique) -> None:
    with st.container(border=True, key="chain_board"):
        english_name = technique.name.split("(", 1)[1].rstrip(")").upper() if "(" in technique.name else technique.slug.upper()
        st.markdown(f'<span class="chain-board-kicker">{english_name} · QUICK VIEW</span>', unsafe_allow_html=True)
        st.markdown(f"#### {technique.name.split('(')[0]} 동작 흐름")
        st.caption("왼쪽에서 오른쪽으로 실제 손과 바늘의 위치를 따라가세요.")

        cards = technique.reference_cards
        for row_start in range(0, len(cards), 3):
            row_cards = cards[row_start : row_start + 3]
            columns = st.columns(len(row_cards))
            for offset, column in enumerate(columns):
                index = row_start + offset
                card = cards[index]
                with column.container(border=True, key=f"chain_card_{index + 1}"):
                    st.markdown(
                        f'<span class="chain-step-number">{index + 1:02d}</span>',
                        unsafe_allow_html=True,
                    )
                    st.image(str(_BASE_DIR / card["path"]), width="stretch")
                    st.markdown(f'<div class="chain-card-title">{card["title"]}</div>', unsafe_allow_html=True)
                    st.caption(card["description"])


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
    symbol_label, symbol_caption = _symbol_presentation(technique)
    with symbol:
        st.markdown(
            technique_symbol_svg(
                technique.symbol_key,
                technique.abbreviation,
                accessible_kind=symbol_label,
            ),
            unsafe_allow_html=True,
        )
    with heading:
        st.markdown(
            ui.tag(f"{_TOOL_LABEL[technique.tool_type]} · {_LEVEL_LABEL[technique.difficulty]}"),
            unsafe_allow_html=True,
        )
        st.markdown(f"# {technique.name.split('(')[0]}")
        abbreviation_label = "표준 도안 약어" if technique.abbreviation_standard else "검색·학습 표기"
        st.caption(f"{abbreviation_label} · {technique.abbreviation}")

    st.caption(f"{symbol_label} · {symbol_caption}")

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

    reference_videos = technique.reference_videos or (
        [{"url": technique.reference_video_url, "title": technique.reference_video_title or "기초 기법 영상", "focus": ""}]
        if technique.reference_video_url else []
    )
    if reference_videos:
        st.markdown("### 1. 실제 손동작 먼저 보기")
        if technique.slug == "crochet-chain-stitch":
            st.write("완전 초보라면 실제 양손의 위치를 먼저 보세요. 재생 속도를 0.5배로 낮추고 아래 세 장면에서 잠시 멈추면 좋아요.")
            st.markdown(
                "- 왼손 검지에 실을 걸고 엄지·중지로 마지막 사슬 바로 아래를 잡는 모습\n"
                "- 코바늘 홈을 아래로 돌려 실을 잡는 순간\n"
                "- 바늘 위 현재 고리는 세지 않고, 바늘 아래 V 모양만 세는 모습"
            )
        else:
            st.write("실제 양손의 위치와 바늘이 들어가는 지점을 먼저 확인하세요. 필요하면 0.5배속으로 낮추고 한 코가 완성되는 구간을 반복해 보세요.")
        for index, reference in enumerate(reference_videos, start=1):
            st.markdown(f"#### {index}. {reference['title']}")
            if reference.get("focus"):
                st.caption(reference["focus"])
            st.video(reference["url"])
            st.link_button("YouTube에서 크게 보기", reference["url"], use_container_width=True)
        if technique.reference_article_url:
            st.link_button("사진 5단계 설명 함께 보기", technique.reference_article_url, use_container_width=True)

    review_title = "### 2. 핵심 장면으로 복습" if technique.reference_cards else "### 2. 영상으로 복습"
    st.markdown(review_title if reference_videos else "### 영상 가이드")
    asset_path = _BASE_DIR / technique.video_asset_path
    if technique.reference_cards:
        overview_tab, slide_tab = st.tabs(["한눈에 보기", "한 장씩 보기"])
        with overview_tab:
            _render_reference_cards(technique)
        with slide_tab:
            step_labels = [f"{index + 1} {card['title']}" for index, card in enumerate(technique.reference_cards)]
            selected_step = st.radio(
                "확인할 단계",
                options=range(len(step_labels)),
                format_func=lambda index: step_labels[index],
                horizontal=True,
                label_visibility="collapsed",
                key=f"reference_step_{technique.slug}",
            )
            st.image(
                str(_BASE_DIR / technique.reference_cards[selected_step]["path"]),
                width="stretch",
            )
            selected_card = technique.reference_cards[selected_step]
            st.markdown(f"#### {selected_step + 1:02d} · {selected_card['title']}")
            st.info(selected_card["description"])
    elif asset_path.is_file():
        st.video(str(asset_path))
        if reference_videos:
            st.caption("이 로컬 영상은 실제 손동작을 본 뒤 실의 이동 경로와 도안 기호를 복습하는 보조 자료입니다.")
    else:
        status = "파일럿 생성 대상" if technique.video_status == "pilot" else "프롬프트 준비 완료"
        st.info(f"{status} · 생성한 MP4를 `{technique.video_asset_path}`에 넣으면 여기에 표시됩니다.")
    if not technique.reference_cards:
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
    st.write("표준 도안 기호와 약어는 정확히 익히고, 기호가 없는 작업 방식은 학습 아이콘과 손동작으로 살펴보세요.")

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
                    symbol_label, _ = _symbol_presentation(technique)
                    st.markdown(
                        technique_symbol_svg(
                            technique.symbol_key,
                            technique.abbreviation,
                            compact=True,
                            accessible_kind=symbol_label,
                        ),
                        unsafe_allow_html=True,
                    )
                    st.caption(symbol_label)
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
