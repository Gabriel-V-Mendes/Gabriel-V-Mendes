#!/usr/bin/env python3
"""Renderiza data/contributions.json como contrib-heatmap.svg animado (53 semanas x 7 dias)."""

import json
from datetime import datetime
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
SVG_WIDTH = 860
SVG_HEIGHT = 200
CELL_SIZE = 12
CELL_GAP = 3
STEP = CELL_SIZE + CELL_GAP
GRID_X = 36
GRID_Y = 58
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def render_heatmap(data: dict, output_path: Path) -> None:
    days = data.get("days", [])
    if not days:
        raise ValueError("data/contributions.json não possui registros em 'days'.")

    first_dt = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    # Domingo = 0 .. Sábado = 6
    first_weekday = (first_dt.weekday() + 1) % 7

    cells_svg = []
    month_labels = []
    seen_months = set()
    last_label_x = -999

    for idx, day in enumerate(days):
        offset = first_weekday + idx
        week = offset // 7
        dow = offset % 7
        if week >= 53:
            continue

        x = GRID_X + week * STEP
        y = GRID_Y + dow * STEP
        level = min(max(int(day.get("level", 0)), 0), len(PALETTE) - 1)
        color = PALETTE[level]
        delay = round(0.05 + (week + dow) * 0.014, 3)

        cells_svg.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2.5" fill="{color}" style="animation-delay:{delay}s">'
            f'<title>{day["date"]}: {day["count"]} contributions</title>'
            f"</rect>"
        )

        ym = day["date"][:7]
        dom = int(day["date"][8:10])
        if dow == 0 and dom <= 7 and ym not in seen_months and week > 0:
            seen_months.add(ym)
            if x - last_label_x >= 30:
                m_idx = int(day["date"][5:7]) - 1
                month_labels.append(
                    f'<text x="{x}" y="{GRID_Y - 8}" fill="#8b949e" font-size="10">{MONTH_NAMES[m_idx]}</text>'
                )
                last_label_x = x

    total = data.get("total_contributions", 0)
    cur_streak = data.get("current_streak", 0)
    max_streak = data.get("longest_streak", 0)
    footer_text = (
        f"{total:,} contributions in the last year  ·  "
        f"current streak: {cur_streak}d  ·  longest streak: {max_streak}d"
    )

    legend_x = SVG_WIDTH - 165
    legend_y = SVG_HEIGHT - 22
    legend_rects = []
    for i, c in enumerate(PALETTE):
        legend_rects.append(
            f'<rect x="{legend_x + 36 + i * 15}" y="{legend_y - 9}" width="11" height="11" rx="2" fill="{c}"/>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">
  <style>
    @keyframes dropIn {{
      0% {{ opacity: 0; transform: translateY(-6px); }}
      100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .cell {{
      opacity: 0;
      animation: dropIn 0.28s ease-out forwards;
    }}
  </style>
  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <rect width="{SVG_WIDTH}" height="28" rx="10" fill="#161b22"/>
  <rect y="18" width="{SVG_WIDTH}" height="10" fill="#161b22"/>
  <line x1="0" y1="28" x2="{SVG_WIDTH}" y2="28" stroke="#30363d" stroke-width="1"/>
  <circle cx="16" cy="14" r="5" fill="#ff5f56"/>
  <circle cx="32" cy="14" r="5" fill="#ffbd2e"/>
  <circle cx="48" cy="14" r="5" fill="#27c93f"/>
  <text x="{SVG_WIDTH / 2:.0f}" y="18" text-anchor="middle" fill="#8b949e" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="11">{data.get("username", "Gabriel-V-Mendes")} — contributions (53 weeks)</text>
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">
    <text x="12" y="{GRID_Y + STEP * 1 + 9}" fill="#8b949e" font-size="9">Mon</text>
    <text x="12" y="{GRID_Y + STEP * 3 + 9}" fill="#8b949e" font-size="9">Wed</text>
    <text x="12" y="{GRID_Y + STEP * 5 + 9}" fill="#8b949e" font-size="9">Fri</text>
    {"".join(month_labels)}
    {"".join(cells_svg)}
    <text x="{GRID_X}" y="{legend_y}" fill="#8b949e" font-size="11">{footer_text}</text>
    <text x="{legend_x}" y="{legend_y}" fill="#8b949e" font-size="10">Less</text>
    {"".join(legend_rects)}
    <text x="{legend_x + 36 + len(PALETTE) * 15 + 4}" y="{legend_y}" fill="#8b949e" font-size="10">More</text>
  </g>
</svg>
"""
    output_path.write_text(svg, encoding="utf-8")
    print(f"Heatmap SVG salvo em: {output_path}")


if __name__ == "__main__":
    data_path = Path("data/contributions.json")
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    render_heatmap(payload, Path("contrib-heatmap.svg"))
