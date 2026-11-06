#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "assets" / "img" / "og-preview.png"
BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
INK = "#12171D"
PANEL = "#1A212A"
TEXT = "#E9ECEF"
MUTED = "#8794A3"
SIGNAL = "#FFB020"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size)


def main() -> int:
    image = Image.new("RGB", (1200, 630), INK)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1200, 12), fill=SIGNAL)
    draw.ellipse((72, 78, 130, 136), outline=MUTED, width=5)
    draw.pieslice((72, 78, 130, 136), 0, 180, fill=SIGNAL)
    draw.text((150, 86), "ZONA GRIS", font=font(BOLD, 30), fill=TEXT)
    draw.text((74, 190), "Atlas abierto de", font=font(BOLD, 70), fill=TEXT)
    draw.text((74, 270), "incidentes híbridos", font=font(BOLD, 70), fill=SIGNAL)
    draw.text((76, 382), "Cada hecho con su fuente y su atribución.", font=font(REGULAR, 31), fill=TEXT)
    draw.text((76, 430), "El sistema no atribuye por su cuenta.", font=font(REGULAR, 31), fill=TEXT)
    draw.line((76, 512, 1124, 512), fill="#2C3642", width=2)
    draw.text((76, 540), "v0.1 · AGPL-3.0 · sin cookies ni rastreadores", font=font(REGULAR, 22), fill=MUTED)
    draw.text((780, 540), "zonagris.viajeinteligencia.com", font=font(REGULAR, 20), fill=MUTED)
    image.save(OUT, optimize=True)
    print(f"og: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
