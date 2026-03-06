"""ThinkTwice — Real-World Showcase Demo Script.

Run with:
    python showcase.py                           # full demo (5 tasks)
    python showcase.py --quick                   # 2 tasks only
    python showcase.py --category algorithms     # one category
    python showcase.py --max-attempts 5          # deeper reflection
    python showcase.py --verbose                 # show full solutions

Requires at least one API key in .env (see .env.example).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

# ── Optional rich import (graceful fallback) ──────────────────────────────

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box as rich_box

    _RICH = True
    console = Console()
except ImportError:  # pragma: no cover
    _RICH = False
    console = None  # type: ignore[assignment]

from src.agent.reflexion_agent import AgentResult, ReflexionAgent
from src.tasks.real_world import RealWorldTaskLoader
from src.tasks.base_task import Task
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger("thinktwice.showcase")

# ── Curated showcase task IDs (one per category, varied types) ────────────

_SHOWCASE_TASK_IDS: dict[str, str] = {
    "data_science": "rw_ds_002",   # A/B test analysis
    "algorithms":   "rw_algo_001", # LRU Cache
    "system_design":"rw_sd_002",   # Cascading failures
    "debugging":    "rw_dbg_001",  # Fibonacci bug fix
    "business":     "rw_biz_001",  # Compound investment
}

_CATEGORY_LABELS: dict[str, str] = {
    "data_science":  "📊 Data Science",
    "algorithms":    "⚡ Algorithms",
    "system_design": "🏗️  System Design",
    "debugging":     "🐛 Debugging",
    "business":      "💼 Business Math",
}

# ── ANSI fallback helpers ─────────────────────────────────────────────────

_BOLD   = "\033[1m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_CYAN   = "\033[36m"
_RED    = "\033[31m"
_MAGENTA= "\033[35m"
_RESET  = "\033[0m"

_ASCII_BANNER = r"""
 _____ _     _       _      _____          _
