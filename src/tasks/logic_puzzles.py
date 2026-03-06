"""Logic puzzle task loader — classic constraint-satisfaction puzzles."""

from __future__ import annotations

from src.tasks.base_task import Task, TaskLoader

_BUILTIN_TASKS = [
    {
        "id": "logic_001",
        "description": (
            "You have three boxes labeled 'Apples', 'Oranges', and 'Apples & Oranges'. "
            "All three labels are WRONG. You may pick one fruit from one box (without "
            "looking inside). Which box should you pick from, and what does each box "
            "actually contain?\n\n"
            "Think step by step, considering every constraint."
        ),
        "expected_answer": (
            "Pick from 'Apples & Oranges'. "
            "If you draw an apple, that box is Apples; the box labeled 'Apples' must be "
            "Oranges; and 'Oranges' must be Apples & Oranges. Vice versa for orange."
        ),
    },
    {
        "id": "logic_002",
        "description": (
            "A farmer needs to cross a river with a wolf, a goat, and a cabbage. "
            "The boat can carry the farmer and one other item. "
            "The wolf will eat the goat if left alone together. "
            "The goat will eat the cabbage if left alone together. "
            "Describe a sequence of crossings that gets all three safely to the other side."
        ),
        "expected_answer": (
            "1. Farmer takes goat across. "
            "2. Farmer returns alone. "
            "3. Farmer takes wolf (or cabbage) across. "
            "4. Farmer returns with goat. "
            "5. Farmer takes cabbage (or wolf) across. "
            "6. Farmer returns alone. "
            "7. Farmer takes goat across."
        ),
    },
    {
        "id": "logic_003",
        "description": (
            "You have 8 balls that look identical. One ball is slightly heavier than the "
            "others. You have a balance scale and can use it only twice. "
            "How do you find the heavier ball in exactly 2 weighings?"
        ),
        "expected_answer": (
            "Divide into groups of 3, 3, and 2. "
            "Weighing 1: Compare the two groups of 3. "
            "If balanced, the heavy ball is in the group of 2 — weigh those two to find it. "
            "If unbalanced, take the heavier group of 3 and weigh any two of them; "
            "if balanced the third is heavy, otherwise the heavier side contains it."
        ),
    },
]


class LogicTaskLoader(TaskLoader):
    """Loader for classic logic puzzles."""

    def get_task_type(self) -> str:
        return "logic"

    def load_tasks(self) -> list[Task]:
        return [
            Task(
                id=t["id"],
                description=t["description"],
                expected_answer=t["expected_answer"],
                task_type="logic",
            )
            for t in _BUILTIN_TASKS
        ]
