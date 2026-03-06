"""ThinkTwice — quick demo script.

Run with:
    python main.py

Requires at least one API key in .env (see .env.example).
"""

from __future__ import annotations

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


def demo_math():
    """Demo: math reasoning with reflexion loop."""
    print("\n" + "=" * 60)
    print("Demo 1: Math Reasoning")
    print("=" * 60)

    task_description = (
        "A student buys 3 notebooks for $2 each and 2 pens for $1.50 each. "
        "She pays with a $10 bill. How much change does she receive?"
    )
    expected_answer = "4"

    client = LLMClient()
    agent = ReflexionAgent(client, max_attempts=3)

    print(f"Task: {task_description}")
    print(f"Expected answer: ${expected_answer}")
    print()

    result = agent.solve(
        task_id="demo_math_001",
        task_description=task_description,
        expected_answer=expected_answer,
        task_type="math",
    )

    print(f"Correct: {result.is_correct}")
    print(f"Attempts: {result.attempts}/{result.max_attempts}")
    print(f"Time: {result.total_time:.1f}s")
    if result.reflections:
        print(f"\nReflections generated: {len(result.reflections)}")
        for i, r in enumerate(result.reflections, 1):
            print(f"  [{i}] Insight: {r.get('key_insight', '')[:80]}")
    print(f"\nFinal solution (last 200 chars):\n{result.final_solution[-200:]}")


def demo_logic():
    """Demo: logic puzzle with reflexion loop."""
    print("\n" + "=" * 60)
    print("Demo 2: Logic Puzzle")
    print("=" * 60)

    task_description = (
        "You have three boxes labeled 'Apples', 'Oranges', and 'Apples & Oranges'. "
        "ALL labels are WRONG. You may pick one fruit from exactly one box "
        "(without looking). Which box should you pick from, and what does each "
        "box actually contain? Explain your reasoning."
    )

    client = LLMClient()
    agent = ReflexionAgent(client, max_attempts=3)

    print(f"Task: {task_description[:100]}...")
    print()

    result = agent.solve(
        task_id="demo_logic_001",
        task_description=task_description,
        task_type="logic",
    )

    print(f"Correct: {result.is_correct}  (score={result.score:.2f})")
    print(f"Attempts: {result.attempts}/{result.max_attempts}")
    print(f"Time: {result.total_time:.1f}s")
    if result.reflections:
        insights = [r.get("key_insight", "") for r in result.reflections]
        print(f"\nKey insights gathered:")
        for insight in insights:
            print(f"  • {insight[:80]}")
    print(f"\nFinal solution (last 300 chars):\n{result.final_solution[-300:]}")


if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║  ThinkTwice — Self-Reflecting LLM Agent  ║")
    print("╚══════════════════════════════════════════╝")

    try:
        demo_math()
        demo_logic()
    except EnvironmentError as e:
        print(f"\n[ERROR] {e}")
        print("Please set an API key in .env (copy .env.example → .env and fill in a key).")
        sys.exit(1)

    print("\n✓ Demo complete!")
