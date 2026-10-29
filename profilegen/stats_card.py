"""Stats: the contribution graph (cells light up like GitHub's), then total,
current streak (with a ring that draws itself) and longest streak."""

from __future__ import annotations

import math
from datetime import date, timedelta

from . import stats
from .svg import circle, document, fit, group, rect, text, width, wrap

W = 480
COLS, ROWS = 53, 7
PAD = 16
PITCH = (W - 2 * PAD) / COLS
CELL = PITCH - 1.6
GRID_Y = 46
RING_R = 31
SIZE = 18           # 18 × 309 / 480 ≥ 11 px on a phone

CSS = """
.col{animation:on .5s ease-out both}
.in{animation:in .6s cubic-bezier(.2,.8,.2,1) both}
.ring{animation:ring 1.2s cubic-bezier(.3,.7,.2,1) 1.3s both}
@keyframes on{from{opacity:0}to{opacity:1}}
@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes ring{from{stroke-dashoffset:%(circ).1f}to{stroke-dashoffset:0}}
"""


def levels(window: dict[date, int]) -> dict[date, int]:
    """0 for no commit, then 1-4 relative to the busiest day in view."""
    peak = max(window.values(), default=0)
    if peak <= 0:
        return {d: 0 for d in window}
    return {d: 0 if n <= 0 else min(4, math.ceil(4 * n / peak)) for d, n in window.items()}


def grid_start(today: date) -> date:
    """Monday of the first of the 53 weeks shown."""
    monday = today - timedelta(days=today.weekday())
    return monday - timedelta(weeks=COLS - 1)


def _day(fmt, d: date, today: date) -> str:
    return fmt.day(d, year=d.year != today.year)


def _span(fmt, s, today: date, start: date | None, end: date | None, ongoing: bool) -> str:
    if not start:
        return "—"
    if ongoing and start != today:
        return f'{_day(fmt, start, today)} – {s["present"]}'
    if start == end:
        return _day(fmt, start, today)
    return f"{_day(fmt, start, today)} – {_day(fmt, end, today)}"


