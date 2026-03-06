"""Code generation task loader — HumanEval-style Python coding problems."""

from __future__ import annotations

from src.tasks.base_task import Task, TaskLoader

# ── Built-in HumanEval-style samples ─────────────────────────────────────────

_BUILTIN_TASKS = [
    {
        "id": "code_001",
        "description": (
            "Write a Python function `has_close_elements(numbers: list[float], threshold: float) -> bool` "
            "that checks whether any two numbers in the list are closer to each other than the given "
            "threshold. Return True if such a pair exists, False otherwise.\n\n"
            "Example: has_close_elements([1.0, 2.0, 3.0], 0.5) -> False\n"
            "Example: has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) -> True"
        ),
        "test_code": (
            "assert has_close_elements([1.0, 2.0, 3.0], 0.5) == False\n"
            "assert has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == True\n"
            "assert has_close_elements([1.0, 2.0, 3.0], 2.0) == True\n"
            "assert has_close_elements([], 0.5) == False\n"
            "assert has_close_elements([1.0], 0.5) == False\n"
            "print('All tests passed!')"
        ),
    },
    {
        "id": "code_002",
        "description": (
            "Write a Python function `separate_paren_groups(paren_string: str) -> list[str]` "
            "that takes a string of multiple groups of nested parentheses separated by spaces "
            "and returns a list of separate parenthesis groups. Each group is balanced and not "
            "nested within each other. Ignore any spaces in the input.\n\n"
            "Example: separate_paren_groups('( ) (( )) (( )( ))') -> ['()', '(())', '(()())']"
        ),
        "test_code": (
            "assert separate_paren_groups('( ) (( )) (( )( ))') == ['()', '(())', '(()())']\n"
            "assert separate_paren_groups('( ) ( ) ( ) ( )') == ['()', '()', '()', '()']\n"
            "assert separate_paren_groups('((()))') == ['((()))']\n"
            "print('All tests passed!')"
        ),
    },
    {
        "id": "code_003",
        "description": (
            "Write a Python function `truncate_number(number: float) -> float` "
            "that takes a positive floating point number and returns the decimal fractional part "
            "(i.e. the part after the decimal point).\n\n"
            "Example: truncate_number(3.5) -> 0.5"
        ),
        "test_code": (
            "assert abs(truncate_number(3.5) - 0.5) < 1e-9\n"
            "assert abs(truncate_number(1.25) - 0.25) < 1e-9\n"
            "assert abs(truncate_number(123.456) - 0.456) < 1e-6\n"
            "assert abs(truncate_number(1.0) - 0.0) < 1e-9\n"
            "print('All tests passed!')"
        ),
    },
]


class CodeTaskLoader(TaskLoader):
    """Loader for HumanEval-style Python coding tasks."""

    def get_task_type(self) -> str:
        return "code"

    def load_tasks(self) -> list[Task]:
        return [
            Task(
                id=t["id"],
                description=t["description"],
                expected_answer=None,
                task_type="code",
                test_code=t["test_code"],
            )
            for t in _BUILTIN_TASKS
        ]
