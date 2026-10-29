import unittest
from datetime import date

from profilegen.readme import links
from profilegen.stats_card import COLS, grid_start, levels

LABELS = {"readme": {"links": {"email": "Email", "linkedin": "LinkedIn", "website": "Website"}}}


class GraphTest(unittest.TestCase):
    def test_grid_starts_on_a_monday_53_weeks_back(self):
        today = date(2026, 10, 29)  # a Thursday
        start = grid_start(today)
        self.assertEqual(start.weekday(), 0)
        self.assertEqual((today - start).days // 7, COLS - 1)

    def test_levels(self):
        d = [date(2026, 1, i) for i in range(1, 6)]
        self.assertEqual(levels({d[0]: 0, d[1]: 1, d[2]: 4, d[3]: 8, d[4]: 3}),
                         {d[0]: 0, d[1]: 1, d[2]: 2, d[3]: 4, d[4]: 2})
        self.assertEqual(levels({d[0]: 0, d[1]: 0}), {d[0]: 0, d[1]: 0})
        self.assertEqual(levels({}), {})


class LinksTest(unittest.TestCase):
    def test_empty_links_are_hidden(self):
        self.assertEqual(links({"contact": {"email": "", "linkedin": " ", "website": ""}}, LABELS), [])
        self.assertEqual(links({}, LABELS), [])

    def test_filled_links_are_escaped(self):
        out = links({"contact": {"email": "a@b.c", "website": 'https://x.y/"z'}}, LABELS)
        self.assertEqual(out[0], '<a href="mailto:a@b.c">Email</a>')
        self.assertIn("&quot;", out[1])


if __name__ == "__main__":
    unittest.main()
