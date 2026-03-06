"""Integration tests for the ReflexionAgent."""

import unittest
from unittest.mock import MagicMock, patch

from src.agent.reflexion_agent import ReflexionAgent, AgentResult


def _make_agent(max_attempts=3):
    mock_client = MagicMock()
    mock_client.total_tokens_used = 0
    return ReflexionAgent(llm_client=mock_client, max_attempts=max_attempts)


class TestReflexionAgentSolve(unittest.TestCase):

    @patch("src.agent.actor.Actor.generate_solution", return_value="FINAL ANSWER: 42")
    @patch(
        "src.agent.evaluator.Evaluator.evaluate",
        return_value={"is_correct": True, "score": 1.0, "feedback": "Correct!", "errors": []},
    )
    def test_solve_succeeds_first_attempt(self, mock_eval, mock_actor):
        agent = _make_agent()
        result = agent.solve("t1", "What is 6*7?", expected_answer="42", task_type="math")
        self.assertIsInstance(result, AgentResult)
        self.assertTrue(result.is_correct)
        self.assertEqual(result.attempts, 1)

    @patch("src.agent.actor.Actor.generate_solution", return_value="FINAL ANSWER: 99")
    @patch(
        "src.agent.evaluator.Evaluator.evaluate",
        return_value={"is_correct": False, "score": 0.0, "feedback": "Wrong!", "errors": ["wrong_answer"]},
    )
    @patch(
        "src.agent.reflector.Reflector.reflect",
        return_value={
            "what_went_wrong": "used wrong formula",
            "root_cause": "misread",
            "key_insight": "read more carefully",
            "strategy": "start over",
            "full_text": "...",
        },
    )
    def test_solve_exhausts_max_attempts(self, mock_reflect, mock_eval, mock_actor):
        agent = _make_agent(max_attempts=3)
        result = agent.solve("t2", "A hard problem", expected_answer="42", task_type="math")
        self.assertFalse(result.is_correct)
        self.assertEqual(result.attempts, 3)
        # Reflector should have been called twice (after attempt 1 and 2)
        self.assertEqual(mock_reflect.call_count, 2)

    @patch("src.agent.actor.Actor.generate_solution", return_value="FINAL ANSWER: 42")
    @patch(
        "src.agent.evaluator.Evaluator.evaluate",
        side_effect=[
            {"is_correct": False, "score": 0.0, "feedback": "Wrong", "errors": []},
            {"is_correct": True, "score": 1.0, "feedback": "Correct!", "errors": []},
        ],
    )
    @patch(
        "src.agent.reflector.Reflector.reflect",
        return_value={
            "what_went_wrong": "x",
            "root_cause": "y",
            "key_insight": "z",
            "strategy": "w",
            "full_text": "...",
        },
    )
    def test_solve_succeeds_on_second_attempt(self, mock_reflect, mock_eval, mock_actor):
        agent = _make_agent(max_attempts=3)
        result = agent.solve("t3", "Problem", expected_answer="42", task_type="math")
        self.assertTrue(result.is_correct)
        self.assertEqual(result.attempts, 2)
        self.assertEqual(mock_reflect.call_count, 1)

    def test_reset_clears_memory(self):
        agent = _make_agent()
        agent.reset()
        stats = agent._memory.get_stats()
        self.assertEqual(stats["total_reflections"], 0)

    @patch("src.agent.actor.Actor.generate_solution", return_value="FINAL ANSWER: 1")
    @patch(
        "src.agent.evaluator.Evaluator.evaluate",
        return_value={"is_correct": True, "score": 1.0, "feedback": "OK", "errors": []},
    )
    def test_solve_batch(self, mock_eval, mock_actor):
        agent = _make_agent()
        tasks = [
            {"id": "b1", "description": "task 1", "expected_answer": "1"},
            {"id": "b2", "description": "task 2", "expected_answer": "2"},
        ]
        results = agent.solve_batch(tasks, task_type="math")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.is_correct for r in results))


if __name__ == "__main__":
    unittest.main()
