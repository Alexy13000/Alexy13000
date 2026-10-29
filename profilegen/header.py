"""Header: name, role, and a line that cycles through what I build.

Final state (no animation, or reduced motion): everything visible, the
ticker on its first item.
"""

from __future__ import annotations

from .svg import document, esc, group, rect, text, width, wrap

W = 840
LINE = 30           # role and ticker size: 30 × 309 / 840 ≥ 11 px on a phone
STEP = 3.0          # seconds per ticker item
START = 1.2         # the ticker starts once the header has appeared

CSS = """
.in{animation:in .7s cubic-bezier(.2,.8,.2,1) both}
.sq{animation:sq .4s ease-out both}
.tick{opacity:0;animation:tick %(total)ss linear infinite}
.tick.first{opacity:1}
@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes sq{from{opacity:0}to{opacity:1}}
@keyframes tick{0%%{opacity:0;transform:translateY(14px)}%(a)s%%{opacity:1;transform:none}
  %(b)s%%{opacity:1;transform:none}%(c)s%%{opacity:0;transform:translateY(-14px)}100%%{opacity:0}}
"""


def render(ctx, theme: str) -> str:
    c = ctx.palette(theme)
    lab = ctx.labels
    items = lab["ticker"]
    total = STEP * len(items)
    share = 100 / len(items)
    css = CSS % {"total": total, "a": f"{share * .12:.2f}", "b": f"{share * .88:.2f}",
                 "c": f"{share:.2f}"}
    cx = W / 2
    body = []

    # a small row of contribution squares: the GitHub motif, lighting up once
    levels = (1, 2, 4, 3, 2, 4, 1, 3, 4, 2, 3)
    sq, gap = 12, 4
    x0 = cx - (len(levels) * (sq + gap) - gap) / 2
    for i, lv in enumerate(levels):
        body.append(rect(x0 + i * (sq + gap), 22, sq, sq, rx=2.5, fill=c["green"][lv],
                         class_="sq", style=f"animation-delay:{.1 + i * .05:.2f}s"))

    body += group([text(cx, 104, lab["name"], class_="b", font_size=60, fill=c["fg"],
                         text_anchor="middle", letter_spacing=-1)],
                  class_="in", style="animation-delay:.2s")
    role, _, company = lab["role"].partition("@")
    body += group([f'<text x="{cx}" y="152" class="r" font-size="{LINE}" fill="{c["muted"]}" '
                   f'text-anchor="middle">{esc(role.strip())} <tspan class="s" fill="{c["fg"]}">'
                   f'@ {esc(company.strip())}</tspan></text>'],
                  class_="in", style="animation-delay:.45s")

    subtitle = wrap(lab["subtitle"], W - 80, LINE, "sans", 2)
    body += group([text(cx, 200 + k * 38, line, class_="r", font_size=LINE, fill=c["fg"],
                         text_anchor="middle") for k, line in enumerate(subtitle)],
                  class_="in", style="animation-delay:.6s")
    ticker_y = 200 + len(subtitle) * 38 + 30
    height = ticker_y + 28

    # the ticker: each line is complete ("Building …"), so it stays centred
    ticker = []
    for i, item in enumerate(items):
        line = f'{lab["building"]} {item}'
        cls = "tick first" if i == 0 else "tick"
        ticker.append(group([text(cx, ticker_y, line, class_="s", font_size=LINE, fill=c["accent"],
                                  text_anchor="middle")],
                            class_=cls, style=f"animation-delay:{START + i * STEP - STEP * .12:.2f}s"))
    body += group([g for t in ticker for g in t], class_="in", style="animation-delay:.85s")

    longest = max(width(f'{lab["building"]} {i}', LINE, "semi") for i in items)
    assert longest < W - 40, "ticker item too long for the header"
    return document(W, height, f'{lab["name"]} — {lab["role"]}. {lab["subtitle"]}',
                    f'{lab["building"]}: ' + ", ".join(items) + ".", css, body)
