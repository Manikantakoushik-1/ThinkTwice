"""Tests for EpisodicMemory."""

import unittest

from src.memory.episodic_memory import EpisodicMemory, Reflection


def _make_reflection(task_id: str, attempt: int, success: bool = False) -> Reflection:
    return Reflection(
        task_id=task_id,
        attempt_number=attempt,
        action_taken=f"action_{attempt}",
        outcome=f"outcome_{attempt}",
        reflection_text=f"reflection_text_{attempt}",
        key_insight=f"insight_{attempt}",
        success=success,
    )


class TestEpisodicMemory(unittest.TestCase):

    def setUp(self):
        self.memory = EpisodicMemory(max_reflections_per_task=5)

    def test_add_and_retrieve_reflection(self):
        r = _make_reflection("task_1", 1)
        self.memory.add_reflection(r)
        reflections = self.memory.get_reflections("task_1")
        self.assertEqual(len(reflections), 1)
        self.assertEqual(reflections[0].task_id, "task_1")
        self.assertEqual(reflections[0].attempt_number, 1)

    def test_get_reflections_empty(self):
        self.assertEqual(self.memory.get_reflections("nonexistent"), [])

    def test_get_latest_reflection(self):
        self.memory.add_reflection(_make_reflection("task_1", 1))
        self.memory.add_reflection(_make_reflection("task_1", 2))
        latest = self.memory.get_latest_reflection("task_1")
        self.assertIsNotNone(latest)
        self.assertEqual(latest.attempt_number, 2)

    def test_get_latest_reflection_empty(self):
        self.assertIsNone(self.memory.get_latest_reflection("nonexistent"))

    def test_max_reflections_cap(self):
        memory = EpisodicMemory(max_reflections_per_task=3)
        for i in range(1, 6):
            memory.add_reflection(_make_reflection("task_1", i))
        reflections = memory.get_reflections("task_1")
        self.assertEqual(len(reflections), 3)
        # Should keep the most recent ones
        self.assertEqual(reflections[-1].attempt_number, 5)

    def test_format_reflections_for_prompt_empty(self):
        result = self.memory.format_reflections_for_prompt("task_1")
        self.assertEqual(result, "")

    def test_format_reflections_for_prompt(self):
        self.memory.add_reflection(_make_reflection("task_1", 1))
        self.memory.add_reflection(_make_reflection("task_1", 2, success=True))
        result = self.memory.format_reflections_for_prompt("task_1")
        self.assertIn("Previous Attempts", result)
        self.assertIn("Attempt 1", result)
        self.assertIn("Attempt 2", result)
        self.assertIn("insight_1", result)
        self.assertIn("✓", result)
        self.assertIn("✗", result)

    def test_get_all_insights(self):
        self.memory.add_reflection(_make_reflection("task_1", 1))
        self.memory.add_reflection(_make_reflection("task_1", 2))
        insights = self.memory.get_all_insights("task_1")
        self.assertEqual(insights, ["insight_1", "insight_2"])

    def test_clear_specific_task(self):
        self.memory.add_reflection(_make_reflection("task_1", 1))
        self.memory.add_reflection(_make_reflection("task_2", 1))
        self.memory.clear("task_1")
        self.assertEqual(self.memory.get_reflections("task_1"), [])
        self.assertEqual(len(self.memory.get_reflections("task_2")), 1)

    def test_clear_all(self):
        self.memory.add_reflection(_make_reflection("task_1", 1))
        self.memory.add_reflection(_make_reflection("task_2", 1))
        self.memory.clear()
        self.assertEqual(self.memory.get_stats()["total_reflections"], 0)

    def test_get_stats(self):
        self.memory.add_reflection(_make_reflection("task_1", 1, success=False))
        self.memory.add_reflection(_make_reflection("task_1", 2, success=True))
        self.memory.add_reflection(_make_reflection("task_2", 1, success=False))
        stats = self.memory.get_stats()
        self.assertEqual(stats["total_tasks"], 2)
        self.assertEqual(stats["total_reflections"], 3)
        self.assertEqual(stats["total_successes"], 1)


if __name__ == "__main__":
    unittest.main()
