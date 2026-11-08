import unittest

import bot


class BotTests(unittest.TestCase):
    def test_short_text_not_split(self):
        self.assertEqual(bot.split_text("hello"), ["hello"])

    def test_long_text_split_within_limit(self):
        text = ("word " * 3000).strip()
        parts = bot.split_text(text, limit=1000)
        self.assertTrue(len(parts) > 1)
        self.assertTrue(all(len(p) <= 1000 for p in parts))
        self.assertEqual(" ".join(parts).split(), text.split())

    def test_trim_history(self):
        h = [{"role": "user", "text": str(i)} for i in range(100)]
        self.assertEqual(len(bot.trim_history(h, max_turns=5)), 10)


if __name__ == "__main__":
    unittest.main()
