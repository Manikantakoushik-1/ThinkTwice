"""Real-world task loader — practical, interview-impressive problems.

Organised into five categories that demonstrate the value of the
Reflexion loop on problems where LLMs commonly fail on the first
attempt:

    * data_science  — statistical / growth calculations
    * algorithms    — coding-interview classics
    * system_design — architecture reasoning
    * debugging     — bug-fix tasks
    * business      — finance / compound-growth maths
"""

from __future__ import annotations

from src.tasks.base_task import Task, TaskLoader

# ── Data-science / analytics tasks (task_type="math") ─────────────────────

_DATA_SCIENCE_TASKS = [
    {
        "id": "rw_ds_001",
        "description": (
            "A startup has 10,000 users growing at 15% month-over-month. "
            "They have $500,000 in runway and are burning $50,000/month, "
            "with costs also growing at 5%/month. "
            "How many complete months until they run out of money? "
            "(Assume costs are paid at the start of each month and growth "
            "is applied at the end.)\n\n"
            "Show your month-by-month calculation and state the final answer as an integer."
        ),
        "expected_answer": "8",
        "category": "data_science",
    },
    {
        "id": "rw_ds_002",
        "description": (
            "An A/B test ran for two weeks:\n"
            "  • Control:   10,000 visitors, 420 conversions\n"
            "  • Treatment: 10,000 visitors, 480 conversions\n\n"
            "1. What is the absolute improvement in conversion rate (in percentage points)?\n"
            "2. What is the relative improvement (as a percentage)?\n\n"
            "Give the FINAL ANSWER as the relative improvement percentage, "
            "rounded to one decimal place."
        ),
        "expected_answer": "14.3",
        "category": "data_science",
    },
    {
        "id": "rw_ds_003",
        "description": (
            "A data pipeline processes 1,000,000 events per day. "
            "Each event is 512 bytes. "
            "You store raw events for 30 days and then delete them. "
            "You also keep a 1% sample permanently (forever), "
            "and after 30 days you aggregate to hourly summaries at 200 bytes each.\n\n"
            "How many GB of storage do you need after exactly 90 days of operation? "
            "(1 GB = 1,000,000,000 bytes). "
            "Round to one decimal place and state as the FINAL ANSWER."
        ),
        "expected_answer": "15.8",
        "category": "data_science",
    },
    {
        "id": "rw_ds_004",
        "description": (
            "A model has 95% accuracy on a dataset where 2% of samples are positive. "
            "The model flags every sample as negative (always predicts 0). "
            "What is the model's precision for the positive class? "
            "Express as a percentage and state as the FINAL ANSWER."
        ),
        "expected_answer": "0",
        "category": "data_science",
    },
]

# ── Algorithm & data-structure tasks (task_type="code") ────────────────────

