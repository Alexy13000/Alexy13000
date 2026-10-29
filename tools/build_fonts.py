"""One-off: subset Mona Sans (OFL) into base64 WOFF2 CSS for the SVGs.

Not used by CI. Run it locally only when the character set changes:

    python3 -m venv .venv && .venv/bin/pip install fonttools brotli
    .venv/bin/python tools/build_fonts.py <folder with the source fonts>

Source (official repository):
  Mona Sans Regular / SemiBold / Bold   https://github.com/github/mona-sans

Subsetting modifies the font and "Mona" is a reserved font name under the
OFL, so the subset is renamed "HD Sans".
"""

import base64
import io
import json
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

OUT = Path(__file__).resolve().parent.parent / "assets" / "fonts"

LATIN = "".join(chr(c) for c in range(0x20, 0x7F))
FRENCH = "àâäçéèêëîïôöùûüÿœæÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ«»"
PUNCT = "  ’‘“”–—…·•→←↑↓×°%€▲▼✓"

FACES = [
    # (source file, family, weight, css file)
    ("MonaSans-Regular.otf", "HD Sans", 400, "sans-400.css"),
    ("MonaSans-SemiBold.otf", "HD Sans", 600, "sans-600.css"),
    ("MonaSans-Bold.otf", "HD Sans", 700, "sans-700.css"),
]


def build(src: Path, family: str, weight: int) -> bytes:
    font = TTFont(src)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "liga", "tnum", "lnum"]
    options.name_IDs = []
    options.notdef_outline = True
    options.hinting = False
    sub = subset.Subsetter(options)
    sub.populate(text=LATIN + FRENCH + PUNCT)
    sub.subset(font)
    style = {400: "Regular", 600: "SemiBold", 700: "Bold"}[weight]
    names = font["name"]
    for rec_id, value in ((1, family), (2, "Regular"), (4, f"{family} {style}"),
                          (6, f"{family.replace(' ', '')}-{style}"), (16, family), (17, style)):
        names.setName(value, rec_id, 3, 1, 0x409)
    buffer = io.BytesIO()
    font.flavor = "woff2"
    font.save(buffer)
    return buffer.getvalue()


def metrics(src: Path) -> dict:
    """Advance width of every subset character, in em."""
    font = TTFont(src)
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    upm = font["head"].unitsPerEm
    return {ch: round(hmtx[cmap[ord(ch)]][0] / upm, 4)
            for ch in sorted(set(LATIN + FRENCH + PUNCT)) if ord(ch) in cmap}


def main(folder: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    widths = {}
    for filename, family, weight, css in FACES:
        widths[css.removesuffix(".css")] = metrics(Path(folder) / filename)
        data = build(Path(folder) / filename, family, weight)
        encoded = base64.b64encode(data).decode()
        (OUT / css).write_text(
            f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;"
            f"src:url(data:font/woff2;base64,{encoded}) format('woff2')}}\n")
        print(f"{css}: {len(data) / 1024:.1f} KB woff2, {len(encoded) / 1024:.1f} KB base64")
    (OUT / "metrics.json").write_text(json.dumps(widths, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
