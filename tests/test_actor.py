"""Tests for the Actor."""

import unittest
from unittest.mock import MagicMock

from src.agent.actor import Actor


def _make_actor():
    mock_client = MagicMock()
    mock_client.generate_with_history.return_value = "FINAL ANSWER: 42"
    return Actor(mock_client)


class TestActor(unittest.TestCase):

    def setUp(self):
        self.actor = _make_actor()

    def test_generate_solution_calls_llm(self):
        self.actor.generate_solution("What is 2+2?", task_type="math")
        self.actor._client.generate_with_history.assert_called_once()

    def test_generate_solution_with_reflection_context(self):
        context = "=== Previous Attempts ===\nAttempt 1 [✗]\n  Key Insight: use step-by-step arithmetic"
        self.actor.generate_solution(
            "What is 2+2?",
            task_type="math",
            reflection_context=context,
            attempt_number=2,
        )
        call_args = self.actor._client.generate_with_history.call_args
        messages = call_args[0][0]
        # The system prompt should contain the reflection context
        system_content = messages[0]["content"]
        self.assertIn("Previous Attempts", system_content)

    def test_generate_solution_retry_prefix(self):
        """On attempt > 1 with context, a retry warning is prepended."""
        self.actor.generate_solution(
            "Solve it",
            task_type="math",
            reflection_context="some reflections",
            attempt_number=2,
        )
        call_args = self.actor._client.generate_with_history.call_args
        messages = call_args[0][0]
        user_content = messages[1]["content"]
        self.assertIn("tried this before and failed", user_content)

    def test_no_retry_prefix_on_first_attempt(self):
        self.actor.generate_solution("Solve it", attempt_number=1)
        call_args = self.actor._client.generate_with_history.call_args
        messages = call_args[0][0]
        user_content = messages[1]["content"]
        self.assertNotIn("tried this before", user_content)

    def test_math_type_instruction_included(self):
        self.actor.generate_solution("What is 2+2?", task_type="math")
        call_args = self.actor._client.generate_with_history.call_args
        messages = call_args[0][0]
        user_content = messages[1]["content"]
        self.assertIn("arithmetic", user_content.lower())

    def test_code_type_instruction_included(self):
        self.actor.generate_solution("Write a function", task_type="code")
        call_args = self.actor._client.generate_with_history.call_args
        messages = call_args[0][0]
        user_content = messages[1]["content"]
        self.assertIn("Python function", user_content)

    def test_format_task_prompt_unknown_type(self):
        prompt = self.actor._format_task_prompt("some task", "unknown_type")
        self.assertIn("some task", prompt)

    def test_returns_llm_response(self):
        result = self.actor.generate_solution("Q?")
        self.assertEqual(result, "FINAL ANSWER: 42")


if __name__ == "__main__":
    unittest.main()