_ALGORITHM_TASKS = [
    {
        "id": "rw_algo_001",
        "description": (
            "Implement an LRU (Least Recently Used) Cache in Python.\n\n"
            "Create a class `LRUCache` with:\n"
            "  • `__init__(self, capacity: int)` — initialise with given capacity\n"
            "  • `get(self, key: int) -> int` — return value or -1 if key not present\n"
            "  • `put(self, key: int, value: int) -> None` — insert/update; evict LRU "
            "entry if at capacity\n\n"
            "Both operations must run in O(1) average time.\n\n"
            "Example:\n"
            "  cache = LRUCache(2)\n"
            "  cache.put(1, 1)   # cache is {1:1}\n"
            "  cache.put(2, 2)   # cache is {1:1, 2:2}\n"
            "  cache.get(1)      # returns 1\n"
            "  cache.put(3, 3)   # evicts key 2, cache is {1:1, 3:3}\n"
            "  cache.get(2)      # returns -1 (not found)"
        ),
        "test_code": (
            "cache = LRUCache(2)\n"
            "cache.put(1, 1)\n"
            "cache.put(2, 2)\n"
            "assert cache.get(1) == 1\n"
            "cache.put(3, 3)\n"
            "assert cache.get(2) == -1\n"
            "cache.put(4, 4)\n"
            "assert cache.get(1) == -1\n"
            "assert cache.get(3) == 3\n"
            "assert cache.get(4) == 4\n"
            "# Edge: capacity 1\n"
            "c1 = LRUCache(1)\n"
            "c1.put(2, 1)\n"
            "assert c1.get(2) == 1\n"
            "c1.put(3, 2)\n"
            "assert c1.get(2) == -1\n"
            "assert c1.get(3) == 2\n"
            "print('All tests passed!')"
        ),
        "category": "algorithms",
    },
    {
        "id": "rw_algo_002",
        "description": (
            "Write a Python function `merge_intervals(intervals: list[list[int]]) -> list[list[int]]` "
            "that merges all overlapping intervals and returns the result sorted.\n\n"
            "Example:\n"
            "  merge_intervals([[1,3],[2,6],[8,10],[15,18]]) -> [[1,6],[8,10],[15,18]]\n"
            "  merge_intervals([[1,4],[4,5]]) -> [[1,5]]\n\n"
            "Handle the empty list case. Intervals may be given in any order."
        ),
        "test_code": (
            "assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]\n"
            "assert merge_intervals([[1,4],[4,5]]) == [[1,5]]\n"
            "assert merge_intervals([]) == []\n"
            "assert merge_intervals([[1,4]]) == [[1,4]]\n"
            "assert merge_intervals([[1,4],[2,3]]) == [[1,4]]\n"
            "assert merge_intervals([[5,6],[1,2],[3,4]]) == [[1,2],[3,4],[5,6]]\n"
            "assert merge_intervals([[1,10],[2,3],[4,5]]) == [[1,10]]\n"
            "print('All tests passed!')"
        ),
        "category": "algorithms",
    },
    {
        "id": "rw_algo_003",
        "description": (
            "Write a Python function `is_valid(s: str) -> bool` that determines whether a "
            "string of brackets is valid. The string may contain '(', ')', '{', '}', '[', ']'.\n\n"
            "A string is valid if:\n"
            "  1. Open brackets are closed by the same type.\n"
            "  2. Open brackets are closed in the correct order.\n"
            "  3. Every close bracket has a corresponding open bracket.\n\n"
            "Example:\n"
            "  is_valid('()') -> True\n"
            "  is_valid('()[]{}') -> True\n"
            "  is_valid('(]') -> False\n"
            "  is_valid('([)]') -> False\n"
            "  is_valid('{[]}') -> True"
        ),
        "test_code": (
            "assert is_valid('()') == True\n"
            "assert is_valid('()[]{}') == True\n"
            "assert is_valid('(]') == False\n"
            "assert is_valid('([)]') == False\n"
            "assert is_valid('{[]}') == True\n"
            "assert is_valid('') == True\n"
            "assert is_valid(']') == False\n"
            "assert is_valid('((') == False\n"
            "assert is_valid('(({}[]))') == True\n"
            "print('All tests passed!')"
        ),
        "category": "algorithms",
    },
    {
        "id": "rw_algo_004",
        "description": (
            "Write a Python function `compress(s: str) -> str` that performs run-length "
            "encoding on a string: consecutive duplicate characters are replaced by the "
            "character followed by the count. If the compressed string is not shorter than "
            "the original, return the original string unchanged.\n\n"
            "Example:\n"
            "  compress('aabcccdddd') -> 'a2b1c3d4'\n"
            "  compress('abc') -> 'abc'  (compressed 'a1b1c1' is longer)\n"
            "  compress('aabb') -> 'aabb'  (compressed 'a2b2' is same length, return original)"
        ),
        "test_code": (
            "assert compress('aabcccdddd') == 'a2b1c3d4'\n"
            "assert compress('abc') == 'abc'\n"
            "assert compress('aabb') == 'aabb'\n"
            "assert compress('') == ''\n"
            "assert compress('aaaa') == 'a4'\n"
            "assert compress('aabbccdd') == 'aabbccdd'\n"
            "assert compress('aaabbbccc') == 'a3b3c3'\n"
            "print('All tests passed!')"
        ),
        "category": "algorithms",
    },
]

# ── System-design / architecture tasks (task_type="logic") ─────────────────

