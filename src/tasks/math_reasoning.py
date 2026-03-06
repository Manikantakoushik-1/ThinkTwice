"""Math reasoning task loader — GSM8K-style word problems."""

from __future__ import annotations

import json
import os
import re

from src.tasks.base_task import Task, TaskLoader

# ── Built-in GSM8K-style samples ─────────────────────────────────────────────

_BUILTIN_TASKS = [
    {
        "id": "math_001",
        "description": (
            "Janet's ducks lay 16 eggs per day. She eats 3 for breakfast every morning "
            "and bakes muffins for her friends every day with 4. She sells the remainder "
            "at the farmers' market daily for $2 per fresh duck egg. "
            "How much in dollars does she make every day at the farmers' market?"
        ),
        "expected_answer": "18",
    },
    {
        "id": "math_002",
        "description": (
            "A robe takes 2 bolts of blue fiber and half that much white fiber. "
            "How many bolts in total does it take?"
        ),
        "expected_answer": "3",
    },
    {
        "id": "math_003",
        "description": (
            "Josh decides to try flipping a house. He buys a house for $80,000 and then "
            "puts in $50,000 in repairs. This increased the value of the house by 150%. "
            "How much profit did he make?"
        ),
        "expected_answer": "70000",
    },
    {
        "id": "math_004",
        "description": (
            "James decides to run 3 sprints 3 times a week. He runs 60 meters each sprint. "
            "How many total meters does he run a week?"
        ),
        "expected_answer": "540",
    },
    {
        "id": "math_005",
        "description": (
            "Wendi brought home 4 chickens. After a few days, she brought home enough "
            "additional chickens to double the number of chickens she owned. Then, a "
            "neighbor's dog ate one of her chickens. Finally, Wendi found an additional "
            "3 chickens wandering around her yard and added those to her flock. "
            "How many chickens does Wendi have now?"
        ),
        "expected_answer": "10",
    },
]


class MathTaskLoader(TaskLoader):
    """Loader for GSM8K-style math problems.

    Loads built-in samples by default; can also load from a JSONL file where
    each line has ``question`` and ``answer`` fields (GSM8K format uses
    ``#### <number>`` at the end of the answer).

    Args:
        jsonl_path: Optional path to a ``.jsonl`` file to load instead of built-ins.
    """

    def __init__(self, jsonl_path: str | None = None) -> None:
        self._jsonl_path = jsonl_path

    def get_task_type(self) -> str:
        return "math"

    def load_tasks(self) -> list[Task]:
        if self._jsonl_path and os.path.isfile(self._jsonl_path):
            return self._load_from_jsonl(self._jsonl_path)
        return [
            Task(
                id=t["id"],
                description=t["description"],
                expected_answer=t["expected_answer"],
                task_type="math",
            )
            for t in _BUILTIN_TASKS
        ]

    # ── JSONL loader ──────────────────────────────────────────────────────────

    @staticmethod
    def _load_from_jsonl(path: str) -> list[Task]:
        tasks: list[Task] = []
        with open(path, encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                question = record.get("question", "")
                raw_answer = record.get("answer", "")
                expected = MathTaskLoader._extract_gsm8k_answer(raw_answer)
                tasks.append(
                    Task(
                        id=f"gsm8k_{idx:04d}",
                        description=question,
                        expected_answer=expected,
                        task_type="math",
                    )
                )
        return tasks

    @staticmethod
    def _extract_gsm8k_answer(answer_text: str) -> str:
        """Extract the numeric answer after '####' in GSM8K format."""
        match = re.search(r"####\s*(-?\d[\d,]*(?:\.\d+)?)", answer_text)
        if match:
            return match.group(1).replace(",", "")
        return answer_text.strip()
