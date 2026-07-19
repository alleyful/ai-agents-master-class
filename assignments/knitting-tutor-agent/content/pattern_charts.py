"""Deterministic SVG renderers for approved beginner-project charts."""

from __future__ import annotations

import math
from html import escape

from domain.project_patterns import RadialCrochetChart


def _polar(radius: float, angle: float, center: float = 300) -> tuple[float, float]:
    radians = math.radians(angle - 90)
    return center + radius * math.cos(radians), center + radius * math.sin(radians)


def _x_symbol(x: float, y: float, size: float, css_class: str) -> str:
    return (
        f'<g class="{css_class}" transform="translate({x:.2f} {y:.2f})">'
        f'<path d="M {-size:.2f} {-size:.2f} L {size:.2f} {size:.2f} '
        f'M {size:.2f} {-size:.2f} L {-size:.2f} {size:.2f}"/></g>'
    )


def radial_crochet_chart_svg(chart: RadialCrochetChart, active_round: int) -> str:
    """Render a complete spiral chart, highlighting stitches of one round."""
    active_round = max(1, min(active_round, len(chart.rounds)))
    center = 300
    first_radius = 58
    radius_gap = 31
    guides: list[str] = []
    symbols: list[str] = []
    branches: list[str] = []
    round_labels: list[str] = []

    def round_class(number: int) -> str:
        if number == active_round:
            return "chart-current"
        if number < active_round:
            return "chart-complete"
        return "chart-future"

    for round_spec in chart.rounds:
        number = round_spec.number
        radius = first_radius + (number - 1) * radius_gap
        css_class = round_class(number)
        guides.append(
            f'<circle class="chart-guide {css_class}" cx="{center}" cy="{center}" r="{radius}"/>'
        )

        stitches_per_sector = number
        sector_spread = 42.0
        positions: list[tuple[float, float, float]] = []
        for sector in range(6):
            sector_center = sector * 60.0
            if stitches_per_sector == 1:
                angles = [sector_center]
            else:
                spacing = sector_spread / (stitches_per_sector - 1)
                angles = [
                    sector_center - sector_spread / 2 + within * spacing
                    for within in range(stitches_per_sector)
                ]
            for angle in angles:
                x, y = _polar(radius, angle, center)
                positions.append((x, y, angle))
                symbols.append(_x_symbol(x, y, 6.2 if number < 6 else 5.5, css_class))

            if number > 1:
                previous_radius = first_radius + (number - 2) * radius_gap
                base_angle = sector_center - sector_spread / 2
                base_x, base_y = _polar(previous_radius + 9, base_angle, center)
                child_angles = angles[:2]
                child_points = [_polar(radius - 10, angle, center) for angle in child_angles]
                branches.append(
                    f'<path class="chart-branch {css_class}" d="M {base_x:.2f} {base_y:.2f} '
                    f'L {child_points[0][0]:.2f} {child_points[0][1]:.2f} '
                    f'M {base_x:.2f} {base_y:.2f} '
                    f'L {child_points[1][0]:.2f} {child_points[1][1]:.2f}"/>'
                )

        label_x, label_y = _polar(radius, 90, center)
        round_labels.append(
            f'<g class="chart-round-label {css_class}"><circle cx="{label_x + 14:.2f}" '
            f'cy="{label_y:.2f}" r="8"/><text x="{label_x + 14:.2f}" '
            f'y="{label_y + 3.2:.2f}" text-anchor="middle">{number}</text></g>'
        )

    active_radius = first_radius + (active_round - 1) * radius_gap
    marker_x, marker_y = _polar(active_radius, 0, center)
    active = chart.rounds[active_round - 1]
    accessible = escape(
        f"{active_round}단, {active.stitch_count}코. {active.instruction}"
    )
    return f"""
<div class="project-chart" role="img" aria-label="{accessible}">
  <svg viewBox="0 0 600 600" aria-hidden="true">
    <g>{''.join(guides)}</g>
    <g>{''.join(branches)}</g>
    <g>{''.join(symbols)}</g>
    <g class="chart-center">
      <circle cx="300" cy="300" r="29"/>
      <path d="M285 300c0-12 21-16 28-4 7 12-6 24-18 19-11-5-12-20-2-27"/>
      <text x="300" y="304" text-anchor="middle">MR</text>
    </g>
    <g>{''.join(round_labels)}</g>
    <g class="chart-marker"><circle cx="{marker_x:.2f}" cy="{marker_y:.2f}" r="5"/>
      <path d="M205 43 A255 255 0 0 0 105 98"/><path d="M106 87l-2 13 13-4"/>
    </g>
  </svg>
</div>
"""


