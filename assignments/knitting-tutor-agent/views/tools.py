"""Browsable tool library and gauge workshop."""

from collections.abc import Callable
from pathlib import Path

import streamlit as st

import ui
from content.tools import (
    BRAND_GUIDES,
    TOOL_DIAMETER_TABLES,
    TOOL_IMAGE_PATHS,
    TOOL_LENGTH_TABLES,
    YARN_LABEL_CHECKLIST,
    YARN_WEIGHT_GUIDE,
    calculate_gauge,
    get_tool,
    list_tools,
    recommend_tools,
)

_BASE_DIR = Path(__file__).resolve().parent.parent

CRAFTS = {"전체": None, "코바늘": "crochet", "대바늘": "needle_knitting", "공통": "both"}
CATEGORIES = {"전체 종류": None, "바늘": "needle", "필수 도구": "essential", "부자재": "notion", "마무리": "finishing", "측정": "measurement"}
CRAFT_LABEL = {"crochet": "코바늘", "needle_knitting": "대바늘", "both": "공통"}
CATEGORY_LABEL = {"needle": "바늘", "essential": "필수", "notion": "부자재", "finishing": "마무리", "measurement": "측정"}


def _gauge_workshop() -> None:
    st.markdown("## 대바늘 의류용 게이지 스와치")
    st.write("게이지는 **세탁·건조까지 마친 편물 10cm 안의 코 수와 단 수**입니다. 의류·모자처럼 완성 치수가 중요한 작품은 바늘 호수보다 이 값이 우선입니다.")
    for index, step in enumerate([
        "도안과 같은 실·바늘·무늬로 가장자리 여유를 둔 15cm 안팎 샘플을 뜹니다.",
        "완성품과 같은 방법으로 세탁하고, 잡아 늘이지 말고 평평하게 말립니다.",
        "가장자리를 피해 중앙에서 가로와 세로를 재고 그 안의 코와 단을 셉니다.",
        "10cm 값으로 환산해 도안과 비교하고 바늘을 바꾼 뒤 새 스와치를 뜹니다.",
    ], 1):
        st.markdown(f"**{index:02d}**　{step}")
    st.warning("샘플이 목표보다 크게 나온 경우 보통 더 작은 바늘, 작게 나온 경우 더 큰 바늘을 씁니다. 아래 계산기는 같은 뜻을 ‘10cm 코 수’ 기준으로 안내합니다.")

    with st.container(border=True):
        st.markdown("#### 내 스와치 계산")
        a, b = st.columns(2)
        stitches = a.number_input("센 코 수", min_value=1.0, value=22.0, step=1.0)
        width = b.number_input("잰 가로 길이(cm)", min_value=1.0, value=10.0, step=0.5)
        c, d = st.columns(2)
        rows = c.number_input("센 단 수", min_value=1.0, value=30.0, step=1.0)
        height = d.number_input("잰 세로 길이(cm)", min_value=1.0, value=10.0, step=0.5)
        target = st.number_input("도안의 목표 코 수/10cm (모르면 0)", min_value=0.0, value=0.0, step=0.5)
        result = calculate_gauge(stitches, rows, width, height, target or None)
        left, right = st.columns(2)
        left.metric("코 게이지", f"{result['stitches_10cm']:.1f}코 / 10cm")
        right.metric("단 게이지", f"{result['rows_10cm']:.1f}단 / 10cm")
        st.info(result["advice"])

    with st.expander("실 굵기별 시작 바늘 범위", expanded=False):
        st.caption("Craft Yarn Council의 일반 범위입니다. 도안·실 라벨과 실제 스와치가 우선입니다.")
        st.dataframe(YARN_WEIGHT_GUIDE, width="stretch", hide_index=True, column_config={
            "weight": "실 굵기", "examples": "예시", "needle_mm": "대바늘 mm", "hook_mm": "코바늘 mm", "knit_sts_10cm": "메리야스 코/10cm",
        })


