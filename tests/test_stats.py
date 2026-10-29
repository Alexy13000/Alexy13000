import unittest
from datetime import date, timedelta

from profilegen.stats import (BestDay, BusiestWeekday, Streak, best_day,
                              busiest_weekday, current_streak, year_total,
                              longest_streak, total)

# Reference week: Monday 2026-10-19 ... Sunday 2026-10-25
MON, TUE, WED, THU, FRI, SAT, SUN = (date(2026, 10, 19) + timedelta(d)
                                     for d in range(7))
NEXT_MON = SUN + timedelta(1)
NEXT_TUE = SUN + timedelta(2)


def calendar(start, end, active=(), counts=None):
    """Zero-filled calendar from start to end, with active days set to 1."""
    days, d = {}, start
    while d <= end:
        days[d] = 0
        d += timedelta(1)
    for d in active:
        days[d] = 1
    days.update(counts or {})
    return days


class CurrentStreakTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(current_streak({}, MON), Streak())

    def test_all_zero(self):
        self.assertEqual(current_streak(calendar(MON, FRI), FRI), Streak())

    def test_today_counts(self):
        days = calendar(MON, WED, active=[TUE, WED])
        self.assertEqual(current_streak(days, WED), Streak(2, TUE, WED))

    def test_today_zero_starts_from_yesterday(self):
        days = calendar(MON, WED, active=[MON, TUE])
        self.assertEqual(current_streak(days, WED), Streak(2, MON, TUE))

    def test_today_and_yesterday_zero_breaks(self):
        days = calendar(MON, THU, active=[MON, TUE])
        self.assertEqual(current_streak(days, THU), Streak())

    def test_today_missing_from_data(self):
        days = calendar(MON, TUE, active=[MON, TUE])
        self.assertEqual(current_streak(days, WED), Streak(2, MON, TUE))

    def test_weekend_gap_is_skipped(self):
        days = calendar(THU, NEXT_MON, active=[THU, FRI, NEXT_MON])
        self.assertEqual(current_streak(days, NEXT_MON),
                         Streak(3, THU, NEXT_MON))

    def test_weekend_gap_breaks_without_skip(self):
        days = calendar(THU, NEXT_MON, active=[THU, FRI, NEXT_MON])
        self.assertEqual(current_streak(days, NEXT_MON, skip_weekends=False),
                         Streak(1, NEXT_MON, NEXT_MON))

    def test_monday_zero_after_weekend_starts_from_friday(self):
        days = calendar(THU, NEXT_MON, active=[THU, FRI])
        self.assertEqual(current_streak(days, NEXT_MON), Streak(2, THU, FRI))

    def test_monday_zero_after_weekend_breaks_on_tuesday(self):
        days = calendar(THU, NEXT_TUE, active=[THU, FRI])
        self.assertEqual(current_streak(days, NEXT_TUE), Streak())

    def test_weekend_contributions_count(self):
        days = calendar(FRI, NEXT_MON, active=[FRI, SAT, SUN, NEXT_MON])
        self.assertEqual(current_streak(days, NEXT_MON),
                         Streak(4, FRI, NEXT_MON))

    def test_today_is_sunday_with_zero(self):
        days = calendar(THU, SUN, active=[THU, FRI])
        self.assertEqual(current_streak(days, SUN), Streak(2, THU, FRI))

    def test_weekend_only_activity(self):
        days = calendar(FRI, NEXT_MON, active=[SAT, SUN])
        self.assertEqual(current_streak(days, NEXT_MON), Streak(2, SAT, SUN))
        self.assertEqual(current_streak(days, NEXT_TUE), Streak())

    def test_stops_at_first_known_day(self):
        days = calendar(WED, FRI, active=[WED, THU, FRI])
        self.assertEqual(current_streak(days, FRI), Streak(3, WED, FRI))

    def test_crosses_year_boundary(self):
        days = calendar(date(2025, 12, 29), date(2026, 1, 2),
                        active=[date(2025, 12, 30), date(2025, 12, 31),
                                date(2026, 1, 1), date(2026, 1, 2)])
        self.assertEqual(current_streak(days, date(2026, 1, 2)),
                         Streak(4, date(2025, 12, 30), date(2026, 1, 2)))


class LongestStreakTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(longest_streak({}), Streak())

    def test_all_zero(self):
        self.assertEqual(longest_streak(calendar(MON, SUN)), Streak())

    def test_single_day(self):
        days = calendar(MON, SUN, active=[WED])
        self.assertEqual(longest_streak(days), Streak(1, WED, WED))

    def test_picks_the_longest(self):
        days = calendar(MON, SUN, active=[MON, WED, THU, FRI])
        self.assertEqual(longest_streak(days), Streak(3, WED, FRI))

    def test_tie_keeps_the_earliest(self):
        days = calendar(MON, FRI, active=[MON, TUE, THU, FRI])
        self.assertEqual(longest_streak(days), Streak(2, MON, TUE))

    def test_spans_weekend(self):
        days = calendar(MON, NEXT_TUE,
                        active=[THU, FRI, NEXT_MON, NEXT_TUE])
        self.assertEqual(longest_streak(days), Streak(4, THU, NEXT_TUE))
        self.assertEqual(longest_streak(days, skip_weekends=False),
                         Streak(2, THU, FRI))

    def test_weekday_gap_breaks(self):
        days = calendar(MON, FRI, active=[MON, TUE, THU])
        self.assertEqual(longest_streak(days), Streak(2, MON, TUE))

    def test_today_zero_does_not_shorten(self):
        days = calendar(MON, THU, active=[MON, TUE, WED])
        self.assertEqual(longest_streak(days), Streak(3, MON, WED))

    def test_sparse_mapping(self):
        # Dates absent from the mapping count as zero.
        days = {MON: 1, TUE: 1, THU: 1}
        self.assertEqual(longest_streak(days), Streak(2, MON, TUE))


class TotalsTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(total({}), 0)
        self.assertEqual(total(calendar(MON, SUN, counts={MON: 3, SUN: 4})), 7)

    def test_best_day(self):
        self.assertEqual(best_day({}), BestDay())
        self.assertEqual(best_day(calendar(MON, SUN)), BestDay())
        days = calendar(MON, SUN, counts={TUE: 5, THU: 5, SAT: 2})
        self.assertEqual(best_day(days), BestDay(5, TUE))


if __name__ == "__main__":
    unittest.main()


class YearAndWeekdayTest(unittest.TestCase):
    def test_year_total(self):
        days = {date(2025, 12, 31): 4, date(2026, 1, 1): 2, date(2026, 6, 1): 3}
        self.assertEqual(year_total(days, 2026), 5)
        self.assertEqual(year_total(days, 2025), 4)
        self.assertEqual(year_total(days, 2024), 0)
        self.assertEqual(year_total({}, 2026), 0)

    def test_busiest_weekday(self):
        days = calendar(MON, NEXT_TUE, counts={TUE: 2, NEXT_TUE: 3, SAT: 4})
        self.assertEqual(busiest_weekday(days), BusiestWeekday(1, 5))

    def test_busiest_weekday_tie_prefers_monday_first(self):
        days = calendar(MON, SUN, counts={WED: 2, MON: 2})
        self.assertEqual(busiest_weekday(days), BusiestWeekday(0, 2))

    def test_busiest_weekday_empty(self):
        self.assertEqual(busiest_weekday({}), BusiestWeekday())
        self.assertEqual(busiest_weekday(calendar(MON, SUN)), BusiestWeekday())
