#!/usr/bin/env python3
"""Gera info-card.svg no estilo neofetch personalizado para Gabriel-V-Mendes."""

import html
import os
from pathlib import Path

SVG_WIDTH = 490
SVG_HEIGHT = 430
STATIC = os.getenv("STATIC", "0") == "1"

ROWS = [
    ("header", "gabriel@github", "Porto Alegre, RS"),
    ("sep", "──────────────", "─────────────────────────────"),
    ("kv", "Now", "IT Infrastructure Technician @ AppMax"),
    ("kv", "Focus", "Cloud · SRE · DevOps Infrastructure"),
    ("kv", "Study", "ADS @ UNISINOS · Oracle ONE"),
    ("kv", "Cloud", "AWS · OCI · OpenTofu · GitOps"),
    ("kv", "Infra", "Linux · Docker · Kubernetes · CI/CD"),
    ("kv", "Code", "Python · Bash · TypeScript · SQL"),
    ("kv", "Repos", "ContainerizacaoPipelineCICD · GitOps_K8s"),
    ("kv", "More", "aws-opentofu-floci · Observabilidade"),
    ("kv", "Impact", "CHAMA (Caldeira) · Instituto Percorre"),
    ("kv", "Web", "linkedin.com/in/gabrielvmendes-dev"),
]

PALETTE_BLOCKS = ["#0d1117", "#ff5f56", "#39d353", "#ffbd2e", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]


def build_info_card(output_path: Path) -> None:
    lines_svg = []
    start_y = 64
    step_y = 26

    for idx, (kind, key, val) in enumerate(ROWS):
        y = start_y + idx * step_y
        delay = round(0.10 + idx * 0.12, 2)
        if STATIC:
            anim_attr = 'opacity="1"'
        else:
            anim_attr = (
                f'opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.32s" fill="freeze" /'
            )

        if kind == "header":
            content = (
                f'<text x="24" y="{y}" font-size="14" font-weight="700">'
                f'<tspan fill="#39d353">{html.escape(key)}</tspan>'
                f'<tspan fill="#8b949e">  //  </tspan>'
                f'<tspan fill="#58a6ff">{html.escape(val)}</tspan>'
                f"</text>"
            )
        elif kind == "sep":
            content = (
                f'<text x="24" y="{y}" fill="#30363d" font-size="12">'
                f"{html.escape(key + val)}</text>"
            )
        else:
            content = (
                f'<text x="24" y="{y}" font-size="13">'
                f'<tspan fill="#39d353" font-weight="700">{html.escape(key):<8}</tspan>'
                f'<tspan fill="#8b949e">: </tspan>'
                f'<tspan fill="#e6edf3">{html.escape(val)}</tspan>'
                f"</text>"
            )

        if STATIC:
            lines_svg.append(f"<g>{content}</g>")
        else:
            lines_svg.append(
                f'<g opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.30s" fill="freeze" />'
                f"{content}</g>"
            )

    # Barra de cores neofetch no rodapé
    blocks_y = 382
    block_delay = round(0.10 + len(ROWS) * 0.12, 2)
    blocks = []
    for b_idx, color in enumerate(PALETTE_BLOCKS):
        bx = 24 + b_idx * 26
        blocks.append(f'<rect x="{bx}" y="{blocks_y}" width="22" height="14" rx="2" fill="{color}" stroke="#30363d" stroke-width="0.5"/>')

    if STATIC:
        palette_group = f'<g>{"".join(blocks)}</g>'
    else:
        palette_group = (
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{block_delay}s" dur="0.35s" fill="freeze" />'
            f'{"".join(blocks)}</g>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">
  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <rect width="{SVG_WIDTH}" height="28" rx="10" fill="#161b22"/>
  <rect y="18" width="{SVG_WIDTH}" height="10" fill="#161b22"/>
  <line x1="0" y1="28" x2="{SVG_WIDTH}" y2="28" stroke="#30363d" stroke-width="1"/>
  <circle cx="16" cy="14" r="5" fill="#ff5f56"/>
  <circle cx="32" cy="14" r="5" fill="#ffbd2e"/>
  <circle cx="48" cy="14" r="5" fill="#27c93f"/>
  <text x="{SVG_WIDTH / 2:.0f}" y="18" text-anchor="middle" fill="#8b949e" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="11">gabriel@github — neofetch</text>
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">
    {"".join(lines_svg)}
    {palette_group}
  </g>
</svg>
"""
    output_path.write_text(svg, encoding="utf-8")
    print(f"Cartão neofetch salvo em: {output_path}")


if __name__ == "__main__":
    build_info_card(Path("info-card.svg"))
