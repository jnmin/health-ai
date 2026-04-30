from __future__ import annotations

import io
import zipfile
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ZIP_PATH = Path("/tmp/dina-2.93.zip")
OUTPUT_DIR = REPO_ROOT / "code" / "frontend" / "src" / "assets" / "fonts"
OUTPUT_FONT = OUTPUT_DIR / "Dina-Regular.ttf"
OUTPUT_LICENSE = OUTPUT_DIR / "Dina-LICENSE.txt"
BDF_MEMBER = "BDF/Dina_r400-10.bdf"

PIXEL_WIDTH = 100
PIXEL_HEIGHT = 100
UNITS_PER_EM = 1600
ASCENT = 1200
DESCENT = 400
LINE_GAP = 200


def parse_bdf_member(zip_path: Path, member_name: str) -> tuple[dict[int, list[str]], int]:
    with zipfile.ZipFile(zip_path) as zf:
        lines = zf.read(member_name).decode("latin-1").splitlines()

    glyphs: dict[int, list[str]] = {}
    default_char = 32
    encoding = None
    bitmap_rows: list[str] | None = None
    in_bitmap = False

    for line in lines:
        if line.startswith("DEFAULT_CHAR "):
            default_char = int(line.split()[1])
        elif line.startswith("ENCODING "):
            encoding = int(line.split()[1])
        elif line == "BITMAP":
            bitmap_rows = []
            in_bitmap = True
        elif line == "ENDCHAR":
            if encoding is not None and bitmap_rows is not None:
                glyphs[encoding] = bitmap_rows
            encoding = None
            bitmap_rows = None
            in_bitmap = False
        elif in_bitmap and bitmap_rows is not None:
            bitmap_rows.append(line.strip())

    return glyphs, default_char


def codepoint_to_char(codepoint: int) -> str:
    if codepoint == 0:
        return "\u0000"

    if codepoint <= 255:
        try:
            return bytes([codepoint]).decode("cp1252")
        except UnicodeDecodeError:
            return bytes([codepoint]).decode("latin-1")

    return chr(codepoint)


def build_glyph(bitmap_rows: list[str]) -> object:
    pen = TTGlyphPen(None)

    for row_index, row_hex in enumerate(bitmap_rows):
        bits = bin(int(row_hex, 16))[2:].zfill(len(row_hex) * 4)
        for column_index, bit in enumerate(bits[:8]):
            if bit != "1":
                continue

            x0 = column_index * PIXEL_WIDTH
            x1 = x0 + PIXEL_WIDTH
            y1 = ASCENT - (row_index * PIXEL_HEIGHT)
            y0 = y1 - PIXEL_HEIGHT

            pen.moveTo((x0, y0))
            pen.lineTo((x1, y0))
            pen.lineTo((x1, y1))
            pen.lineTo((x0, y1))
            pen.closePath()

    return pen.glyph()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    glyph_bitmaps, default_char = parse_bdf_member(ZIP_PATH, BDF_MEMBER)

    glyph_order = [".notdef"]
    cmap: dict[int, str] = {}
    glyf = {".notdef": TTGlyphPen(None).glyph()}
    horizontal_metrics = {".notdef": (PIXEL_WIDTH * 8, 0)}

    for codepoint in sorted(glyph_bitmaps):
        glyph_name = f"uni{codepoint:04X}"
        glyph_order.append(glyph_name)
        glyph = build_glyph(glyph_bitmaps[codepoint])
        glyf[glyph_name] = glyph
        horizontal_metrics[glyph_name] = (PIXEL_WIDTH * 8, 0)

        try:
            character = codepoint_to_char(codepoint)
        except ValueError:
            continue

        if character:
            cmap[ord(character)] = glyph_name

    notdef_name = f"uni{default_char:04X}"
    if default_char in glyph_bitmaps:
        glyf[".notdef"] = build_glyph(glyph_bitmaps[default_char])

    fb = FontBuilder(UNITS_PER_EM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(horizontal_metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=-DESCENT, lineGap=LINE_GAP)
    fb.setupOS2(
        sTypoAscender=ASCENT,
        sTypoDescender=-DESCENT,
        sTypoLineGap=LINE_GAP,
        usWinAscent=ASCENT,
        usWinDescent=DESCENT,
        sxHeight=900,
        sCapHeight=900,
    )
    fb.setupNameTable(
        {
            "familyName": "Dina",
            "styleName": "Regular",
            "uniqueFontIdentifier": "Dina Regular Web Converted",
            "fullName": "Dina Regular",
            "psName": "Dina-Regular",
            "version": "Version 2.93 web build",
        }
    )
    fb.setupPost()
    fb.setupMaxp()
    fb.save(OUTPUT_FONT)

    with zipfile.ZipFile(ZIP_PATH) as zf:
        license_text = zf.read("LICENSE").decode("utf-8")
        readme_text = zf.read("README.md").decode("utf-8")

    OUTPUT_LICENSE.write_text(
        f"{license_text}\n\nOriginal package readme excerpt:\n\n{readme_text}",
        encoding="utf-8",
    )

    print(f"Wrote {OUTPUT_FONT}")
    print(f"Wrote {OUTPUT_LICENSE}")


if __name__ == "__main__":
    main()
