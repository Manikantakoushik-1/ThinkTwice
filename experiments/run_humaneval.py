"""HumanEval benchmark: baseline (1 attempt) vs reflexion (N attempts)."""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.agent.reflexion_agent import ReflexionAgent
from src.tasks.code_generation import CodeTaskLoader
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _tasks_to_dicts(tasks):
    return [
        {"id": t.id, "description": t.description, "expected_answer": t.expected_answer, "test_code": t.test_code}
        for t in tasks
    ]


def main():
    client = LLMClient()
    loader = CodeTaskLoader()
    tasks = loader.load_tasks()

    logger.info("Running HumanEval benchmark on %d tasks...", len(tasks))

    baseline_agent = ReflexionAgent(client, max_attempts=1)
    baseline_results = baseline_agent.solve_batch(_tasks_to_dicts(tasks), task_type="code")
    b_correct = sum(1 for r in baseline_results if r.is_correct)

    reflexion_agent = ReflexionAgent(client, max_attempts=3)
    reflexion_results = reflexion_agent.solve_batch(_tasks_to_dicts(tasks), task_type="code")
    r_correct = sum(1 for r in reflexion_results if r.is_correct)

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task_type": "code",
        "baseline": {
            "mode": "baseline",
            "total": len(tasks),
            "correct": b_correct,
            "accuracy": b_correct / len(tasks) if tasks else 0,
            "total_tokens": sum(r.tokens_used for r in baseline_results),
        },
        "reflexion": {
            "mode": "reflexion",
            "total": len(tasks),
            "correct": r_correct,
            "accuracy": r_correct / len(tasks) if tasks else 0,
            "avg_attempts": sum(r.attempts for r in reflexion_results) / len(reflexion_results) if reflexion_results else 0,
            "total_tokens": sum(r.tokens_used for r in reflexion_results),
        },
    }

    os.makedirs("results", exist_ok=True)
    out_path = "results/humaneval_results.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*50}")
    print("HumanEval Benchmark Results")
    print(f"{'='*50}")
    print(f"Baseline  accuracy: {report['baseline']['accuracy']:.1%} ({b_correct}/{len(tasks)})")
    print(f"Reflexion accuracy: {report['reflexion']['accuracy']:.1%} ({r_correct}/{len(tasks)})")
    improvement = report["reflexion"]["accuracy"] - report["baseline"]["accuracy"]
    print(f"Improvement: {improvement:+.1%}")
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
