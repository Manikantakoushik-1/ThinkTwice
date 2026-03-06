"""Abstract base classes for task definitions and loaders."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Task:
    """A single task instance."""

    id: str
    description: str
    expected_answer: str | None
    task_type: str
    test_code: str | None = None
    metadata: dict = field(default_factory=dict)


class TaskLoader(ABC):
    """Abstract base class for task loaders."""

    @abstractmethod
    def load_tasks(self) -> list[Task]:
        """Load and return a list of Task instances."""

    @abstractmethod
    def get_task_type(self) -> str:
        """Return the task type string (e.g. 'math', 'code', 'logic', 'planning')."""
