"""Planning task loader — open-ended system design and architecture tasks."""

from __future__ import annotations

from src.tasks.base_task import Task, TaskLoader

_BUILTIN_TASKS = [
    {
        "id": "plan_001",
        "description": (
            "Design a high-level architecture for a real-time chat application that can "
            "support 1 million concurrent users. Include components for: message delivery, "
            "presence (online/offline status), message persistence, and horizontal scaling. "
            "Identify potential bottlenecks and how you would address them."
        ),
    },
    {
        "id": "plan_002",
        "description": (
            "You have a large monolithic Python web application that has grown to 500k lines "
            "of code and is becoming hard to maintain and deploy. Create a step-by-step "
            "migration plan to break it into microservices. Address: how to identify service "
            "boundaries, how to handle data separation, how to manage the transition period "
            "without downtime, and how to handle cross-service transactions."
        ),
    },
]


class PlanningTaskLoader(TaskLoader):
    """Loader for open-ended planning and system-design tasks.

    These tasks have no single correct answer and are evaluated by LLM-as-judge.
    """

    def get_task_type(self) -> str:
        return "planning"

    def load_tasks(self) -> list[Task]:
        return [
            Task(
                id=t["id"],
                description=t["description"],
                expected_answer=None,  # judged by LLM
                task_type="planning",
            )
            for t in _BUILTIN_TASKS
        ]
