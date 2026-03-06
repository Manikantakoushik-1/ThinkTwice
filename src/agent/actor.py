"""Actor — LLM-based solution generator for the ReflexionAgent."""

from __future__ import annotations

from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """\
You are an expert problem-solving assistant. Your goal is to solve tasks correctly and completely.

Rules:
1. Think step-by-step before giving your final answer.
2. Show your reasoning clearly.
3. Always end your response with "FINAL ANSWER: <your answer>" on a new line.
4. Be precise and concise.

{reflection_context}
"""

_TYPE_INSTRUCTIONS: dict[str, str] = {
    "math": (
        "For math problems: show each arithmetic step explicitly, "
        "double-check your arithmetic, and express the final answer as a number."
    ),
    "code": (
        "For coding tasks: write a complete, runnable Python function. "
        "Do not include test calls at the module level — only define the function."
    ),
    "logic": (
        "For logic puzzles: list every constraint and work through them systematically."
    ),
    "planning": (
        "For planning tasks: break the solution into clear, numbered steps and "
        "consider potential obstacles."
    ),
}


class Actor:
    """Generates solutions using an LLM, optionally augmented with reflection context.

    Args:
        llm_client: A configured :class:`~src.utils.llm_client.LLMClient`.
        temperature: Sampling temperature (default ``0.3`` for determinism).
    """

    def __init__(self, llm_client: LLMClient, temperature: float = 0.3) -> None:
        self._client = llm_client
        self._temperature = temperature

    def generate_solution(
        self,
        task_description: str,
        task_type: str = "general",
        reflection_context: str = "",
        attempt_number: int = 1,
    ) -> str:
        """Generate a solution for the given task.

        Args:
            task_description: The problem statement.
            task_type: One of ``math``, ``code``, ``logic``, ``planning``.
            reflection_context: Formatted string of previous reflections.
            attempt_number: Current attempt number (1-based).

        Returns:
            The raw LLM response string.
        """
        retry_prefix = ""
        if attempt_number > 1 and reflection_context:
            retry_prefix = (
                "IMPORTANT — You have tried this before and failed. "
                "Study your previous mistakes carefully and use a DIFFERENT approach.\n\n"
            )

        system = SYSTEM_PROMPT.format(
            reflection_context=reflection_context if reflection_context else ""
        )
        user_prompt = self._format_task_prompt(
            retry_prefix + task_description, task_type
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ]

        logger.info(
            "Actor generating solution — attempt=%d task_type=%s", attempt_number, task_type
        )
        response = self._client.generate_with_history(
            messages, temperature=self._temperature
        )
        logger.debug("Actor response (first 200 chars): %s", response[:200])
        return response

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_task_prompt(self, task_description: str, task_type: str) -> str:
        """Add type-specific instructions to the task prompt."""
        instruction = _TYPE_INSTRUCTIONS.get(task_type, "")
        if instruction:
            return f"{instruction}\n\nTask:\n{task_description}"
        return f"Task:\n{task_description}"
