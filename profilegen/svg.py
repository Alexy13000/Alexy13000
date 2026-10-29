"""Small SVG toolkit shared by the cards: fonts, text metrics, elements."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# Face keys match the CSS files in assets/fonts/ (built by tools/build_fonts.py)
FACES = {
    "sans": ("'HD Sans'", 400, "sans-400"),
    "semi": ("'HD Sans'", 600, "sans-600"),
    "bold": ("'HD Sans'", 700, "sans-700"),
}

REDUCED_MOTION = ("@media (prefers-reduced-motion: reduce){"
                  "*{animation:none!important;transition:none!important}}")

# GitHub's own stack as the fallback, so a missing glyph still looks native
_STACK = "'HD Sans',-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
BASE_CSS = (f"text{{font-family:{_STACK}}}"
            ".r{font-weight:400}.s{font-weight:600}.b{font-weight:700}")


@lru_cache(maxsize=None)
def _metrics() -> dict:
    return json.loads((FONTS / "metrics.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def font_css(face: str) -> str:
    return (FONTS / f"{FACES[face][2]}.css").read_text(encoding="utf-8").strip()


def esc(text) -> str:
    return escape(str(text), {'"': "&quot;"})


def width(text: str, size: float, face: str = "sans", spacing: float = 0) -> float:
    """Rendered width of `text`, from the real advance widths of the subset."""
    table = _metrics()[FACES[face][2]]
    fallback = 0.6
    return sum(table.get(ch, fallback) for ch in text) * size + spacing * len(text)


def fit(text: str, max_width: float, size: float, face: str = "sans", spacing: float = 0) -> str:
    """Truncate with an ellipsis so the text fits `max_width`."""
    if width(text, size, face, spacing) <= max_width:
        return text
    while text and width(text + "…", size, face, spacing) > max_width:
        text = text[:-1]
    return text.rstrip(" ·,-—") + "…"


def wrap(text: str, max_width: float, size: float, face: str = "sans",
         lines: int = 3, spacing: float = 0) -> list[str]:
    """Greedy word wrap on at most `lines` lines; the last one is truncated."""
    words, out, line = text.split(), [], ""
    for i, word in enumerate(words):
        candidate = f"{line} {word}".strip()
        if not line or width(candidate, size, face, spacing) <= max_width:
            line = candidate
            continue
        out.append(line)
        line = word
        if len(out) == lines - 1:
            line = " ".join(words[i:])
            break
    if line:
        out.append(line)
    return [fit(item, max_width, size, face, spacing) for item in out[:lines]]


def document(w: int, h: int, title: str, desc: str, css: str, body: list[str],
             faces: tuple[str, ...] = ("sans", "semi", "bold")) -> str:
    fonts = "".join(font_css(f) for f in faces)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">',
        f'<title id="t">{esc(title)}</title>',
        f'<desc id="d">{esc(desc)}</desc>',
        f"<style>{fonts}{BASE_CSS}{css}{REDUCED_MOTION}</style>",
        *body,
        "</svg>",
        "",
    ])


def _num(value) -> str:
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def attrs(**values) -> str:
    """Render keyword arguments as XML attributes (`class_` -> `class`)."""
    parts = []
    for key, value in values.items():
        if value is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        parts.append(f'{name}="{esc(_num(value))}"')
    return " ".join(parts)


def text(x, y, content, **extra) -> str:
    return f"<text {attrs(x=float(x), y=float(y), **extra)}>{esc(content)}</text>"


def rect(x, y, w, h, **extra) -> str:
    return f"<rect {attrs(x=float(x), y=float(y), width=float(w), height=float(h), **extra)}/>"


def circle(cx, cy, r, **extra) -> str:
    return f"<circle {attrs(cx=float(cx), cy=float(cy), r=float(r), **extra)}/>"


def path(d: str, **extra) -> str:
    return f"<path {attrs(d=d, **extra)}/>"


def group(content: list[str], **extra) -> list[str]:
    return [f"<g {attrs(**extra)}>", *content, "</g>"]
