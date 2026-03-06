"""ThinkTwice — quick demo script.

Run with:
    python main.py              # standard demo (math + code + logic)
    python main.py --showcase   # full real-world showcase

Requires at least one API key in .env (see .env.example).
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Add project root to path so `src` is importable
sys.path.insert(0, os.path.dirname(__file__))

from src.agent.reflexion_agent import ReflexionAgent
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger("thinktwice.demo")

_BANNER = """\
╔══════════════════════════════════════════════════════════╗
║   🧠  ThinkTwice — Self-Reflecting LLM Agent             ║
║       Attempt → Evaluate → Reflect → Retry               ║
╚══════════════════════════════════════════════════════════╝"""


def _print_section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def _print_result(result) -> None:  # type: ignore[type-arg]
    status = "✓  CORRECT" if result.is_correct else "✗  incorrect"
    print(f"  Status   : {status}  (score={result.score:.2f})")
    print(f"  Attempts : {result.attempts}/{result.max_attempts}")
    print(f"  Time     : {result.total_time:.1f}s  |  Tokens: {result.tokens_used}")
    if result.reflections:
        print(f"  Reflections generated: {len(result.reflections)}")
        for i, r in enumerate(result.reflections, 1):
            insight = r.get("key_insight", "")
            print(f"    [{i}] 💡 {insight[:90]}")
    preview = result.final_solution[-220:].replace("\n", " ")
    print(f"  Answer   : …{preview}")


def demo_math(client: LLMClient) -> None:
    """Demo: challenging multi-step math with reflexion loop."""
    _print_section("Demo 1 · Math Reasoning")

    task_description = (
        "Company X's revenue grew 20% in Year 1, then declined 20% in Year 2, "
        "then grew 20% again in Year 3. "
        "If the starting revenue was $1,000,000, what is the revenue at the end "
        "of Year 3? Give the answer in dollars as the FINAL ANSWER."
    )
    expected_answer = "1152000"

    print(f"  Task: {task_description[:100]}…")
    print(f"  Expected: ${expected_answer}")

    agent = ReflexionAgent(client, max_attempts=3)
    result = agent.solve(
        task_id="demo_math_001",
        task_description=task_description,
        expected_answer=expected_answer,
        task_type="math",
    )
    _print_result(result)


def demo_code(client: LLMClient) -> None:
    """Demo: coding interview question with reflexion loop."""
    _print_section("Demo 2 · Code Generation  (LRU Cache)")

    task_description = (
        "Implement an LRU (Least Recently Used) Cache in Python. "
        "Create a class `LRUCache` with `__init__(self, capacity)`, "
        "`get(self, key) -> int` (returns -1 if missing), "
        "and `put(self, key, value) -> None` (evicts LRU entry when full). "
        "Both operations must run in O(1) average time."
    )
    test_code = (
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
        "print('All tests passed!')"
    )

    print(f"  Task: {task_description[:100]}…")

    agent = ReflexionAgent(client, max_attempts=3)
    result = agent.solve(
        task_id="demo_code_001",
        task_description=task_description,
        task_type="code",
        test_code=test_code,
    )
    _print_result(result)


def demo_logic(client: LLMClient) -> None:
    """Demo: system-design reasoning with reflexion loop."""
    _print_section("Demo 3 · System Design Reasoning")

    task_description = (
        "A production microservice system has three services in a call chain: "
        "A → B → C. Normally each service responds in ~50 ms. "
        "Service C's latency suddenly spikes to 5,000 ms. "
        "1. What happens to Services A and B?\n"
        "2. What is 'cascading failure' and why does it occur here?\n"
        "3. Name and explain THREE design patterns that prevent this failure.\n"
        "(Must name specific patterns: e.g. Circuit Breaker, Bulkhead, Timeout.)"
    )

    print(f"  Task: {task_description[:100]}…")

    agent = ReflexionAgent(client, max_attempts=3)
    result = agent.solve(
        task_id="demo_logic_001",
        task_description=task_description,
        task_type="logic",
    )
    _print_result(result)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="ThinkTwice — Self-Reflecting LLM Agent demo",
    )
    parser.add_argument(
        "--showcase",
        action="store_true",
        help="Run the full real-world showcase demo (showcase.py)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    if args.showcase:
        # Redirect to showcase.py
        import subprocess  # noqa: PLC0415
        sys.exit(subprocess.call([sys.executable, "showcase.py"]))

    print(_BANNER)

    try:
        client = LLMClient()
        demo_math(client)
        demo_code(client)
        demo_logic(client)
    except EnvironmentError as e:
        print(f"\n[ERROR] {e}")
        print("Please set an API key in .env (copy .env.example → .env and fill in a key).")
        sys.exit(1)

    print(f"\n{'═' * 60}")
    print("  ✓  Demo complete!  Run `python main.py --showcase` for the")
    print("     full real-world showcase with rich terminal output.")
    print(f"{'═' * 60}\n")