def _render_detail(slug: str, on_ask: Callable[[str], None] | None) -> None:
    item = get_tool(slug)
    if item is None:
        st.session_state.pop("selected_tool", None)
        st.rerun()
    if st.button("← 전체 도구", key="tool_back"):
        st.session_state.pop("selected_tool", None)
        st.rerun()
    st.markdown(ui.tag(f"{CRAFT_LABEL[item.craft]} · {CATEGORY_LABEL[item.category]}"), unsafe_allow_html=True)
    st.markdown(f"# {item.name}")
    image_path = _BASE_DIR / TOOL_IMAGE_PATHS[item.slug]
    with st.container(key="tool_detail_illustration"):
        st.image(str(image_path), caption=f"{item.name}의 대표 형태를 단순화한 학습용 일러스트", width="stretch")
    st.write(item.summary)
    with st.container(border=True):
        st.markdown("#### 잘 맞는 작업")
        st.markdown("\n".join(f"- {value}" for value in item.best_for))

    if item.slug == "single-crochet-hook":
        st.markdown("### 실 라벨에서 먼저 볼 것")
        st.write("코바늘은 보통 게이지 계산부터 시작하지 않습니다. 실 라벨이나 도안의 권장 코바늘을 확인하고, 그 규격으로 작은 시작 샘플을 떠 손땀과 원하는 조직을 봅니다.")
        for index, value in enumerate(YARN_LABEL_CHECKLIST, start=1):
            st.markdown(f"**{index}.** {value}")
    if item.size_guide:
        st.markdown("### 규격을 읽는 법")
        st.markdown("\n".join(f"- {value}" for value in item.size_guide))
    diameter_table = TOOL_DIAMETER_TABLES.get(item.slug)
    if diameter_table:
        st.markdown("### 1. 바늘 굵기 고르기")
        st.write("**mm는 바늘 몸통이나 팁의 지름**입니다. 코 크기와 게이지에 영향을 주므로 실 라벨·도안의 권장 mm에서 시작하세요.")
        st.dataframe(
            diameter_table,
            width="stretch",
            hide_index=True,
            column_config={"marking": "호수·제품 표기", "mm": "바늘 지름", "yarn_start": "실 굵기 출발점"},
        )
        if item.slug in {"single-crochet-hook", "steel-crochet-hook"}:
            st.caption("호수/mm 대응은 Tulip의 표기를 기준으로 정리한 출발표입니다. 브랜드·제품군마다 제공 규격이 다를 수 있으니 제품 몸통의 mm와 실 라벨을 함께 확인하세요.")
        elif item.craft == "needle_knitting":
            st.caption("국내에서 함께 쓰이는 일본식 호수 대응입니다. 국가·브랜드마다 호수 체계가 다르므로 제품에 적힌 mm를 최종 기준으로 보세요.")
        elif item.slug == "tunisian-hook":
            st.caption("아후강 뜨기는 조직이 조밀해지기 쉬워 일반 코바늘 권장치보다 1–2mm 크게 시작하기도 합니다. 도안 지정 규격이 가장 우선입니다.")
    length_table = TOOL_LENGTH_TABLES.get(item.slug)
    if length_table:
        st.markdown("### 2. 바늘·케이블 길이 고르기")
        st.write("**cm는 코를 수용하는 바늘·팁·케이블의 길이**입니다. 바늘 굵기와는 별개이므로 작품 폭·둘레와 코 수에 맞춰 따로 고릅니다.")
        st.dataframe(
            length_table,
            width="stretch",
            hide_index=True,
            column_config={"length": "표기 길이", "measured_as": "어디를 잰 길이?", "use": "주로 쓰는 작업"},
        )
        if item.slug == "fixed-circular":
            st.info("고정형 줄바늘의 40·60·80cm는 보통 케이블만이 아니라 **두 바늘 팁을 포함한 끝↔끝 완성 길이**입니다.")
        elif item.slug == "interchangeable-needles":
            st.info("교체식 케이블 포장은 **케이블 단독 길이** 또는 **팁 결합 후 완성 길이** 중 하나를 쓸 수 있습니다. 같은 숫자라도 브랜드 표기 기준을 확인하세요.")
    st.markdown("### 구매 전 체크")
    st.markdown("\n".join(f"- {value}" for value in item.buying_tips))
    budget, upgrade = st.columns(2)
    with budget.container(border=True):
        st.markdown("#### 처음·가성비")
        st.write(item.budget_choice)
    with upgrade.container(border=True):
        st.markdown("#### 취향이 생긴 뒤")
        st.write(item.upgrade_choice)
    if on_ask:
        st.button("이 도구를 선생님에게 질문하기", on_click=on_ask, args=(item.name,), width="stretch", type="primary")


