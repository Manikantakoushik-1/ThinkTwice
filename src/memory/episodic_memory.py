"""Episodic memory — stores reflections across agent attempts."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Reflection:
    """A single reflection produced after a failed attempt."""

    task_id: str
    attempt_number: int
    action_taken: str
    outcome: str
    reflection_text: str
    key_insight: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    success: bool = False


class EpisodicMemory:
    """Stores and retrieves reflections across attempts for each task.

    Args:
        max_reflections_per_task: Maximum number of reflections to keep per task.
            Oldest reflections are dropped when the limit is exceeded.
    """

    def __init__(self, max_reflections_per_task: int = 10) -> None:
        self._max = max_reflections_per_task
        self._store: dict[str, list[Reflection]] = defaultdict(list)

    # ── Write API ──────────────────────────────────────────────────────────────

    def add_reflection(self, reflection: Reflection) -> None:
        """Store a reflection; evicts the oldest if the cap is reached."""
        bucket = self._store[reflection.task_id]
        bucket.append(reflection)
        if len(bucket) > self._max:
            self._store[reflection.task_id] = bucket[-self._max :]

    # ── Read API ───────────────────────────────────────────────────────────────

    def get_reflections(self, task_id: str) -> list[Reflection]:
        """Return all reflections for *task_id* (oldest first)."""
        return list(self._store.get(task_id, []))

    def get_latest_reflection(self, task_id: str) -> Reflection | None:
        """Return the most recent reflection for *task_id*, or ``None``."""
        bucket = self._store.get(task_id, [])
        return bucket[-1] if bucket else None

    def get_all_insights(self, task_id: str) -> list[str]:
        """Return just the ``key_insight`` strings for *task_id*."""
        return [r.key_insight for r in self._store.get(task_id, [])]

    def format_reflections_for_prompt(self, task_id: str) -> str:
        """Format all reflections for injection into an LLM prompt."""
        reflections = self.get_reflections(task_id)
        if not reflections:
            return ""

        lines: list[str] = ["=== Previous Attempts ==="]
        for r in reflections:
            status = "✓" if r.success else "✗"
            lines.append(
                f"\nAttempt {r.attempt_number} [{status}]"
                f"\n  Action:     {r.action_taken}"
                f"\n  Outcome:    {r.outcome}"
                f"\n  Reflection: {r.reflection_text}"
                f"\n  Key Insight: {r.key_insight}"
            )
        lines.append("=== End of Previous Attempts ===")
        return "\n".join(lines)

    # ── Maintenance ────────────────────────────────────────────────────────────

    def clear(self, task_id: str | None = None) -> None:
        """Clear reflections for a specific task, or all tasks if *task_id* is ``None``."""
        if task_id is None:
            self._store.clear()
        else:
            self._store.pop(task_id, None)

    def get_stats(self) -> dict[str, int]:
        """Return aggregate statistics across all tasks."""
        total_tasks = len(self._store)
        total_reflections = sum(len(v) for v in self._store.values())
        total_successes = sum(
            1 for bucket in self._store.values() for r in bucket if r.success
        )
        return {
            "total_tasks": total_tasks,
            "total_reflections": total_reflections,
            "total_successes": total_successes,
        }
