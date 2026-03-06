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
    # ── Interview-level tasks ─────────────────────────────────────────────
    {
        "id": "code_004",
        "description": (
            "Write a Python function `two_sum(nums: list[int], target: int) -> list[int]` "
            "that returns the indices of the two numbers in `nums` that add up to `target`. "
            "You may assume exactly one valid solution exists and you may not use the same "
            "element twice.\n\n"
            "Your solution must run in O(n) time using a hash map.\n\n"
            "Example:\n"
            "  two_sum([2, 7, 11, 15], 9) -> [0, 1]\n"
            "  two_sum([3, 2, 4], 6) -> [1, 2]"
        ),
        "test_code": (
            "assert two_sum([2, 7, 11, 15], 9) == [0, 1]\n"
            "assert two_sum([3, 2, 4], 6) == [1, 2]\n"
            "assert two_sum([3, 3], 6) == [0, 1]\n"
            "assert two_sum([1, 2, 3, 5], 8) == [2, 3]\n"
            "# Verify indices are distinct\n"
            "result = two_sum([3, 3], 6)\n"
            "assert result[0] != result[1], 'Must not reuse same index'\n"
            "print('All tests passed!')"
        ),
    },
    {
        "id": "code_005",
        "description": (
            "Write a Python function `is_valid_brackets(s: str) -> bool` that checks whether "
            "the input string of brackets is valid. "
            "The string contains only '(', ')', '{', '}', '[', ']'.\n\n"
            "Rules:\n"
            "  1. Every opening bracket must be closed by the same type.\n"
            "  2. Brackets must be closed in the correct (LIFO) order.\n"
            "  3. Every closing bracket must have a matching open bracket.\n\n"
            "Example:\n"
            "  is_valid_brackets('()[]{}') -> True\n"
            "  is_valid_brackets('([)]') -> False\n"
            "  is_valid_brackets('{[]}') -> True"
        ),
        "test_code": (
            "assert is_valid_brackets('()') == True\n"
            "assert is_valid_brackets('()[]{}') == True\n"
            "assert is_valid_brackets('(]') == False\n"
            "assert is_valid_brackets('([)]') == False\n"
            "assert is_valid_brackets('{[]}') == True\n"
            "assert is_valid_brackets('') == True\n"
            "assert is_valid_brackets(']') == False\n"
            "assert is_valid_brackets('((') == False\n"
            "assert is_valid_brackets('(({}[]))') == True\n"
            "print('All tests passed!')"
        ),
    },
    {
        "id": "code_006",
        "description": (
            "Write a Python function `merge_sorted_arrays(nums1: list[int], m: int, "
            "nums2: list[int], n: int) -> None` that merges `nums2` into `nums1` "
            "in-place. `nums1` has length `m + n`, with the last `n` slots initialised "
            "to 0 (they are placeholders). Both arrays are sorted in non-decreasing order.\n\n"
            "The function must modify `nums1` in-place (no return value) and must not "
            "use extra arrays.\n\n"
            "Example:\n"
            "  nums1 = [1, 2, 3, 0, 0, 0]; nums2 = [2, 5, 6]; m = 3; n = 3\n"
            "  merge_sorted_arrays(nums1, 3, nums2, 3)\n"
            "  # nums1 is now [1, 2, 2, 3, 5, 6]"
        ),
        "test_code": (
            "nums1 = [1, 2, 3, 0, 0, 0]\n"
            "merge_sorted_arrays(nums1, 3, [2, 5, 6], 3)\n"
            "assert nums1 == [1, 2, 2, 3, 5, 6], f'Got {nums1}'\n"
            "nums1 = [1]\n"
            "merge_sorted_arrays(nums1, 1, [], 0)\n"
            "assert nums1 == [1]\n"
            "nums1 = [0]\n"
            "merge_sorted_arrays(nums1, 0, [1], 1)\n"
            "assert nums1 == [1], f'Got {nums1}'\n"
            "nums1 = [4, 5, 6, 0, 0, 0]\n"
            "merge_sorted_arrays(nums1, 3, [1, 2, 3], 3)\n"
            "assert nums1 == [1, 2, 3, 4, 5, 6], f'Got {nums1}'\n"
            "print('All tests passed!')"
        ),
    },
    {
        "id": "code_007",
        "description": (
            "Write a Python function `run_length_encode(s: str) -> str` that compresses "
            "a string using run-length encoding: consecutive duplicate characters are "
            "replaced with the character followed by its count. "
            "If the encoded result is NOT shorter than the original, return the original.\n\n"
            "Example:\n"
            "  run_length_encode('aabcccdddd') -> 'a2b1c3d4'\n"
            "  run_length_encode('abc') -> 'abc'  # 'a1b1c1' is longer\n"
            "  run_length_encode('aabb') -> 'aabb'  # 'a2b2' same length"
        ),
        "test_code": (
            "assert run_length_encode('aabcccdddd') == 'a2b1c3d4'\n"
            "assert run_length_encode('abc') == 'abc'\n"
            "assert run_length_encode('aabb') == 'aabb'\n"
            "assert run_length_encode('') == ''\n"
            "assert run_length_encode('aaaa') == 'a4'\n"
            "assert run_length_encode('aaabbbccc') == 'a3b3c3'\n"
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
