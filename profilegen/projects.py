"""Projects: compact cards in the style of GitHub's pinned repositories."""

from __future__ import annotations

from .svg import circle, document, fit, group, rect, text, width, wrap

W = 480
SIZE = 18           # 18 × 309 / 480 ≥ 11 px on a phone
GAP = 10

# GitHub linguist colours for languages; topics get a neutral dot
LANG_COLOURS = {"Kotlin": "#A97BFF", "Python": "#3572A5", "Go": "#00ADD8"}

CSS = """
.card{animation:card .6s cubic-bezier(.2,.8,.2,1) both}
@keyframes card{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
"""

# 20 × 20 line icons, drawn by hand
ICONS = {
    "tv": '<rect x="2" y="3" width="16" height="11" rx="2"/><path d="M7 17h6M10 14v3"/>',
    "layout": '<rect x="2" y="3" width="16" height="14" rx="2"/><path d="M2 7h16M8 7v10"/>',
    "pulse": '<path d="M2 10h4l2-5 4 10 2-5h4"/>',
    "plug": '<path d="M7 2v4M13 2v4M5 6h10v3a5 5 0 0 1-10 0zM10 14v4"/>',
    "ticket": '<path d="M3 5h14v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4z"/><path d="M12 5v10" stroke-dasharray="2 2"/>',
    "clinic": '<rect x="3" y="3" width="14" height="14" rx="3"/><path d="M10 6.5v7M6.5 10h7"/>',
}


def render(ctx, theme: str) -> str:
    c = ctx.palette(theme)
    projects = ctx.labels["projects"]
    body, y = [], 1
    for i, p in enumerate(projects):
        tag = p.get("tag", "")
        tag_w = width(tag, SIZE) + 20 if tag else 0
        dot = LANG_COLOURS.get(tag.split(" · ")[0], c["muted"])
        lines = wrap(p["text"], W - 46 - 16, SIZE, "sans", 2)
        card_h = 52 + 24 * len(lines)
        card = [
            rect(.5, y, W - 1, card_h, rx=6, fill=c["card"], stroke=c["border"]),
            f'<g transform="translate(16 {y + 15})" fill="none" stroke="{c["muted"]}" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[p["icon"]]}</g>',
            text(46, y + 31, fit(p["title"], W - 46 - 16 - tag_w - 12, SIZE, "semi"), class_="s",
                 font_size=SIZE, fill=c["accent"]),
        ]
        card += [text(46, y + 58 + k * 24, line, class_="r", font_size=SIZE, fill=c["muted"])
                 for k, line in enumerate(lines)]
        if tag:
            card += [circle(W - 16 - tag_w + 6, y + 25, 6, fill=dot),
                     text(W - 16, y + 31, tag, class_="r", font_size=SIZE, fill=c["muted"],
                          text_anchor="end")]
        body += group(card, class_="card", style=f"animation-delay:{.1 + i * .08:.2f}s")
        y += card_h + GAP
    height = int(y - GAP + 1)
    alt = ctx.labels["readme"]["alt_projects"]
    desc = "; ".join(f'{p["title"]}: {p["text"]}' for p in projects)
    return document(W, height, alt, desc, CSS, body)
