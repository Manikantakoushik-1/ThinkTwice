"""Tests for the real-world task loader."""

from __future__ import annotations

import unittest

from src.tasks.real_world import RealWorldTaskLoader, _CATEGORY_TASK_TYPES
from src.tasks.base_task import Task


class TestRealWorldTaskLoader(unittest.TestCase):

    def test_load_all_tasks_returns_tasks(self):
        tasks = RealWorldTaskLoader.load_all_tasks()
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0)
        for t in tasks:
            self.assertIsInstance(t, Task)

    def test_all_tasks_have_required_fields(self):
        for task in RealWorldTaskLoader.load_all_tasks():
            self.assertTrue(task.id, f"Task missing id: {task}")
            self.assertTrue(task.description, f"Task missing description: {task.id}")
            self.assertIn(task.task_type, ("math", "code", "logic"),
                          f"Unexpected task_type for {task.id}")
            self.assertIn("category", task.metadata,
                          f"Task {task.id} missing category metadata")

    def test_category_filter_algorithms(self):
        loader = RealWorldTaskLoader(category="algorithms")
        tasks = loader.load_tasks()
        self.assertGreater(len(tasks), 0)
        for t in tasks:
            self.assertEqual(t.task_type, "code")
            self.assertEqual(t.metadata["category"], "algorithms")

    def test_category_filter_data_science(self):
        loader = RealWorldTaskLoader(category="data_science")
        tasks = loader.load_tasks()
        self.assertGreater(len(tasks), 0)
        for t in tasks:
            self.assertEqual(t.task_type, "math")

    def test_category_filter_system_design(self):
        loader = RealWorldTaskLoader(category="system_design")
        tasks = loader.load_tasks()
        self.assertGreater(len(tasks), 0)
        for t in tasks:
            self.assertEqual(t.task_type, "logic")

    def test_category_filter_debugging(self):
        loader = RealWorldTaskLoader(category="debugging")
        tasks = loader.load_tasks()
        self.assertGreater(len(tasks), 0)
        for t in tasks:
            self.assertEqual(t.task_type, "code")
            self.assertIsNotNone(t.test_code, f"Debugging task {t.id} missing test_code")

    def test_category_filter_business(self):
        loader = RealWorldTaskLoader(category="business")
        tasks = loader.load_tasks()
        self.assertGreater(len(tasks), 0)
        for t in tasks:
            self.assertEqual(t.task_type, "math")

    def test_no_category_returns_all(self):
        all_via_none = RealWorldTaskLoader().load_tasks()
        all_via_classmethod = RealWorldTaskLoader.load_all_tasks()
        self.assertEqual(len(all_via_none), len(all_via_classmethod))

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            RealWorldTaskLoader(category="nonexistent")

    def test_get_task_type_single_category(self):
        for cat, expected_type in _CATEGORY_TASK_TYPES.items():
            loader = RealWorldTaskLoader(category=cat)
            self.assertEqual(loader.get_task_type(), expected_type)

    def test_get_task_type_mixed(self):
        loader = RealWorldTaskLoader()
        self.assertEqual(loader.get_task_type(), "mixed")

    def test_code_tasks_have_test_code(self):
        for task in RealWorldTaskLoader.load_all_tasks():
            if task.task_type == "code":
                self.assertIsNotNone(task.test_code,
                                     f"Code task {task.id} missing test_code")
                self.assertIn("print('All tests passed!')", task.test_code,
                               f"Code task {task.id} test_code missing success print")

    def test_math_tasks_have_expected_answer(self):
        for task in RealWorldTaskLoader.load_all_tasks():
            if task.task_type == "math":
                self.assertIsNotNone(task.expected_answer,
                                     f"Math task {task.id} missing expected_answer")

    def test_categories_constant(self):
        self.assertEqual(
            sorted(RealWorldTaskLoader.CATEGORIES),
            sorted(["data_science", "algorithms", "system_design", "debugging", "business"]),
        )

    def test_task_ids_unique(self):
        tasks = RealWorldTaskLoader.load_all_tasks()
        ids = [t.id for t in tasks]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate task IDs found")


class TestMathTaskLoaderExtended(unittest.TestCase):
    """Verify the new harder math tasks were added to math_reasoning.py."""

    def test_ten_math_tasks_loaded(self):
        from src.tasks.math_reasoning import MathTaskLoader
        tasks = MathTaskLoader().load_tasks()
        self.assertEqual(len(tasks), 10, "Expected exactly 10 math tasks")

    def test_new_sequential_discount_task(self):
        from src.tasks.math_reasoning import MathTaskLoader
        tasks = {t.id: t for t in MathTaskLoader().load_tasks()}
        self.assertIn("math_006", tasks)
        self.assertEqual(tasks["math_006"].expected_answer, "3")

    def test_new_growth_decline_task(self):
        from src.tasks.math_reasoning import MathTaskLoader
        tasks = {t.id: t for t in MathTaskLoader().load_tasks()}
        self.assertIn("math_009", tasks)
        self.assertEqual(tasks["math_009"].expected_answer, "1152000")


class TestCodeTaskLoaderExtended(unittest.TestCase):
    """Verify the new interview-level code tasks were added."""

    def test_seven_code_tasks_loaded(self):
        from src.tasks.code_generation import CodeTaskLoader
        tasks = CodeTaskLoader().load_tasks()
        self.assertEqual(len(tasks), 7, "Expected exactly 7 code tasks")

    def test_two_sum_task_present(self):
        from src.tasks.code_generation import CodeTaskLoader
        tasks = {t.id: t for t in CodeTaskLoader().load_tasks()}
        self.assertIn("code_004", tasks)
        self.assertIsNotNone(tasks["code_004"].test_code)

    def test_valid_brackets_task_present(self):
        from src.tasks.code_generation import CodeTaskLoader
        tasks = {t.id: t for t in CodeTaskLoader().load_tasks()}
        self.assertIn("code_005", tasks)

    def test_merge_sorted_arrays_task_present(self):
        from src.tasks.code_generation import CodeTaskLoader
        tasks = {t.id: t for t in CodeTaskLoader().load_tasks()}
        self.assertIn("code_006", tasks)

    def test_run_length_encode_task_present(self):
        from src.tasks.code_generation import CodeTaskLoader
        tasks = {t.id: t for t in CodeTaskLoader().load_tasks()}
        self.assertIn("code_007", tasks)


if __name__ == "__main__":
    unittest.main()