_SYSTEM_DESIGN_TASKS = [
    {
        "id": "rw_sd_001",
        "description": (
            "You are designing a URL shortener (like bit.ly) that must handle:\n"
            "  • 100 million unique URLs stored\n"
            "  • 1 billion redirect requests per day\n"
            "  • < 10 ms p99 redirect latency\n\n"
            "Answer the following questions:\n"
            "1. Which data store(s) would you choose and why?\n"
            "2. What is the key schema (what maps to what)?\n"
            "3. What is the expected read/write ratio?\n"
            "4. How would you handle hot links (viral URLs)?\n\n"
            "Be specific about trade-offs."
        ),
        "expected_answer": (
            "A Redis or in-memory cache layer for hot links with a persistent store "
            "(e.g., Cassandra or DynamoDB) for durability. "
            "Schema: short_code -> original_url. "
            "Read/write ratio roughly 1000:1 (redirects vastly outnumber creations). "
            "Hot links cached with TTL or LFU eviction policy."
        ),
        "category": "system_design",
    },
    {
        "id": "rw_sd_002",
        "description": (
            "A production microservice system has three services in a call chain: "
            "A → B → C. Normally each service responds in ~50 ms. "
            "Service C's latency suddenly spikes to 5,000 ms (5 s).\n\n"
            "1. What happens to Services A and B's response times and thread pools?\n"
            "2. What is 'cascading failure' and why does it occur here?\n"
            "3. Name and explain THREE design patterns that would prevent or limit this failure.\n\n"
            "Your answer must name specific patterns (e.g., Circuit Breaker, Bulkhead, Timeout)."
        ),
        "expected_answer": (
            "B waits for C (5 s instead of 50 ms), so A waits for B. "
            "Thread pools at A and B exhaust as requests queue up — cascading failure. "
            "Preventative patterns: "
            "(1) Circuit Breaker — opens after N failures, failing fast; "
            "(2) Timeout — limits how long B waits for C; "
            "(3) Bulkhead — isolates thread pools so C's slowness doesn't exhaust A's pool."
        ),
        "category": "system_design",
    },
    {
        "id": "rw_sd_003",
        "description": (
            "You need to design the storage layer for a social-media feed (like Twitter's "
            "home timeline). Each user follows up to 2,000 accounts; the platform has "
            "200 million active users generating 500 million posts per day.\n\n"
            "Compare these two approaches:\n"
            "  • Fan-out on write: pre-compute each follower's feed at post time.\n"
            "  • Fan-out on read: compute the feed dynamically at read time.\n\n"
            "For each approach state: storage cost, read latency, write latency, and the "
            "class of users (celebrity vs. regular) where it breaks down. "
            "Which hybrid approach do real systems (Twitter/X) use and why?"
        ),
        "expected_answer": (
            "Fan-out on write: low read latency (pre-built), high write cost for celebrities "
            "(millions of followers). "
            "Fan-out on read: cheap writes but O(following_count) read latency. "
            "Hybrid: fan-out on write for regular users, fan-out on read for celebrities; "
            "merge at read time. Twitter uses this hybrid."
        ),
        "category": "system_design",
    },
]

# ── Debugging / code-review tasks (task_type="code") ───────────────────────

