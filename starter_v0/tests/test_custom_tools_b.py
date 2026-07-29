from __future__ import annotations

import unittest
from tools.text_stats.tool import text_stats
from tools.math_eval.tool import math_eval
from tools.datetime_utils.tool import datetime_utils


class TestCustomToolsB(unittest.TestCase):

    # --- Tests for text_stats ---
    def test_text_stats_basic(self):
        sample_text = (
            "Artificial Intelligence is transforming the world. Visit https://openai.com for more info. "
            "Contact us at research@example.com! Intelligence research is key."
        )
        res = text_stats(text=sample_text, top_keywords_limit=3)
        self.assertIsNone(res["error"])
        self.assertGreater(res["word_count"], 10)
        self.assertIn("https://openai.com", res["extracted_urls"])
        self.assertIn("research@example.com", res["extracted_emails"])
        self.assertGreater(len(res["top_keywords"]), 0)

    def test_text_stats_empty(self):
        res = text_stats(text="")
        self.assertIsNotNone(res["error"])
        self.assertEqual(res["word_count"], 0)

    # --- Tests for math_eval ---
    def test_math_eval_success(self):
        res1 = math_eval("(120 + 80) / 2")
        self.assertIsNone(res1["error"])
        self.assertEqual(res1["result"], 100.0)
        self.assertEqual(res1["formatted_result"], "100")

        res2 = math_eval("round(150.789, 2)")
        self.assertIsNone(res2["error"])
        self.assertEqual(res2["result"], 150.79)

    def test_math_eval_division_by_zero(self):
        res = math_eval("100 / 0")
        self.assertIsNotNone(res["error"])
        self.assertIsNone(res["result"])

    def test_math_eval_invalid(self):
        res = math_eval("import os; os.system('ls')")
        self.assertIsNotNone(res["error"])

    # --- Tests for datetime_utils ---
    def test_datetime_utils_current_time(self):
        res = datetime_utils(action="current_time")
        self.assertIsNone(res["error"])
        self.assertIn("year", res["details"])

    def test_datetime_utils_date_diff(self):
        res = datetime_utils(action="date_diff", start_date="2026-07-01", end_date="2026-07-10")
        self.assertIsNone(res["error"])
        self.assertEqual(res["details"]["days_difference"], 9)

    def test_datetime_utils_add_days(self):
        res = datetime_utils(action="add_days", start_date="2026-07-01", days=10)
        self.assertIsNone(res["error"])
        self.assertEqual(res["result"], "2026-07-11")


if __name__ == "__main__":
    unittest.main()
