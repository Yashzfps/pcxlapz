import unittest

from modules.personality import error, greeting, info, style, success


class TestPersonality(unittest.TestCase):
    def test_greeting_has_rias_name(self):
        self.assertIn("Rias", greeting())

    def test_style_prefixes_text(self):
        self.assertTrue(style("Hello").startswith("Rias ✨:"))

    def test_success_error_info_wrappers(self):
        self.assertIn("Done", success("Done"))
        self.assertIn("Oops", error("Oops"))
        self.assertIn("Info", info("Info"))


if __name__ == "__main__":
    unittest.main()