_DEBUGGING_TASKS = [
    {
        "id": "rw_dbg_001",
        "description": (
            "The following Python function is supposed to return the n-th Fibonacci number "
            "(0-indexed: fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, …) but contains a bug.\n\n"
            "```python\n"
            "def fib(n):\n"
            "    if n <= 1:\n"
            "        return n\n"
            "    a, b = 0, 1\n"
            "    for _ in range(n):   # bug is here\n"
            "        a, b = b, a + b\n"
            "    return a\n"
            "```\n\n"
            "Identify the bug and write a corrected version of `fib(n)` that passes all tests."
        ),
        "test_code": (
            "assert fib(0) == 0\n"
            "assert fib(1) == 1\n"
            "assert fib(2) == 1\n"
            "assert fib(3) == 2\n"
            "assert fib(4) == 3\n"
            "assert fib(5) == 5\n"
            "assert fib(10) == 55\n"
            "print('All tests passed!')"
        ),
        "category": "debugging",
    },
    {
        "id": "rw_dbg_002",
        "description": (
            "The function below is meant to find the two indices whose values sum to "
            "`target` (guaranteed to have exactly one solution), but it has a subtle bug "
            "that causes it to find the same element twice.\n\n"
            "```python\n"
            "def two_sum(nums, target):\n"
            "    seen = {}\n"
            "    for i, num in enumerate(nums):\n"
            "        complement = target - num\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[num] = i   # this line has the bug\n"  
            "    return []\n"
            "```\n\n"
            "Actually the function above is correct. Here is the BUGGY version:\n\n"
            "```python\n"
            "def two_sum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        for j in range(i, len(nums)):  # bug: j should start at i+1\n"
            "            if nums[i] + nums[j] == target:\n"
            "                return [i, j]\n"
            "    return []\n"
            "```\n\n"
            "Fix the bug and write a corrected `two_sum(nums, target)` function."
        ),
        "test_code": (
            "assert two_sum([2, 7, 11, 15], 9) == [0, 1]\n"
            "assert two_sum([3, 2, 4], 6) == [1, 2]\n"
            "assert two_sum([3, 3], 6) == [0, 1]\n"
            "assert two_sum([1, 2, 3, 5], 8) == [2, 3]\n"
            "# Ensure no index is reused\n"
            "result = two_sum([3, 3], 6)\n"
            "assert result[0] != result[1], 'Must not reuse same element'\n"
            "print('All tests passed!')"
        ),
        "category": "debugging",
    },
    {
        "id": "rw_dbg_003",
        "description": (
            "The following function is supposed to remove duplicates from a sorted list "
            "in-place and return the length of the unique section, but it has an "
            "off-by-one error.\n\n"
            "```python\n"
            "def remove_duplicates(nums):\n"
            "    if not nums:\n"
            "        return 0\n"
            "    k = 0\n"
            "    for i in range(1, len(nums)):\n"
            "        if nums[i] != nums[k]:\n"
            "            k += 1\n"
            "            nums[k] = nums[i]\n"
            "    return k   # off-by-one: should return k + 1\n"
            "```\n\n"
            "Fix the bug and write the corrected `remove_duplicates(nums)` function."
        ),
        "test_code": (
            "nums = [1, 1, 2]\n"
            "k = remove_duplicates(nums)\n"
            "assert k == 2, f'Expected 2, got {k}'\n"
            "assert nums[:k] == [1, 2]\n"
            "nums2 = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]\n"
            "k2 = remove_duplicates(nums2)\n"
            "assert k2 == 5, f'Expected 5, got {k2}'\n"
            "assert nums2[:k2] == [0, 1, 2, 3, 4]\n"
            "assert remove_duplicates([]) == 0\n"
            "assert remove_duplicates([1]) == 1\n"
            "print('All tests passed!')"
        ),
        "category": "debugging",
    },
]

# ── Real-world business / finance tasks (task_type="math") ─────────────────

