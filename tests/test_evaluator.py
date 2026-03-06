"""Tests for the Evaluator."""

import unittest
from unittest.mock import MagicMock, patch

from src.agent.evaluator import Evaluator


def _make_evaluator():
    mock_client = MagicMock()
    return Evaluator(mock_client)


class TestMathEvaluation(unittest.TestCase):

    def setUp(self):
        self.evaluator = _make_evaluator()

    def test_correct_integer_answer(self):
        solution = "The answer is...\nFINAL ANSWER: 42"
        result = self.evaluator._evaluate_math(solution, "42")
        self.assertTrue(result["is_correct"])
        self.assertEqual(result["score"], 1.0)

    def test_correct_answer_with_commas(self):
        solution = "FINAL ANSWER: 1,234"
        result = self.evaluator._evaluate_math(solution, "1234")
        self.assertTrue(result["is_correct"])

    def test_wrong_answer(self):
        solution = "FINAL ANSWER: 10"
        result = self.evaluator._evaluate_math(solution, "42")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["score"], 0.0)

    def test_missing_final_answer(self):
        solution = "The answer is somewhere in here but not formatted."
        result = self.evaluator._evaluate_math(solution, "42")
        self.assertFalse(result["is_correct"])
        self.assertIn("missing_final_answer", result["errors"])

    def test_float_tolerance(self):
        solution = "FINAL ANSWER: 3.14159"
        result = self.evaluator._evaluate_math(solution, "3.14159")
        self.assertTrue(result["is_correct"])

    def test_correct_answer_case_insensitive(self):
        solution = "final answer: 99"
        result = self.evaluator._evaluate_math(solution, "99")
        self.assertTrue(result["is_correct"])


class TestCodeEvaluation(unittest.TestCase):

    def setUp(self):
        self.evaluator = _make_evaluator()

    def test_passing_code(self):
        solution = (
            "```python\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "```"
        )
        test_code = "assert add(2, 3) == 5\nprint('passed')"
        result = self.evaluator._evaluate_code(solution, test_code)
        self.assertTrue(result["is_correct"])
        self.assertEqual(result["score"], 1.0)

    def test_failing_code(self):
        solution = (
            "```python\n"
            "def add(a, b):\n"
            "    return a - b  # wrong\n"
            "```"
        )
        test_code = "assert add(2, 3) == 5"
        result = self.evaluator._evaluate_code(solution, test_code)
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["score"], 0.0)

    def test_no_code_block(self):
        solution = "Here is my answer in plain text."
        result = self.evaluator._evaluate_code(solution, "assert True")
        self.assertFalse(result["is_correct"])
        self.assertIn("no_code_found", result["errors"])


class TestNormalizeNumber(unittest.TestCase):

    def test_integer(self):
        self.assertEqual(Evaluator._normalize_number("42"), 42.0)

    def test_float(self):
        self.assertAlmostEqual(Evaluator._normalize_number("3.14"), 3.14)

    def test_with_commas(self):
        self.assertEqual(Evaluator._normalize_number("1,234,567"), 1234567.0)

    def test_negative(self):
        self.assertEqual(Evaluator._normalize_number("-5"), -5.0)

    def test_non_numeric(self):
        self.assertIsNone(Evaluator._normalize_number("abc"))


if __name__ == "__main__":
    unittest.main()