def mini_hat_chart_svg(chart: RadialCrochetChart, active_rounds: list[int]) -> str:
    """Render the approved mini-hat pattern as one complete symbol chart.

    The crown, vertical side and brim are still worked in continuous rounds. The
    concentric layout preserves every stitch count; the BLO bend is explicitly
    marked because BLO has no single universal chart glyph.
    """
    center = 350
    first_radius = 48
    radius_gap = 25
    symbols: list[str] = []
    guides: list[str] = []
    labels: list[str] = []
    branches: list[str] = []
    active = set(active_rounds)

    for round_spec in chart.rounds:
        number = round_spec.number
        radius = first_radius + (number - 1) * radius_gap
        css_class = "chart-current" if number in active else "chart-future"
        guides.append(f'<circle class="chart-guide {css_class}" cx="{center}" cy="{center}" r="{radius}"/>')
        for index in range(round_spec.stitch_count):
            angle = index * 360 / round_spec.stitch_count
            x, y = _polar(radius, angle, center)
            symbols.append(_x_symbol(x, y, 5.3 if number < 9 else 4.7, css_class))

        previous_count = chart.rounds[number - 2].stitch_count if number > 1 else 0
        increase_count = max(0, round_spec.stitch_count - previous_count)
        if increase_count:
            previous_radius = radius - radius_gap
            for increase in range(increase_count):
                angle = increase * 360 / increase_count
                base_x, base_y = _polar(previous_radius + 7, angle, center)
                left_x, left_y = _polar(radius - 7, angle - 4.2, center)
                right_x, right_y = _polar(radius - 7, angle + 4.2, center)
                branches.append(
                    f'<path class="chart-branch {css_class}" d="M {base_x:.2f} {base_y:.2f} '
                    f'L {left_x:.2f} {left_y:.2f} M {base_x:.2f} {base_y:.2f} L {right_x:.2f} {right_y:.2f}"/>'
                )
        label_x, label_y = _polar(radius, 90, center)
        note = " · BLO" if number == 5 else ""
        labels.append(
            f'<text class="{css_class}" x="{label_x + 10:.2f}" y="{label_y + 3:.2f}">{number}단 · {round_spec.stitch_count}코{note}</text>'
        )

    accessible = escape(
        "미니 모자 키링 전체 기호 도안. 1단부터 11단까지 6, 12, 18, 24, 24, 24, 24, 24, 30, 36, 36코"
    )
    return f"""
<div class="project-chart mini-hat-chart" role="img" aria-label="{accessible}">
  <svg viewBox="0 0 760 700" aria-hidden="true">
    <g>{''.join(guides)}</g>
    <g>{''.join(branches)}</g>
    <g>{''.join(symbols)}</g>
    <g class="chart-center"><circle cx="350" cy="350" r="25"/><text x="350" y="354" text-anchor="middle">MR</text></g>
    <g class="chart-round-labels">{''.join(labels)}</g>
    <path class="chart-section-line" d="M350 224 A126 126 0 0 1 476 350"/>
    <text class="chart-section-note" x="470" y="215">5단 BLO · 옆면 꺾기</text>
  </svg>
</div>
"""
