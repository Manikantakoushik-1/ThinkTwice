"""Tests for the Reflector."""

import unittest
from unittest.mock import MagicMock

from src.agent.reflector import Reflector


_STRUCTURED_RESPONSE = """\
WHAT WENT WRONG:
The calculation skipped the multiplication step.

ROOT CAUSE:
The agent misread the problem and added instead of multiplied.

KEY INSIGHT:
Always re-read the problem statement before computing.

STRATEGY:
1. Re-read the problem carefully.
2. Identify the correct operation (multiply vs. add).
3. Show each step explicitly.
"""


def _make_reflector(llm_response: str = _STRUCTURED_RESPONSE):
    mock_client = MagicMock()
    mock_client.generate_with_history.return_value = llm_response
    return Reflector(mock_client)


class TestReflector(unittest.TestCase):

    def setUp(self):
        self.reflector = _make_reflector()

    def test_reflect_calls_llm(self):
        self.reflector.reflect(
            task_description="What is 3 * 4?",
            failed_solution="FINAL ANSWER: 7",
            evaluation_feedback="Expected 12, got 7",
        )
        self.reflector._client.generate_with_history.assert_called_once()

    def test_reflect_returns_all_keys(self):
        result = self.reflector.reflect(
            task_description="What is 3 * 4?",
            failed_solution="FINAL ANSWER: 7",
            evaluation_feedback="Expected 12, got 7",
        )
        self.assertIn("what_went_wrong", result)
        self.assertIn("root_cause", result)
        self.assertIn("key_insight", result)
        self.assertIn("strategy", result)
        self.assertIn("full_text", result)

    def test_parse_all_sections(self):
        parsed = Reflector._parse_reflection(_STRUCTURED_RESPONSE)
        self.assertIn("multiplication step", parsed["what_went_wrong"])
        self.assertIn("misread", parsed["root_cause"])
        self.assertIn("re-read", parsed["key_insight"])
        self.assertIn("Re-read", parsed["strategy"])

    def test_parse_reflection_fallback(self):
        """Unstructured output should land in key_insight."""
        parsed = Reflector._parse_reflection("Something went wrong, try again.")
        self.assertEqual(parsed["key_insight"], "Something went wrong, try again.")

    def test_retry_note_on_second_attempt(self):
        self.reflector.reflect(
            task_description="Q",
            failed_solution="A",
            evaluation_feedback="Wrong",
            previous_reflections="some reflections",
            attempt_number=2,
        )
        call_args = self.reflector._client.generate_with_history.call_args
        messages = call_args[0][0]
        user_content = messages[1]["content"]
        self.assertIn("NEW and DEEPER", user_content)

    def test_full_text_present(self):
        result = self.reflector.reflect("Q", "A", "Wrong")
        self.assertEqual(result["full_text"], _STRUCTURED_RESPONSE)


if __name__ == "__main__":
    unittest.main()
