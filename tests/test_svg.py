import unittest

from profilegen.svg import esc, text


class EscapeTest(unittest.TestCase):
    def test_xml_escape(self):
        self.assertEqual(esc('<a href="x">&\'</a>'), "&lt;a href=&quot;x&quot;&gt;&amp;'&lt;/a&gt;")

    def test_text_element_is_escaped(self):
        svg = text(0, 0, "</text><script>alert(1)</script>")
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)


if __name__ == "__main__":
    unittest.main()