def _selection_helper() -> None:
    with st.expander("내 프로젝트 도구 빠르게 고르기", expanded=False):
        craft_label = st.segmented_control("뜨개 방식", ["아직 모름", "코바늘", "대바늘"], default="아직 모름")
        project = st.text_input("만들 작품", placeholder="예: 첫 목도리, 아미구루미, 모자")
        level = st.segmented_control("경험", ["첫 작품", "기초 경험", "업그레이드"], default="첫 작품")
        if project:
            tool_type = {"코바늘": "crochet", "대바늘": "needle_knitting"}.get(craft_label, "unknown")
            mapped_level = {"첫 작품": "first_project", "기초 경험": "beginner", "업그레이드": "upgrading"}[level]
            for advice in recommend_tools(project, tool_type, mapped_level):
                st.success(advice)
            st.caption("정확한 mm는 실 라벨과 도안의 게이지를 확인한 뒤 결정하세요.")


def _render_grid() -> None:
    st.markdown(f'<span class="library-kicker">TOOL LIBRARY · {len(list_tools())} GUIDES</span>', unsafe_allow_html=True)
    st.markdown("# 도구와 부자재 찾아보기")
    st.write("처음에는 필요한 규격 하나만, 취향이 생긴 뒤에는 재질과 시스템을 비교하세요. 가격 대신 구매 단계와 용도를 기준으로 안내합니다.")
    _selection_helper()
    query = st.text_input("도구 검색", placeholder="예: 줄바늘, 숏팁, 아후강, 가위, 가방 부자재", label_visibility="collapsed")
    craft_col, category_col = st.columns(2)
    craft_label = craft_col.segmented_control("방식", list(CRAFTS), default="전체")
    category_label = category_col.selectbox("종류", list(CATEGORIES), label_visibility="collapsed")
    craft = CRAFTS[craft_label]
    items = list_tools(craft=craft, category=CATEGORIES[category_label], query=query)
    if craft == "both":
        items = [item for item in items if item.craft == "both"]
    st.caption(f"{len(items)}개의 도구 안내")
    for start in range(0, len(items), 2):
        for column, item in zip(st.columns(2), items[start:start + 2]):
            with column.container(border=True, key=f"tool_grid_card_{item.slug}"):
                st.image(str(_BASE_DIR / TOOL_IMAGE_PATHS[item.slug]), width="stretch")
                st.caption(f"{CRAFT_LABEL[item.craft]} · {CATEGORY_LABEL[item.category]}")
                st.markdown(f"### {item.name}")
                st.write(item.summary)
                st.caption(" · ".join(item.best_for[:3]))
                if st.button("선택 기준 보기 →", key=f"tool_{item.slug}", width="stretch"):
                    st.session_state.selected_tool = item.slug
                    st.rerun()
    with st.expander("대바늘 의류를 뜰 때 · 게이지 내는 법과 계산기", expanded=False):
        _gauge_workshop()
    st.markdown("## 브랜드는 언제 살까요?")
    st.caption("브랜드는 등급표가 아니라 특징 참고용입니다. 손에 맞는 단품을 먼저 시험하세요.")
    for brand in BRAND_GUIDES:
        with st.expander(f"{brand.name} · {brand.tier}"):
            st.write(brand.known_for)
            st.markdown(f"**추천 시점**　{brand.good_time_to_buy}")
            st.caption(f"확인할 점 · {brand.caution}")
            if brand.official_url:
                st.link_button("공식 제품 정보", brand.official_url)


def render(on_ask: Callable[[str], None] | None = None) -> None:
    st.markdown(
        """
        <style>
        [class*="st-key-tool_grid_card_"] [data-testid="stImage"] img {
          height: 190px; object-fit: contain; background: #F6F4EE;
        }
        .st-key-tool_detail_illustration [data-testid="stImage"] img {
          max-height: 430px; object-fit: contain; background: #F6F4EE;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    selected = st.session_state.get("selected_tool")
    if selected:
        _render_detail(selected, on_ask)
    else:
        _render_grid()
