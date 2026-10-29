"""Date and number formatting driven by the labels of profile.toml."""

from __future__ import annotations

from datetime import date


class Formatter:
    def __init__(self, lang: str, labels: dict):
        self.lang = lang
        self.months = labels["months"]
        self.weekdays = labels["weekdays"]

    def plural(self, n: int, one: str, many: str) -> str:
        """French uses the singular for 0 and 1, English only for 1."""
        return one if n == 1 or (self.lang == "fr" and n == 0) else many

    def number(self, value: int) -> str:
        grouped = f"{value:,}"
        return grouped.replace(",", "\u00a0") if self.lang == "fr" else grouped

    def month(self, day: date) -> str:
        return f"{self.months[day.month - 1]} {day.year}"

    def day(self, day: date, year: bool = True) -> str:
        month = self.months[day.month - 1]
        if self.lang == "fr":
            core = f"{day.day} {month}"
        else:
            core = f"{month} {day.day}"
        if not year:
            return core
        return f"{core} {day.year}" if self.lang == "fr" else f"{core}, {day.year}"

    def short_weekday(self, day: date) -> str:
        return f"{self.weekdays[day.weekday()]} {day.day} {self.months[day.month - 1]}"

    def span(self, start: date, end: date) -> str:
        if start == end:
            return self.day(start)
        if start.year != end.year:
            return f"{self.day(start)} – {self.day(end)}"
        if start.month != end.month:
            return f"{self.day(start, False)} – {self.day(end)}"
        if self.lang == "fr":
            return f"{start.day} – {self.day(end)}"
        return f"{self.months[start.month - 1]} {start.day} – {end.day}, {end.year}"
