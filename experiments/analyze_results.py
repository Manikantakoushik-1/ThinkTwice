"""Analyze experiment results and print a comparison table."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

RESULT_FILES = {
    "math": "results/gsm8k_results.json",
    "code": "results/humaneval_results.json",
    "logic": "results/logic_results.json",
    "planning": "results/planning_results.json",
}


def load_result(path: str) -> dict | None:
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return json.load(f)


def format_pct(value: float) -> str:
    return f"{value:.1%}"


def main():
    print(f"\n{'='*70}")
    print(f"{'ThinkTwice — Experiment Results Summary':^70}")
    print(f"{'='*70}")
    print(f"{'Task Type':<12} {'Baseline':>10} {'Reflexion':>10} {'Improvement':>12} {'Token Ratio':>12}")
    print(f"{'-'*70}")

    for task_type, path in RESULT_FILES.items():
        data = load_result(path)
        if data is None:
            print(f"{task_type:<12} {'N/A':>10} {'N/A':>10} {'N/A':>12} {'N/A':>12}")
            continue

        baseline = data.get("baseline", {})
        reflexion = data.get("reflexion", {})

        # Use accuracy if available, else avg_score
        b_metric = baseline.get("accuracy", baseline.get("avg_score", 0))
        r_metric = reflexion.get("accuracy", reflexion.get("avg_score", 0))
        improvement = r_metric - b_metric

        b_tokens = baseline.get("total_tokens", 0)
        r_tokens = reflexion.get("total_tokens", 0)
        token_ratio = (r_tokens / b_tokens) if b_tokens > 0 else float("nan")

        print(
            f"{task_type:<12} {format_pct(b_metric):>10} {format_pct(r_metric):>10} "
            f"{improvement:>+11.1%} {token_ratio:>11.1f}x"
        )

    print(f"{'='*70}")
    print("\nNote: Token Ratio = reflexion tokens / baseline tokens (cost overhead)")


if __name__ == "__main__":
    main()