|_   _| |__ (_)_ __ | | __ |_   _|_      _(_) ___ ___
  | | | '_ \| | '_ \| |/ /   | | \ \ /\ / / |/ __/ _ \
  | | | | | | | | | |   <    | |  \ V  V /| | (_|  __/
  |_| |_| |_|_|_| |_|_|\_\   |_|   \_/\_/ |_|\___\___|

  🧠  Self-Reflecting LLM Agent  |  Real-World Showcase
  Attempt → Evaluate → Reflect → Retry
"""


def _p(text: str) -> None:
    """Print with or without rich."""
    if _RICH:
        console.print(text)  # type: ignore[union-attr]
    else:
        # Strip rich markup for plain output
        import re
        plain = re.sub(r"\[/?[^\]]*\]", "", text)
        print(plain)


def _print_banner() -> None:
    if _RICH:
        console.print(  # type: ignore[union-attr]
            Panel.fit(
                "[bold cyan]🧠  ThinkTwice[/bold cyan]  ·  "
                "[bold white]Self-Reflecting LLM Agent[/bold white]\n"
                "[dim]Attempt → Evaluate → Reflect → Retry[/dim]\n"
                "[italic yellow]Real-World Showcase Demo[/italic yellow]",
                border_style="cyan",
                padding=(1, 4),
            )
        )
    else:
        print(_ASCII_BANNER)
        print("=" * 65)


def _print_task_header(idx: int, total: int, category: str, task: Task) -> None:
    label = _CATEGORY_LABELS.get(category, category)
    if _RICH:
        console.print(  # type: ignore[union-attr]
            f"\n[bold white]Task {idx}/{total}[/bold white]  "
            f"[bold yellow]{label}[/bold yellow]"
        )
        console.print(  # type: ignore[union-attr]
            Panel(
                f"[bold]{task.description[:300]}{'…' if len(task.description) > 300 else ''}[/bold]",
                title=f"[cyan]{task.id}[/cyan]",
                border_style="dim",
            )
        )
    else:
        print(f"\n{'─'*65}")
        print(f"  Task {idx}/{total}  |  {label}  [{task.id}]")
        print(f"{'─'*65}")
        print(f"  {task.description[:200]}…")
        print()


def _print_attempt_result(
    label: str, result: AgentResult, verbose: bool = False
) -> None:
    correct_str = "✓  CORRECT" if result.is_correct else "✗  incorrect"
    color = "green" if result.is_correct else "red"

    if _RICH:
        _p(
            f"  [{color}]{correct_str}[/{color}]  "
            f"score=[bold]{result.score:.2f}[/bold]  "
            f"attempts=[bold]{result.attempts}/{result.max_attempts}[/bold]  "
            f"time=[bold]{result.total_time:.1f}s[/bold]  "
            f"tokens=[bold]{result.tokens_used}[/bold]"
        )
    else:
        print(f"  {label}: {correct_str}  score={result.score:.2f}  "
              f"attempts={result.attempts}/{result.max_attempts}  "
              f"time={result.total_time:.1f}s")

    if result.reflections:
        if _RICH:
            _p("  [italic yellow]💡 Reflection insights:[/italic yellow]")
        else:
            print("  Reflection insights:")
        for i, r in enumerate(result.reflections, 1):
            insight = r.get("key_insight", "—")
            strategy = r.get("strategy", "")
            if _RICH:
                _p(f"    [yellow][{i}] {insight[:100]}[/yellow]")
                if strategy:
                    _p(f"        [dim]→ Strategy: {strategy[:80]}[/dim]")
            else:
                print(f"    [{i}] {insight[:100]}")
                if strategy:
                    print(f"        → Strategy: {strategy[:80]}")

    if verbose and result.final_solution:
        if _RICH:
            _p("\n  [dim]── Final solution (last 400 chars) ──[/dim]")
            _p(f"  [dim]{result.final_solution[-400:]}[/dim]")
        else:
            print(f"\n  Final solution:\n  {result.final_solution[-400:]}")


def _run_baseline(agent: ReflexionAgent, task: Task) -> AgentResult:
    """Single-attempt baseline (max_attempts=1)."""
    agent.max_attempts = 1
    agent.reset()
    return agent.solve(
        task_id=f"{task.id}_baseline",
        task_description=task.description,
        expected_answer=task.expected_answer,
        task_type=task.task_type,
        test_code=task.test_code,
    )


def _run_reflexion(agent: ReflexionAgent, task: Task, max_attempts: int) -> AgentResult:
    """Full reflexion run."""
    agent.max_attempts = max_attempts
    agent.reset()
    return agent.solve(
        task_id=task.id,
        task_description=task.description,
        expected_answer=task.expected_answer,
        task_type=task.task_type,
        test_code=task.test_code,
    )


def _print_comparison_table(
    task_results: list[dict],
) -> None:
    """Print a side-by-side baseline vs reflexion table."""
    if _RICH:
        table = Table(
            title="📊  Baseline vs Reflexion — Summary",
            box=rich_box.ROUNDED,
            border_style="cyan",
            show_lines=True,
        )
        table.add_column("Task", style="bold white", min_width=22)
        table.add_column("Category", style="yellow")
        table.add_column("Baseline", justify="center")
        table.add_column("Reflexion", justify="center")
        table.add_column("Improved?", justify="center")
        table.add_column("Attempts", justify="center")
        table.add_column("Time (s)", justify="right")

        for tr in task_results:
            base_ok = tr["baseline"].is_correct
            refx_ok = tr["reflexion"].is_correct
            improved = (not base_ok) and refx_ok
            base_str = "[green]✓[/green]" if base_ok else "[red]✗[/red]"
            refx_str = "[green]✓[/green]" if refx_ok else "[red]✗[/red]"
            imp_str  = "[bold green]🚀 YES[/bold green]" if improved else (
                       "[dim]—[/dim]" if base_ok else "[yellow]~[/yellow]")
            table.add_row(
                tr["task"].id,
                _CATEGORY_LABELS.get(tr["category"], tr["category"]),
                base_str,
                refx_str,
                imp_str,
                str(tr["reflexion"].attempts),
                f"{tr['reflexion'].total_time:.1f}",
            )

        console.print("\n")  # type: ignore[union-attr]
        console.print(table)  # type: ignore[union-attr]
    else:
        print(f"\n{'═'*65}")
        print("  SUMMARY: Baseline vs Reflexion")
        print(f"{'═'*65}")
        header = f"  {'Task':<20} {'Cat':<14} {'Base':^6} {'Refx':^6} {'Improved':^10}"
        print(header)
        print(f"  {'-'*60}")
        for tr in task_results:
            base_ok = tr["baseline"].is_correct
            refx_ok = tr["reflexion"].is_correct
            improved = (not base_ok) and refx_ok
            print(
                f"  {tr['task'].id:<20} "
                f"{tr['category']:<14} "
                f"{'✓' if base_ok else '✗':^6} "
                f"{'✓' if refx_ok else '✗':^6} "
                f"{'🚀 YES' if improved else '—':^10}"
            )
        print(f"{'═'*65}\n")


def _print_stats(task_results: list[dict]) -> None:
    n = len(task_results)
    base_correct = sum(1 for tr in task_results if tr["baseline"].is_correct)
    refx_correct = sum(1 for tr in task_results if tr["reflexion"].is_correct)
    improved     = sum(
        1 for tr in task_results
        if (not tr["baseline"].is_correct) and tr["reflexion"].is_correct
    )
    total_reflections = sum(
        len(tr["reflexion"].reflections) for tr in task_results
    )
    total_time = sum(tr["reflexion"].total_time for tr in task_results)

    if _RICH:
        _p(f"\n[bold cyan]📈  Statistics[/bold cyan]")
        _p(f"  Tasks run          : [bold]{n}[/bold]")
        _p(f"  Baseline correct   : [bold]{base_correct}/{n}[/bold]  ({100*base_correct//n}%)")
        _p(f"  Reflexion correct  : [bold]{refx_correct}/{n}[/bold]  ({100*refx_correct//n}%)")
        _p(f"  [bold green]Reflection improved: {improved} task(s)[/bold green]")
        _p(f"  Total reflections  : [bold]{total_reflections}[/bold]")
        _p(f"  Total time         : [bold]{total_time:.1f}s[/bold]")
    else:
        print(f"\n{'─'*65}")
        print("  Statistics")
        print(f"  Tasks run         : {n}")
        print(f"  Baseline correct  : {base_correct}/{n}")
        print(f"  Reflexion correct : {refx_correct}/{n}")
        print(f"  Reflection improved {improved} task(s)")
        print(f"  Total reflections : {total_reflections}")
        print(f"  Total time        : {total_time:.1f}s")
        print(f"{'─'*65}\n")


def _save_results(task_results: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    records = []
    for tr in task_results:
        records.append({
            "task_id": tr["task"].id,
            "category": tr["category"],
            "task_type": tr["task"].task_type,
            "baseline": {
                "is_correct": tr["baseline"].is_correct,
                "score": tr["baseline"].score,
                "attempts": tr["baseline"].attempts,
                "total_time": tr["baseline"].total_time,
                "tokens_used": tr["baseline"].tokens_used,
            },
            "reflexion": {
                "is_correct": tr["reflexion"].is_correct,
                "score": tr["reflexion"].score,
                "attempts": tr["reflexion"].attempts,
                "total_time": tr["reflexion"].total_time,
                "tokens_used": tr["reflexion"].tokens_used,
                "reflections": tr["reflexion"].reflections,
                "evaluation_history": tr["reflexion"].evaluation_history,
            },
            "improved_by_reflection": (
                (not tr["baseline"].is_correct) and tr["reflexion"].is_correct
            ),
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "results": records}, f, indent=2)
    _p(f"\n[dim]Results saved to {path}[/dim]")


def _select_tasks(
    all_tasks: list[Task],
    category: str | None,
    quick: bool,
) -> list[tuple[str, Task]]:
    """Return a list of (category, task) pairs for the showcase."""
    # Build category lookup
    task_by_id: dict[str, tuple[str, Task]] = {}
    for t in all_tasks:
        cat = t.metadata.get("category", "unknown")
        task_by_id[t.id] = (cat, t)

    if category is not None:
        # All tasks from the requested category
        selected = [
            (cat, t) for (cat, t) in task_by_id.values() if cat == category
        ]
    else:
        # Curated showcase selection
        selected = [
            task_by_id[tid]
            for tid in _SHOWCASE_TASK_IDS.values()
            if tid in task_by_id
        ]

    if quick:
        selected = selected[:2]

    return selected


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="showcase.py",
        description="ThinkTwice — Real-World Showcase Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python showcase.py\n"
            "  python showcase.py --quick\n"
            "  python showcase.py --category algorithms\n"
            "  python showcase.py --max-attempts 5 --verbose\n"
        ),
    )
    parser.add_argument(
        "--category",
        choices=RealWorldTaskLoader.CATEGORIES,
        default=None,
        help="Run only tasks from this category.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run just 2 tasks (faster demo).",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        metavar="N",
        help="Max reflexion attempts per task (default: 3).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print full solutions.",
    )
    parser.add_argument(
        "--output",
        default="results/showcase_results.json",
        metavar="PATH",
        help="Path to save JSON results (default: results/showcase_results.json).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    _print_banner()

    try:
        client = LLMClient()
    except EnvironmentError as e:
        _p(f"[bold red][ERROR][/bold red] {e}")
        _p("Please set an API key in .env (copy .env.example → .env and fill in a key).")
        sys.exit(1)

    loader = RealWorldTaskLoader()
    all_tasks = loader.load_all_tasks()
    selected = _select_tasks(all_tasks, args.category, args.quick)

    if not selected:
        _p("[red]No tasks selected. Check --category value.[/red]")
        sys.exit(1)

    _p(
        f"\n[bold]Running [cyan]{len(selected)}[/cyan] tasks with "
        f"max_attempts=[cyan]{args.max_attempts}[/cyan][/bold]\n"
    )

    agent = ReflexionAgent(client, max_attempts=args.max_attempts)
    task_results: list[dict] = []

    for idx, (category, task) in enumerate(selected, 1):
        _print_task_header(idx, len(selected), category, task)

        # ── Baseline: single attempt ──────────────────────────────────────
        if _RICH:
            _p("  [bold dim]⟶  Baseline (1 attempt) …[/bold dim]")
        else:
            print("  ⟶  Baseline (1 attempt) …")

        baseline_result = _run_baseline(agent, task)
        _print_attempt_result("Baseline", baseline_result, verbose=False)

        # ── Reflexion: full loop ──────────────────────────────────────────
        if _RICH:
            _p(f"\n  [bold]⟶  Reflexion ({args.max_attempts} attempts) …[/bold]")
        else:
            print(f"\n  ⟶  Reflexion ({args.max_attempts} attempts) …")

        reflexion_result = _run_reflexion(agent, task, args.max_attempts)
        _print_attempt_result("Reflexion", reflexion_result, verbose=args.verbose)

        # Highlight improvement
        if (not baseline_result.is_correct) and reflexion_result.is_correct:
            if _RICH:
                _p(
                    "\n  [bold green]🚀  Reflection loop FIXED this task! "
                    f"Solved on attempt {reflexion_result.attempts}.[/bold green]"
                )
            else:
                print(
                    f"\n  🚀  Reflection loop FIXED this task! "
                    f"Solved on attempt {reflexion_result.attempts}."
                )

        task_results.append({
            "category": category,
            "task": task,
            "baseline": baseline_result,
            "reflexion": reflexion_result,
        })

    # ── Final summary ─────────────────────────────────────────────────────
    _print_comparison_table(task_results)
    _print_stats(task_results)
    _save_results(task_results, args.output)

    if _RICH:
        _p(
            "\n[bold cyan]✓  Showcase complete![/bold cyan]  "
            "Visit [underline]results/showcase_results.json[/underline] for detailed data.\n"
        )
    else:
        print("\n✓  Showcase complete!  See results/showcase_results.json\n")


if __name__ == "__main__":
    main()
