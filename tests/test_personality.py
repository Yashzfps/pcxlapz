import unittest

from modules.personality import RiasPersonality


class PersonalityTests(unittest.TestCase):
    def test_style_prefix_and_suffix(self):
        persona = RiasPersonality()
        text = persona.style("hello")
        self.assertTrue(text.startswith("Rias: "))
        self.assertTrue(text.endswith("✨"))


if __name__ == "__main__":
    unittest.main()

