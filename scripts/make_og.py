#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "web" / "assets" / "img"
BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
INK = "#12171D"
PANEL = "#1A212A"
TEXT = "#E9ECEF"
MUTED = "#8794A3"
SIGNAL = "#FFB020"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size)


def logo(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 0, 1200, 12), fill=SIGNAL)
    draw.ellipse((72, 78, 130, 136), outline=MUTED, width=5)
    draw.pieslice((72, 78, 130, 136), 0, 180, fill=SIGNAL)
    draw.text((150, 86), "ATLAS ZONA GRIS", font=font(BOLD, 28), fill=TEXT)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.line((76, 512, 1124, 512), fill="#2C3642", width=2)
    draw.text((76, 540), "v0.1 · AGPL-3.0 · sin cookies ni rastreadores", font=font(REGULAR, 22), fill=MUTED)
    draw.text((780, 540), "zonagris.pruebapublica.com", font=font(REGULAR, 20), fill=MUTED)


def build_atlas() -> None:
    image = Image.new("RGB", (1200, 630), INK)
    draw = ImageDraw.Draw(image)
    logo(draw)
    draw.text((74, 190), "Atlas Zona Gris", font=font(BOLD, 66), fill=TEXT)
    draw.text((74, 286), "Observación documental de", font=font(BOLD, 44), fill=TEXT)
    draw.text((74, 340), "riesgos e infraestructuras", font=font(BOLD, 44), fill=SIGNAL)
    draw.text((76, 424), "Documentos, fuentes y fecha. Sin atribuciones inventadas.", font=font(REGULAR, 28), fill=TEXT)
    footer(draw)
    out = IMG / "og-atlas.png"
    image.save(out, optimize=True)
    print(f"og: {out}")


def build_registros() -> None:
    image = Image.new("RGB", (1200, 630), INK)
    draw = ImageDraw.Draw(image)
    logo(draw)
    draw.text((74, 170), "REGISTROS DOCUMENTALES", font=font(BOLD, 24), fill=SIGNAL)
    draw.text((74, 216), "Ocho documentos", font=font(BOLD, 62), fill=TEXT)
    draw.text((74, 286), "institucionales", font=font(BOLD, 62), fill=TEXT)
    draw.text((76, 378), "Metadatos, fuente original y condiciones de reutilización.", font=font(REGULAR, 28), fill=TEXT)
    draw.text((76, 424), "212 revisados · 8 incorporados · 204 descartados", font=font(REGULAR, 26), fill=MUTED)
    footer(draw)
    out = IMG / "og-registros.png"
    image.save(out, optimize=True)
    print(f"og: {out}")


def build_caso_moscu() -> None:
    image = Image.new("RGB", (1200, 630), INK)
    draw = ImageDraw.Draw(image)
    logo(draw)
    draw.text((74, 168), "CASO · AEROPUERTOS · N1", font=font(BOLD, 24), fill=SIGNAL)
    draw.text((74, 218), "Cuatro episodios,", font=font(BOLD, 62), fill=TEXT)
    draw.text((74, 288), "no una campaña.", font=font(BOLD, 62), fill=SIGNAL)
    draw.text((76, 386), "Moscú · 2025–2026 · recurrencia documentada", font=font(BOLD, 30), fill=TEXT)
    draw.text((76, 430), "Sin atribución y sin conclusión de campaña.", font=font(REGULAR, 28), fill=MUTED)
    footer(draw)
    out = IMG / "og-caso-moscu.png"
    image.save(out, optimize=True)
    print(f"og: {out}")


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    build_atlas()
    build_registros()
    build_caso_moscu()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
