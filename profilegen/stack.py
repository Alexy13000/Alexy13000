"""Stack: one row of sober, hand-drawn monochrome icons."""

from __future__ import annotations

from .svg import document, esc, group, rect

W, TILE = 480, 48

CSS = """
.tile{animation:tile .5s cubic-bezier(.2,.8,.2,1) both}
@keyframes tile{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
"""


def _icons(ink: str, bg: str) -> dict:
    """28 × 28 glyphs. Strokes use `ink`; cut-outs use the tile colour `bg`."""
    s = (f'fill="none" stroke="{ink}" stroke-width="2" stroke-linecap="round" '
         f'stroke-linejoin="round"')
    return {
        "kotlin": f'<path d="M4 4h20L14 14l10 10H4z" fill="{ink}"/>',
        "python": (f'<path d="M14 3c-5 0-6 2-6 4v3h7v1H6c-2.5 0-3.5 2-3.5 4.5S3.5 20 6 20h2v-3c0-2 1.5-3.5 3.5-3.5h5'
                   f'c2 0 3.5-1.5 3.5-3.5V7c0-2-2-4-6-4z" fill="{ink}"/>'
                   f'<path d="M14 25c5 0 6-2 6-4v-3h-7v-1h9c2.5 0 3.5-2 3.5-4.5S24.5 8 22 8h-2v3c0 2-1.5 3.5-3.5 3.5h-5'
                   f'c-2 0-3.5 1.5-3.5 3.5V21c0 2 2 4 6 4z" fill="{ink}" opacity=".55"/>'
                   f'<circle cx="11" cy="6.5" r="1.3" fill="{bg}"/><circle cx="17" cy="21.5" r="1.3" fill="{bg}"/>'),
        "flask": f'<path d="M11 3h6M12 3v8L5 23a2 2 0 0 0 2 3h14a2 2 0 0 0 2-3l-7-12V3M8.5 18h11" {s}/>',
        "sqlite": (f'<ellipse cx="14" cy="6.5" rx="9" ry="3.5" {s}/>'
                   f'<path d="M5 6.5v15c0 2 4 3.5 9 3.5s9-1.5 9-3.5v-15M5 14c0 2 4 3.5 9 3.5s9-1.5 9-3.5" {s}/>'),
        "go": (f'<path d="M3 11h6M2 15h5M4 19h4" {s}/>'
               f'<path d="M17 9.5a5 5 0 1 0 1 5.5h-4" {s}/><circle cx="23" cy="14" r="3.6" {s}/>'),
        "javascript": (f'<rect x="3" y="3" width="22" height="22" rx="3" fill="{ink}"/>'
                       f'<path d="M14 12v7.5a2 2 0 0 1-3.5 1.3M22 13a2.3 2.3 0 0 0-4 .5c0 2.8 4.5 1.8 4.5 4.6a2.3 2.3 0 0 1-4.3 1" '
                       f'fill="none" stroke="{bg}" stroke-width="1.9" stroke-linecap="round"/>'),
        "windows": (f'<path d="M4 6.5l8.5-1.2v8.2H4zM14.5 5l9.5-1.4v9.9h-9.5zM4 15.5h8.5v8.2L4 22.5zM14.5 15.5H24v9.9'
                    f'L14.5 24z" fill="{ink}"/>'),
        "actions": (f'<circle cx="8" cy="8" r="3.5" {s}/><circle cx="20" cy="20" r="3.5" {s}/>'
                    f'<path d="M8 11.5v3a4 4 0 0 0 4 4h4.5M11.5 8H18a2 2 0 0 1 2 2v6.5" {s}/>'
                    f'<path d="M22 6l-4-2.5v5z" fill="{ink}"/>'),
    }


def render(ctx, theme: str) -> str:
    c = ctx.palette(theme)
    stack = ctx.labels["stack"]
    icons = _icons(c["fg"], c["subtle"])
    gap = (W - 2 - len(stack) * TILE) / (len(stack) - 1)
    body = []
    for i, item in enumerate(stack):
        x = 1 + i * (TILE + gap)
        tile = [rect(x, 1, TILE, TILE, rx=10, fill=c["subtle"], stroke=c["border"]),
                f'<g transform="translate({x + 10:.1f} 11)">{icons[item["icon"]]}</g>',
                f'<title>{esc(item["name"])}</title>']
        body += group(tile, class_="tile", style=f"animation-delay:{.1 + i * .06:.2f}s")
    names = ", ".join(i["name"] for i in stack)
    return document(W, TILE + 2, f'{ctx.labels["stack_title"]}: {names}', names, CSS, body,
                    faces=())