_BUSINESS_TASKS = [
    {
        "id": "rw_biz_001",
        "description": (
            "You invest $10,000 at an annual interest rate of 6%, compounded monthly, "
            "and you add $200 at the end of every month.\n\n"
            "What is the total value of the investment after exactly 5 years (60 months)?\n\n"
            "Use the future-value formulas:\n"
            "  FV_principal  = P × (1 + r)^n\n"
            "  FV_payments   = PMT × [((1 + r)^n − 1) / r]\n"
            "where r = monthly rate = 0.06/12, n = 60.\n\n"
            "Round to the nearest dollar and state as the FINAL ANSWER."
        ),
        "expected_answer": "27443",
        "category": "business",
    },
    {
        "id": "rw_biz_002",
        "description": (
            "A US taxpayer has $85,000 of ordinary taxable income in 2024. "
            "Using the following simplified federal tax brackets (single filer):\n"
            "  • 10%  on income $0 – $11,600\n"
            "  • 12%  on income $11,601 – $47,150\n"
            "  • 22%  on income $47,151 – $100,525\n\n"
            "Calculate:\n"
            "1. The total federal income tax owed.\n"
            "2. The effective (average) tax rate as a percentage.\n\n"
            "State the total tax owed as an integer (rounded) as the FINAL ANSWER."
        ),
        "expected_answer": "13753",
        "category": "business",
    },
    {
        "id": "rw_biz_003",
        "description": (
            "A SaaS company has these metrics:\n"
            "  • Monthly Recurring Revenue (MRR): $120,000\n"
            "  • Monthly churn rate: 2%\n"
            "  • Customer Acquisition Cost (CAC): $500\n"
            "  • Average Revenue Per User (ARPU): $60/month\n\n"
            "Calculate:\n"
            "1. Customer Lifetime (in months) = 1 / churn_rate\n"
            "2. Lifetime Value (LTV) = ARPU × customer_lifetime\n"
            "3. LTV:CAC ratio\n\n"
            "State the LTV:CAC ratio rounded to one decimal place as the FINAL ANSWER."
        ),
        "expected_answer": "6.0",
        "category": "business",
    },
    {
        "id": "rw_biz_004",
        "description": (
            "An e-commerce store has a current conversion rate of 3.2% with 50,000 monthly "
            "visitors and an average order value of $75.\n\n"
            "A new checkout redesign increased conversions to 3.8%.\n\n"
            "Calculate:\n"
            "1. Monthly revenue before the redesign.\n"
            "2. Monthly revenue after the redesign.\n"
            "3. Additional monthly revenue generated by the redesign.\n\n"
            "State the additional monthly revenue (in whole dollars) as the FINAL ANSWER."
        ),
        "expected_answer": "22500",
        "category": "business",
    },
]

# ── Master registry ────────────────────────────────────────────────────────

_ALL_TASKS_BY_CATEGORY: dict[str, list[dict]] = {
    "data_science": _DATA_SCIENCE_TASKS,
    "algorithms": _ALGORITHM_TASKS,
    "system_design": _SYSTEM_DESIGN_TASKS,
    "debugging": _DEBUGGING_TASKS,
    "business": _BUSINESS_TASKS,
}

_CATEGORY_TASK_TYPES: dict[str, str] = {
    "data_science": "math",
    "algorithms": "code",
    "system_design": "logic",
    "debugging": "code",
    "business": "math",
}


def _build_task(raw: dict) -> Task:
    category = raw["category"]
    task_type = _CATEGORY_TASK_TYPES[category]
    return Task(
        id=raw["id"],
        description=raw["description"],
        expected_answer=raw.get("expected_answer"),
        task_type=task_type,
        test_code=raw.get("test_code"),
        metadata={"category": category},
    )


class RealWorldTaskLoader(TaskLoader):
    """Loader for real-world, interview-impressive tasks.

    Args:
        category: Optional filter — one of ``'data_science'``, ``'algorithms'``,
            ``'system_design'``, ``'debugging'``, ``'business'``.
            If *None* (default) all tasks are returned.
    """

    CATEGORIES = list(_ALL_TASKS_BY_CATEGORY.keys())

    def __init__(self, category: str | None = None) -> None:
        if category is not None and category not in self.CATEGORIES:
            raise ValueError(
                f"Unknown category '{category}'. "
                f"Choose from: {self.CATEGORIES}"
            )
        self._category = category

    def get_task_type(self) -> str:
        # When filtering by a single category we can be precise.
        if self._category is not None:
            return _CATEGORY_TASK_TYPES[self._category]
        # Mixed bag when all categories are loaded.
        return "mixed"

    def load_tasks(self) -> list[Task]:
        if self._category is not None:
            raw_tasks = _ALL_TASKS_BY_CATEGORY[self._category]
            return [_build_task(t) for t in raw_tasks]
        return self.load_all_tasks()

    @classmethod
    def load_all_tasks(cls) -> list[Task]:
        """Return every real-world task regardless of category."""
        tasks: list[Task] = []
        for raw_list in _ALL_TASKS_BY_CATEGORY.values():
            for raw in raw_list:
                tasks.append(_build_task(raw))
        return tasks
