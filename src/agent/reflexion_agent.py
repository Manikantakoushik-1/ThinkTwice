"""ReflexionAgent — main orchestrator for the Attempt→Evaluate→Reflect→Retry loop."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from src.agent.actor import Actor
from src.agent.evaluator import Evaluator
from src.agent.reflector import Reflector
from src.memory.episodic_memory import EpisodicMemory, Reflection
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentResult:
    """Full record of a single task run."""

    task_id: str
    task_description: str
    final_solution: str
    is_correct: bool
    score: float
    attempts: int
    max_attempts: int
    reflections: list[dict] = field(default_factory=list)
    evaluation_history: list[dict] = field(default_factory=list)
    total_time: float = 0.0
    tokens_used: int = 0


class ReflexionAgent:
    """Self-reflecting LLM agent that loops: Attempt → Evaluate → Reflect → Retry.

    Args:
        llm_client: Shared :class:`~src.utils.llm_client.LLMClient`.
        max_attempts: Maximum number of attempts per task (default ``3``).
    """

    def __init__(
        self,
        llm_client: LLMClient,
        max_attempts: int = 3,
    ) -> None:
        self._llm = llm_client
        self.max_attempts = max_attempts
        self._actor = Actor(llm_client)
        self._evaluator = Evaluator(llm_client)
        self._reflector = Reflector(llm_client)
        self._memory = EpisodicMemory()

    # ── Public API ────────────────────────────────────────────────────────────

    def solve(
        self,
        task_id: str,
        task_description: str,
        expected_answer: str | None = None,
        task_type: str = "general",
        test_code: str | None = None,
    ) -> AgentResult:
        """Run the reflexion loop for a single task.

        Returns:
            An :class:`AgentResult` summarising the full run.
        """
        start_time = time.time()
        tokens_before = self._llm.total_tokens_used

        last_solution = ""
        eval_result: dict = {}
        reflections_list: list[dict] = []
        eval_history: list[dict] = []

        for attempt in range(1, self.max_attempts + 1):
            logger.info(
                "── Attempt %d/%d  task_id=%s ──", attempt, self.max_attempts, task_id
            )

            # 1. Retrieve reflection context from memory
            reflection_context = self._memory.format_reflections_for_prompt(task_id)

            # 2. Actor generates a solution
            last_solution = self._actor.generate_solution(
                task_description=task_description,
                task_type=task_type,
                reflection_context=reflection_context,
                attempt_number=attempt,
            )

            # 3. Evaluator checks correctness
            eval_result = self._evaluator.evaluate(
                solution=last_solution,
                expected_answer=expected_answer,
                task_type=task_type,
                task_description=task_description,
                test_code=test_code,
            )
            eval_history.append({"attempt": attempt, **eval_result})

            logger.info(
                "Evaluator result — correct=%s score=%.2f feedback=%s",
                eval_result["is_correct"],
                eval_result["score"],
                eval_result["feedback"][:100],
            )

            # 4. If correct, we're done!
            if eval_result["is_correct"]:
                logger.info("✓ Task solved in %d attempt(s)!", attempt)
                break

            # 5. If we have attempts left, reflect and store
            if attempt < self.max_attempts:
                reflection_data = self._reflector.reflect(
                    task_description=task_description,
                    failed_solution=last_solution,
                    evaluation_feedback=eval_result.get("feedback", ""),
                    previous_reflections=reflection_context,
                    attempt_number=attempt,
                )

                reflection = Reflection(
                    task_id=task_id,
                    attempt_number=attempt,
                    action_taken=last_solution[:300],
                    outcome=eval_result.get("feedback", ""),
                    reflection_text=reflection_data.get("full_text", ""),
                    key_insight=reflection_data.get("key_insight", ""),
                    success=False,
                )
                self._memory.add_reflection(reflection)
                reflections_list.append(reflection_data)

                logger.info(
                    "Reflector insight: %s", reflection_data.get("key_insight", "")[:100]
                )
            else:
                logger.info("✗ Max attempts reached for task_id=%s", task_id)

        total_time = time.time() - start_time
        tokens_used = self._llm.total_tokens_used - tokens_before

        return AgentResult(
            task_id=task_id,
            task_description=task_description,
            final_solution=last_solution,
            is_correct=eval_result.get("is_correct", False),
            score=eval_result.get("score", 0.0),
            attempts=attempt,
            max_attempts=self.max_attempts,
            reflections=reflections_list,
            evaluation_history=eval_history,
            total_time=total_time,
            tokens_used=tokens_used,
        )

    def solve_batch(
        self,
        tasks: list[dict],
        task_type: str = "general",
    ) -> list[AgentResult]:
        """Solve a list of tasks, clearing memory between each.

        Each item in *tasks* must have keys: ``id``, ``description``.
        Optional keys: ``expected_answer``, ``test_code``.
        """
        results = []
        for task in tasks:
            self._memory.clear(task.get("id", ""))
            result = self.solve(
                task_id=task.get("id", "unknown"),
                task_description=task["description"],
                expected_answer=task.get("expected_answer"),
                task_type=task_type,
                test_code=task.get("test_code"),
            )
            results.append(result)
        return results

    def reset(self) -> None:
        """Clear all episodic memory."""
        self._memory.clear()
        logger.info("ReflexionAgent memory reset.")
