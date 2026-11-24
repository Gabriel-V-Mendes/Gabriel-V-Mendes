#!/usr/bin/env python3
"""Prepara uma foto para conversão em ASCII:
1. Remove o fundo com rembg
2. Compõe sobre fundo branco puro
3. Aumenta o contraste local com OpenCV CLAHE em tons de cinza
"""

import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: Path, output_path: Path) -> None:
    raw_bytes = input_path.read_bytes()
    cutout_bytes = remove(raw_bytes)
    rgba = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")

    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("L")

    gray = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(output_path)
    print(f"Foto preparada salva em: {output_path}")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source-photo.jpg")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("source-prepped.png")
    if not src.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {src}")
    prep_photo(src, dst)
