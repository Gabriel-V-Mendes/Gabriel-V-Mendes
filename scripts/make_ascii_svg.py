#!/usr/bin/env python3
"""Converte source-prepped.png em um SVG monocromático autotipável (SMIL)."""

import html
import sys
from pathlib import Path

from PIL import Image

RAMP = " .`:-=+*cs#%@"  # claro (esparso) -> escuro (denso)
COLS = 92
ROWS = 48
SVG_WIDTH = 370
SVG_HEIGHT = 430
FONT_SIZE = 7.2
LINE_HEIGHT = 8.0
PAD_X = 14
PAD_TOP = 42


def image_to_ascii_lines(image_path: Path, cols: int = COLS, rows: int = ROWS) -> list[str]:
    img = Image.open(image_path).convert("L")
    img = img.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = list(img.getdata())

    lines: list[str] = []
    scale = len(RAMP) - 1
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            val = pixels[r * cols + c]
            # Branco (255) -> índice 0 (' '), Preto (0) -> último índice ('@')
            idx = int((255 - val) / 255 * scale)
            row_chars.append(RAMP[idx])
        lines.append("".join(row_chars))
    return lines


def build_ascii_svg(lines: list[str], output_path: Path) -> None:
    char_w = FONT_SIZE * 0.602
    text_w = COLS * char_w

    clips = []
    rows_svg = []
    for i, line in enumerate(lines):
        y = PAD_TOP + i * LINE_HEIGHT
        delay = round(0.08 + i * 0.045, 3)
        dur = 0.28
        clip_id = f"clip-row-{i}"
        clips.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="{PAD_X}" y="{y - LINE_HEIGHT + 1:.1f}" width="0" height="{LINE_HEIGHT + 1:.1f}">'
            f'<animate attributeName="width" from="0" to="{text_w:.1f}" '
            f'begin="{delay}s" dur="{dur}s" fill="freeze" />'
            f"</rect></clipPath>"
        )

        escaped = html.escape(line)
        rows_svg.append(
            f'<text x="{PAD_X}" y="{y:.1f}" clip-path="url(#{clip_id})" '
            f'xml:space="preserve">{escaped}</text>'
        )
        # Cursor de bloco acompanhando a borda da digitação
        rows_svg.append(
            f'<rect x="{PAD_X}" y="{y - FONT_SIZE + 1:.1f}" width="5" height="{FONT_SIZE:.1f}" '
            f'fill="#39d353" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.05;0.95;1" '
            f'begin="{delay}s" dur="{dur}s" fill="freeze" />'
            f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + text_w:.1f}" '
            f'begin="{delay}s" dur="{dur}s" fill="freeze" />'
            f"</rect>"
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">
  <defs>
    {"".join(clips)}
  </defs>
  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <rect width="{SVG_WIDTH}" height="28" rx="10" fill="#161b22"/>
  <rect y="18" width="{SVG_WIDTH}" height="10" fill="#161b22"/>
  <line x1="0" y1="28" x2="{SVG_WIDTH}" y2="28" stroke="#30363d" stroke-width="1"/>
  <circle cx="16" cy="14" r="5" fill="#ff5f56"/>
  <circle cx="32" cy="14" r="5" fill="#ffbd2e"/>
  <circle cx="48" cy="14" r="5" fill="#27c93f"/>
  <text x="{SVG_WIDTH / 2:.0f}" y="18" text-anchor="middle" fill="#8b949e" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="11">portrait.sh — ascii</text>
  <g fill="#c9d1d9" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="{FONT_SIZE}" letter-spacing="0">
    {"".join(rows_svg)}
  </g>
</svg>
"""
    output_path.write_text(svg, encoding="utf-8")
    print(f"SVG ASCII gerado em: {output_path}")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source-prepped.png")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("gabriel-ascii.svg")
    if not src.exists():
        raise FileNotFoundError(f"Execute scripts/prep_photo.py primeiro. Não encontrado: {src}")
    lines = image_to_ascii_lines(src)
    build_ascii_svg(lines, dst)
