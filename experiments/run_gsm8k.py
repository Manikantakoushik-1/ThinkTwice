"""GSM8K benchmark: baseline (1 attempt) vs reflexion (N attempts)."""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.agent.reflexion_agent import ReflexionAgent
from src.tasks.math_reasoning import MathTaskLoader
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_baseline(tasks, llm_client) -> dict:
    """Run each task once (no reflection)."""
    agent = ReflexionAgent(llm_client, max_attempts=1)
    results = agent.solve_batch(
        [{"id": t.id, "description": t.description, "expected_answer": t.expected_answer} for t in tasks],
        task_type="math",
    )
    correct = sum(1 for r in results if r.is_correct)
    return {
        "mode": "baseline",
        "total": len(tasks),
        "correct": correct,
        "accuracy": correct / len(tasks) if tasks else 0,
        "avg_attempts": 1.0,
        "total_tokens": sum(r.tokens_used for r in results),
    }


def run_reflexion(tasks, llm_client, max_attempts: int = 3) -> dict:
    """Run each task with up to max_attempts (reflexion loop)."""
    agent = ReflexionAgent(llm_client, max_attempts=max_attempts)
    results = agent.solve_batch(
        [{"id": t.id, "description": t.description, "expected_answer": t.expected_answer} for t in tasks],
        task_type="math",
    )
    correct = sum(1 for r in results if r.is_correct)
    avg_attempts = sum(r.attempts for r in results) / len(results) if results else 0
    return {
        "mode": "reflexion",
        "total": len(tasks),
        "correct": correct,
        "accuracy": correct / len(tasks) if tasks else 0,
        "avg_attempts": avg_attempts,
        "total_tokens": sum(r.tokens_used for r in results),
    }


def main():
    client = LLMClient()
    loader = MathTaskLoader()
    tasks = loader.load_tasks()

    logger.info("Running GSM8K benchmark on %d tasks...", len(tasks))

    baseline = run_baseline(tasks, client)
    reflexion = run_reflexion(tasks, client, max_attempts=3)

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task_type": "math",
        "baseline": baseline,
        "reflexion": reflexion,
    }

    os.makedirs("results", exist_ok=True)
    out_path = "results/gsm8k_results.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*50}")
    print("GSM8K Benchmark Results")
    print(f"{'='*50}")
    print(f"Baseline  accuracy: {baseline['accuracy']:.1%} ({baseline['correct']}/{baseline['total']})")
    print(f"Reflexion accuracy: {reflexion['accuracy']:.1%} ({reflexion['correct']}/{reflexion['total']})")
    improvement = reflexion["accuracy"] - baseline["accuracy"]
    print(f"Improvement: {improvement:+.1%}")
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
