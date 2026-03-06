"""Planning tasks benchmark: baseline vs reflexion."""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.agent.reflexion_agent import ReflexionAgent
from src.tasks.planning import PlanningTaskLoader
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _tasks_to_dicts(tasks):
    return [
        {"id": t.id, "description": t.description, "expected_answer": t.expected_answer}
        for t in tasks
    ]


def main():
    client = LLMClient()
    loader = PlanningTaskLoader()
    tasks = loader.load_tasks()

    logger.info("Running Planning Tasks benchmark on %d tasks...", len(tasks))

    baseline_agent = ReflexionAgent(client, max_attempts=1)
    baseline_results = baseline_agent.solve_batch(_tasks_to_dicts(tasks), task_type="planning")
    b_scores = [r.score for r in baseline_results]

    reflexion_agent = ReflexionAgent(client, max_attempts=3)
    reflexion_results = reflexion_agent.solve_batch(_tasks_to_dicts(tasks), task_type="planning")
    r_scores = [r.score for r in reflexion_results]

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task_type": "planning",
        "baseline": {
            "mode": "baseline",
            "total": len(tasks),
            "avg_score": sum(b_scores) / len(b_scores) if b_scores else 0,
        },
        "reflexion": {
            "mode": "reflexion",
            "total": len(tasks),
            "avg_score": sum(r_scores) / len(r_scores) if r_scores else 0,
            "avg_attempts": sum(r.attempts for r in reflexion_results) / len(reflexion_results) if reflexion_results else 0,
        },
    }

    os.makedirs("results", exist_ok=True)
    out_path = "results/planning_results.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*50}")
    print("Planning Tasks Benchmark Results")
    print(f"{'='*50}")
    print(f"Baseline  avg score: {report['baseline']['avg_score']:.2f}")
    print(f"Reflexion avg score: {report['reflexion']['avg_score']:.2f}")
    improvement = report["reflexion"]["avg_score"] - report["baseline"]["avg_score"]
    print(f"Improvement: {improvement:+.2f}")
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