def render(ctx, theme: str) -> str:
    c = ctx.palette(theme)
    s = ctx.labels["stats"]
    fmt, today, days, created = ctx.fmt, ctx.today, ctx.days, ctx.created
    skip = bool(ctx.cfg.get("streak_skip_weekends", True))
    start = grid_start(today)
    window = {start + timedelta(i): days.get(start + timedelta(i), 0)
              for i in range((today - start).days + 1)}
    lv = levels(window)
    body = []

    # months
    free_from = 0  # first x where a month label may start without touching the previous one
    for col in range(COLS):
        monday = start + timedelta(weeks=col)
        first = next((monday + timedelta(i) for i in range(7) if (monday + timedelta(i)).day == 1), None)
        x = PAD + col * PITCH
        name = s["months"][first.month - 1] if first else ""
        if first and first <= today and x >= free_from and x + width(name, SIZE) <= W - PAD:
            body.append(text(x, 30, name, class_="r", font_size=SIZE, fill=c["muted"]))
            free_from = x + width(name, SIZE) + 8

    # graph, lit column by column
    for col in range(COLS):
        cells = []
        for row in range(ROWS):
            d = start + timedelta(weeks=col, days=row)
            if d > today:
                continue
            cells.append(rect(PAD + col * PITCH, GRID_Y + row * PITCH, CELL, CELL, rx=1.5,
                              fill=c["green"][lv.get(d, 0)]))
        body += group(cells, class_="col", style=f"animation-delay:{.15 + col * .018:.3f}s")

    # "N contributions in the last year" and the legend (words dropped if tight)
    ly = GRID_Y + ROWS * PITCH + 26
    year_line = s["last_year"].replace("{n}", fmt.number(sum(window.values())))
    body.append(text(PAD, ly, year_line, class_="r", font_size=SIZE, fill=c["muted"]))
    squares = 5 * (PITCH + 2)
    words = width(s["less"], SIZE) + width(s["more"], SIZE) + 12
    with_words = width(year_line, SIZE) + 16 + squares + words <= W - 2 * PAD
    lx = W - PAD
    if with_words:
        lx -= width(s["more"], SIZE) + 6
        body.append(text(W - PAD, ly, s["more"], class_="r", font_size=SIZE, fill=c["muted"],
                         text_anchor="end"))
    for i in range(4, -1, -1):
        lx -= PITCH + 2
        body.append(rect(lx, ly - 11.5, CELL, CELL, rx=1.5, fill=c["green"][i]))
    if with_words:
        body.append(text(lx - 6, ly, s["less"], class_="r", font_size=SIZE, fill=c["muted"],
                         text_anchor="end"))

    # the three numbers
    top = ly + 22
    body.append(rect(PAD, top, W - 2 * PAD, 1, fill=c["border"]))
    total = stats.total(days)
    cur = stats.current_streak(days, today, skip)
    longest = stats.longest_streak(days, skip)
    ongoing = bool(cur.end and (today - cur.end).days <= 1)
    cols = [
        (fmt.number(total), s["total"], _span(fmt, s, today, created, today, True)),
        (str(cur.length), s["current"],
         _span(fmt, s, today, cur.start, cur.end, ongoing) if cur.length else _day(fmt, today, today)),
        (str(longest.length), s["longest"], _span(fmt, s, today, longest.start, longest.end, False)),
    ]
    # the ring column is narrower: its label is the shortest
    widths = (166, 128, W - 2 * PAD - 294)
    lefts = (PAD, PAD + 166, PAD + 294)
    y0 = top + 22
    circ = 2 * math.pi * RING_R
    date_lines = 1
    for i, (value, label, dates) in enumerate(cols):
        col_w = widths[i]
        cx = lefts[i] + col_w / 2
        part = []
        if i == 1:
            part += [circle(cx, y0 + RING_R + 4, RING_R, fill="none", stroke=c["track"], stroke_width=5),
                     circle(cx, y0 + RING_R + 4, RING_R, fill="none", stroke=c["green"][3],
                            stroke_width=5, stroke_linecap="round", stroke_dasharray=f"{circ:.1f}",
                            class_="ring",
                            transform=f"rotate(-90 {cx:.1f} {y0 + RING_R + 4:.1f})")]
        part.append(text(cx, y0 + RING_R + 14, value, class_="b", font_size=28, fill=c["fg"],
                         text_anchor="middle"))
        ly2 = y0 + 2 * RING_R + 36
        part.append(text(cx, ly2, fit(label, col_w - 6, SIZE), class_="r", font_size=SIZE,
                         fill=c["green"][3] if i == 1 else c["fg"], text_anchor="middle"))
        lines = wrap(dates, col_w - 6, SIZE, "sans", 2)
        date_lines = max(date_lines, len(lines))
        for k, line in enumerate(lines):
            part.append(text(cx, ly2 + 25 + k * 23, line, class_="r", font_size=SIZE,
                             fill=c["muted"], text_anchor="middle"))
        body += group(part, class_="in", style=f"animation-delay:{1.1 + i * .15:.2f}s")
        if i:
            body.append(rect(lefts[i], y0 + 6, 1, 2 * RING_R + 70, fill=c["border"]))

    bottom = y0 + 2 * RING_R + 36 + 25 + 23 * date_lines
    if skip:
        note = wrap(s["working_days"], W - 2 * PAD, SIZE, "sans", 2)
        for k, line in enumerate(note):
            body.append(text(W / 2, bottom + 34 + k * 23, line, class_="r", font_size=SIZE,
                             fill=c["muted"], text_anchor="middle"))
        bottom += 20 + 23 * len(note)
    height = int(bottom + 30)
    body.insert(0, rect(.5, .5, W - 1, height - 1, rx=6, fill=c["card"], stroke=c["border"]))

    desc = (f'{s["total"]}: {fmt.number(total)} ({cols[0][2]}). '
            f'{s["current"]}: {cur.length} ({cols[1][2]}). '
            f'{s["longest"]}: {longest.length} ({cols[2][2]}).'
            + (f' {s["working_days"]}.' if skip else ""))
    return document(W, height, s["title"], desc, CSS % {"circ": circ}, body)


def summary(ctx) -> str:
    """Text equivalent for the README alt attribute."""
    s, fmt, days, today = ctx.labels["stats"], ctx.fmt, ctx.days, ctx.today
    skip = bool(ctx.cfg.get("streak_skip_weekends", True))
    cur = stats.current_streak(days, today, skip)
    longest = stats.longest_streak(days, skip)
    return (f'{s["total"]}: {fmt.number(stats.total(days))} · {s["current"]}: {cur.length} · '
            f'{s["longest"]}: {longest.length}' + (f' · {s["working_days"]}' if skip else ""))
