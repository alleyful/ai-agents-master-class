"""Project workbench for pre-authored beginner curricula."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Callable

import streamlit as st

from content.pattern_charts import mini_hat_chart_svg, radial_crochet_chart_svg
from domain.curricula import CURRICULA
from domain.project_patterns import (
    RADIAL_CROCHET_CHARTS,
    MINI_HAT_CHART,
    phase_index_for_step,
    phase_progress,
    phases_for_project,
)


CompleteCallback = Callable[[str, int], None]
OpenLibraryCallback = Callable[[str], None]
FocusStepCallback = Callable[[str, int], None]


def _phase_tracker(project_id: str, step_id: str) -> str:
    phases = phases_for_project(project_id)
    active_index = phase_index_for_step(project_id, step_id)
    items: list[str] = []
    for index, phase in enumerate(phases):
        state = "complete" if index < active_index else "current" if index == active_index else "future"
        marker = "✓" if state == "complete" else str(index + 1)
        current, total = phase_progress(project_id, step_id) if state == "current" else (0, len(phase.step_ids))
        progress = ""
        if state == "current" and total > 1:
            progress = (
                f'<span class="phase-sub">현재 {current}/{total}</span>'
                f'<span class="phase-bar"><i style="width:{current / total * 100:.1f}%"></i></span>'
            )
        else:
            progress = f'<span class="phase-sub">{escape(phase.description)}</span>'
        items.append(
            f'<div class="project-phase {state}"><span class="phase-marker">{marker}</span>'
            f'<span class="phase-copy"><strong>{escape(phase.title)}</strong>{progress}</span></div>'
        )
    return f'<div class="project-phase-track">{"".join(items)}</div>'


def _step_round(step_id: str) -> int | None:
    if not step_id.startswith("round-"):
        return None
    suffix = step_id.removeprefix("round-")
    return int(suffix) if suffix.isdigit() else None


def _select_round(key: str, round_number: int) -> None:
    st.session_state[key] = round_number


def _render_techniques(techniques: list[str], open_library: OpenLibraryCallback, key_scope: str) -> None:
    labels = [item.split("(")[0].strip() for item in techniques]
    st.caption("이번 단계에서 필요한 기법 · 누르면 손동작 설명을 바로 볼 수 있어요.")
    with st.container(horizontal=True, gap="small", key=f"workbench_techniques_{key_scope}"):
        for index, label in enumerate(labels):
            st.button(
                f"⌘ {label} 설명 보기 →",
                on_click=open_library,
                args=(techniques[index],),
                key=f"open_technique_{key_scope}_{index}",
            )


def _render_project_overview(
    card_id: str,
    curriculum_id: str,
    current_index: int,
    focus_step: FocusStepCallback,
    open_library: OpenLibraryCallback,
) -> None:
    """Show the complete authored route once, before focused step coaching."""
    curriculum = CURRICULA[curriculum_id]
    step = curriculum.steps[current_index]
    st.markdown(_phase_tracker(curriculum_id, step.id), unsafe_allow_html=True)
    st.markdown('<span class="workbench-kicker">작품 전체 안내</span>', unsafe_allow_html=True)
    st.markdown("### 먼저 완성까지의 길을 한 번 볼게요")
    st.caption("이 전체 안내는 시작할 때 한 번 확인합니다. 다음부터는 현재 단계의 동작과 완료 기준만 크게 보여드려요.")

    if curriculum_id in RADIAL_CROCHET_CHARTS:
        chart = RADIAL_CROCHET_CHARTS[curriculum_id]
        chart_column, pattern_column = st.columns([1.2, 1], gap="large")
        with chart_column:
            st.markdown(radial_crochet_chart_svg(chart, 1), unsafe_allow_html=True)
        with pattern_column:
            st.markdown("#### 전체 글 도안")
            for round_spec in chart.rounds:
                st.markdown(
                    f'<div class="written-round"><b>{round_spec.number}단</b>'
                    f'<span>{escape(round_spec.instruction)}</span><em>[{round_spec.stitch_count}]</em></div>',
                    unsafe_allow_html=True,
                )
            st.markdown('<div class="written-round"><b>마무리</b><span>빼뜨기하고 실 끝을 뒤쪽 코 사이에 숨깁니다.</span><em></em></div>', unsafe_allow_html=True)
    elif curriculum_id == MINI_HAT_CHART.project_id:
        chart_column, pattern_column = st.columns([1.2, 1], gap="large")
        with chart_column:
            st.markdown(mini_hat_chart_svg(MINI_HAT_CHART, []), unsafe_allow_html=True)
        with pattern_column:
            st.markdown("#### 전체 글·기호 도안")
            for index, line in enumerate(curriculum.written_pattern):
                st.markdown(
                    f'<div class="written-round"><b>{index + 1:02d}</b><span>{escape(line)}</span><em></em></div>',
                    unsafe_allow_html=True,
                )
    else:
        st.markdown("#### 전체 기본 도안")
        st.caption(f"{curriculum.pattern_format} · {curriculum.construction}")
        for index, line in enumerate(curriculum.written_pattern):
            st.markdown(
                f'<div class="written-round"><b>{index + 1:02d}</b><span>{escape(line)}</span><em></em></div>',
                unsafe_allow_html=True,
            )

    with st.expander("이 작품에서 배우는 기법"):
        techniques: list[str] = []
        for name in curriculum.pattern_techniques or [item.technique for item in curriculum.steps]:
            if name not in techniques:
                techniques.append(name)
        _render_techniques(techniques, open_library, f"{card_id}_overview")

    st.button(
        f"{step.title} 자세히 시작하기 →",
        key=f"focus_step_{card_id}",
        on_click=focus_step,
        args=(curriculum_id, current_index),
        type="primary",
        use_container_width=True,
    )


def _render_radial_project(
    card_id: str,
    curriculum_id: str,
    current_index: int,
    complete_step: CompleteCallback,
    open_library: OpenLibraryCallback,
    is_preview: bool,
) -> None:
    curriculum = CURRICULA[curriculum_id]
    step = curriculum.steps[current_index]
    chart = RADIAL_CROCHET_CHARTS[curriculum_id]
    current_round = _step_round(step.id)
    selected_round = current_round or len(chart.rounds)
    selected = chart.rounds[selected_round - 1]

    st.markdown(_phase_tracker(curriculum_id, step.id), unsafe_allow_html=True)
    instruction_column, chart_column = st.columns([0.78, 1.42], gap="large")

    with instruction_column:
        st.markdown('<span class="workbench-kicker">지금 뜰 차례</span>', unsafe_allow_html=True)
        if current_round is None:
            st.markdown(f"### {step.title}")
            st.write(step.why)
            st.write(step.practice)
            st.info(step.success_check)
        else:
            st.markdown(f"### {selected_round}단 · {selected.stitch_count}코")
            st.write(step.why)
            st.write(selected.instruction)
            st.markdown(
                f'<div class="round-summary"><strong>한 줄 도안</strong><span>{escape(selected.notation)} '
                f'→ {selected.stitch_count}코</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div class="round-summary"><strong>완료 확인</strong><span>{escape(step.success_check)}</span></div>',
            unsafe_allow_html=True,
        )
        label = "다음 단계 미리보기 →" if is_preview else f"{step.title} 완료하고 다음으로 →"
        st.button(
            label,
            key=f"complete_workbench_{card_id}",
            on_click=complete_step,
            args=(curriculum_id, current_index),
            type="primary",
            use_container_width=True,
        )

    with chart_column:
        st.markdown(
            '<div class="chart-heading"><strong>원형 티코스터 전체 도안</strong>'
            '<span>나선뜨기 · 현재 단의 기호만 강조</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(radial_crochet_chart_svg(chart, selected_round), unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-legend"><span><b>MR</b> 매직링</span><span><b>×</b> 짧은뜨기</span>'
            '<span><b>××</b> 같은 코에 두 번 · 늘리기</span><span><b>●</b> 현재 단 시작점</span></div>',
            unsafe_allow_html=True,
        )

    written_tab, technique_tab = st.tabs(["현재 단계 글 도안", "필요한 기법"])
    with written_tab:
        if current_round is None:
            st.markdown(f'<div class="written-round current"><b>마무리</b><span>{escape(step.practice)}</span><em></em></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="written-round current"><b>{selected.number}단</b>'
                f'<span>{escape(selected.instruction)}</span><em>[{selected.stitch_count}]</em></div>',
                unsafe_allow_html=True,
            )
    with technique_tab:
        techniques = selected.techniques if current_round is not None else [step.technique]
        _render_techniques(techniques, open_library, f"{card_id}_{selected_round}")


def _render_pre_authored_project(
    card_id: str,
    curriculum_id: str,
    current_index: int,
    complete_step: CompleteCallback,
    open_library: OpenLibraryCallback,
    is_preview: bool,
) -> None:
    curriculum = CURRICULA[curriculum_id]
    step = curriculum.steps[current_index]
    st.markdown(_phase_tracker(curriculum_id, step.id), unsafe_allow_html=True)
    with st.container(border=True, key=f"focused_step_{card_id}"):
        st.markdown('<span class="workbench-kicker">지금 진행할 작업</span>', unsafe_allow_html=True)
        st.markdown(f"### {step.title}")
        st.write(step.why)
        st.write(step.practice)
        st.markdown(
            f'<div class="round-summary"><strong>완료 확인</strong><span>{escape(step.success_check)}</span></div>',
            unsafe_allow_html=True,
        )
        st.button(
            "다음 단계 미리보기 →" if is_preview else f"{step.title} 완료하고 다음으로 →",
            key=f"complete_workbench_{card_id}",
            on_click=complete_step,
            args=(curriculum_id, current_index),
            type="primary",
            use_container_width=True,
        )
    with st.expander("이 단계에 필요한 기법", expanded=False):
        _render_techniques([step.technique], open_library, f"{card_id}_{current_index}")


def _render_mini_hat_project(
    card_id: str,
    curriculum_id: str,
    current_index: int,
    complete_step: CompleteCallback,
    open_library: OpenLibraryCallback,
    is_preview: bool,
) -> None:
    """Mini-hat workbench with a complete, count-checked symbol chart."""
    curriculum = CURRICULA[curriculum_id]
    step = curriculum.steps[current_index]
    active_by_step = {
        "top-1-2": [1, 2],
        "top-3-4": [3, 4],
        "side-5-8": [5, 6, 7, 8],
        "brim-9-10": [9, 10],
        "finish-11": [11],
    }
    active_rounds = active_by_step.get(step.id, [])
    st.markdown(_phase_tracker(curriculum_id, step.id), unsafe_allow_html=True)
    instruction_column, chart_column = st.columns([0.8, 1.4], gap="large")

    with instruction_column:
        st.markdown('<span class="workbench-kicker">지금 진행할 작업</span>', unsafe_allow_html=True)
        st.markdown(f"### {step.title}")
        st.write(step.practice)
        st.markdown(
            f'<div class="round-summary"><strong>완료 확인</strong><span>{escape(step.success_check)}</span></div>',
            unsafe_allow_html=True,
        )
        st.button(
            "다음 단계 미리보기 →" if is_preview else f"{step.title} 완료하고 다음으로 →",
            key=f"complete_workbench_{card_id}",
            on_click=complete_step,
            args=(curriculum_id, current_index),
            type="primary",
            use_container_width=True,
        )

    with chart_column:
        st.markdown(
            '<div class="chart-heading"><strong>미니 모자 키링 전체 기호 도안</strong>'
            '<span>꼭대기 → 옆면 → 챙 · 현재 단계 강조</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(mini_hat_chart_svg(MINI_HAT_CHART, active_rounds), unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-legend"><span><b>MR</b> 매직링</span><span><b>×</b> 짧은뜨기</span>'
            '<span><b>V</b> 같은 코에 짧은뜨기 2코</span><span><b>BLO</b> 뒤 고리에만 뜨기</span></div>',
            unsafe_allow_html=True,
        )

    written_tab, technique_tab = st.tabs(["현재 단계 글·기호 도안", "필요한 기법"])
    with written_tab:
        active_text = step.project_use
        for index, line in enumerate(curriculum.written_pattern):
            if active_text and active_text not in line:
                continue
            st.markdown(
                f'<div class="written-round current"><b>{index + 1:02d}</b><span>{escape(line)}</span><em></em></div>',
                unsafe_allow_html=True,
            )
    with technique_tab:
        techniques: list[str] = []
        for round_number in active_rounds:
            for technique in MINI_HAT_CHART.rounds[round_number - 1].techniques:
                if technique not in techniques:
                    techniques.append(technique)
        _render_techniques(techniques or [step.technique], open_library, f"{card_id}_{current_index}")


def render_project_workbench(
    card: dict,
    *,
    complete_step: CompleteCallback,
    focus_step: FocusStepCallback,
    open_library: OpenLibraryCallback,
    base_dir: Path,
) -> None:
    """Render the current, non-stale learning card for a curated project."""
    del base_dir  # Reserved for project-specific image/video panels.
    program = card["payload"].get("learning_program", {})
    curriculum_id = program.get("curriculum_id", "")
    current_index = int(program.get("current_step", 0))
    if curriculum_id not in CURRICULA or current_index >= len(CURRICULA[curriculum_id].steps):
        return

    curriculum = CURRICULA[curriculum_id]
    is_preview = program.get("status") == "preview"
    view_mode = card["payload"].get("view_mode", "step")
    st.markdown(
        f'<div class="project-workbench-title"><span>{escape(curriculum.badge)}</span>'
        f'<h2>{escape(curriculum.title)}</h2><p>{escape(curriculum.outcome)}</p>'
        '<small>작업대 · 현재 단계, 전체 도안, 기법 확인과 진도 저장을 한곳에서 진행합니다.</small></div>',
        unsafe_allow_html=True,
    )
    if view_mode == "overview":
        _render_project_overview(card["id"], curriculum_id, current_index, focus_step, open_library)
        return
    if curriculum_id == MINI_HAT_CHART.project_id:
        _render_mini_hat_project(card["id"], curriculum_id, current_index, complete_step, open_library, is_preview)
    elif curriculum_id in RADIAL_CROCHET_CHARTS:
        _render_radial_project(card["id"], curriculum_id, current_index, complete_step, open_library, is_preview)
    else:
        _render_pre_authored_project(card["id"], curriculum_id, current_index, complete_step, open_library, is_preview)
