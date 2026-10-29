"""Contribution statistics: totals, best day and streaks.

All functions take ``days``: a mapping ``datetime.date -> int`` (contribution
count). Missing dates count as zero. Pure functions, no I/O.

Streak rules
------------
* A day with at least one contribution extends the streak.
* When ``skip_weekends`` is true, a Saturday or Sunday *without* contributions
  is neutral: it neither breaks nor extends the streak. Weekend contributions
  still count.
* The current streak may start from yesterday: today at zero does not break it
  (the day is not over yet).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Mapping, Optional

ONE_DAY = timedelta(days=1)


@dataclass(frozen=True)
class Streak:
    length: int = 0
    start: Optional[date] = None
    end: Optional[date] = None


@dataclass(frozen=True)
class BestDay:
    count: int = 0
    day: Optional[date] = None


def is_weekend(day: date) -> bool:
    return day.weekday() >= 5


def _neutral(day: date, skip_weekends: bool) -> bool:
    return skip_weekends and is_weekend(day)


def total(days: Mapping[date, int]) -> int:
    return sum(max(0, n) for n in days.values())


def best_day(days: Mapping[date, int]) -> BestDay:
    """Highest daily count; the earliest date wins a tie."""
    best = BestDay()
    for day in sorted(days):
        if days[day] > best.count:
            best = BestDay(days[day], day)
    return best


def current_streak(days: Mapping[date, int], today: date,
                   skip_weekends: bool = True) -> Streak:
    if not days:
        return Streak()
    first = min(days)
    cursor = today
    if days.get(today, 0) <= 0:
        cursor -= ONE_DAY  # today is still in progress
    length, start, end = 0, None, None
    while cursor >= first:
        if days.get(cursor, 0) > 0:
            length += 1
            start = cursor
            end = end or cursor
        elif not _neutral(cursor, skip_weekends):
            break
        cursor -= ONE_DAY
    return Streak(length, start, end)


def longest_streak(days: Mapping[date, int],
                   skip_weekends: bool = True) -> Streak:
    """Longest run; the earliest run wins a tie."""
    if not days:
        return Streak()
    best = Streak()
    length, start, end = 0, None, None
    cursor, last = min(days), max(days)
    while cursor <= last:
        if days.get(cursor, 0) > 0:
            if length == 0:
                start = cursor
            length += 1
            end = cursor
            if length > best.length:
                best = Streak(length, start, end)
        elif not _neutral(cursor, skip_weekends):
            length = 0
        cursor += ONE_DAY
    return best


def year_total(days: Mapping[date, int], year: int) -> int:
    return sum(max(0, n) for d, n in days.items() if d.year == year)


@dataclass(frozen=True)
class BusiestWeekday:
    weekday: Optional[int] = None  # 0 = Monday … 6 = Sunday
    count: int = 0


def busiest_weekday(days: Mapping[date, int]) -> BusiestWeekday:
    """Weekday with the most contributions overall; Monday-first on a tie."""
    totals = [0] * 7
    for day, n in days.items():
        totals[day.weekday()] += max(0, n)
    best = max(range(7), key=lambda i: (totals[i], -i))
    return BusiestWeekday(best, totals[best]) if totals[best] > 0 else BusiestWeekday()
