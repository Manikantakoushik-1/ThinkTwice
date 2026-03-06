"""Reflector — self-reflection engine that analyzes failed attempts."""

from __future__ import annotations

import re

from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """\
You are a self-reflection engine for an AI agent. Your job is to analyze why an attempt failed
and provide structured, actionable insights to guide the next attempt.

Always respond with the following four sections (use exact headers):

WHAT WENT WRONG:
<describe the specific mistake(s) in the solution>

ROOT CAUSE:
<identify the underlying reason for the failure>

KEY INSIGHT:
<one concise, actionable insight that will help succeed next time>

STRATEGY:
<concrete steps the agent should take differently on the next attempt>
"""


class Reflector:
    """Analyzes failed attempts and generates structured reflections.

    Args:
        llm_client: A configured :class:`~src.utils.llm_client.LLMClient`.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self._client = llm_client

    def reflect(
        self,
        task_description: str,
        failed_solution: str,
        evaluation_feedback: str,
        previous_reflections: str = "",
        attempt_number: int = 1,
    ) -> dict[str, str]:
        """Generate a structured reflection for a failed attempt.

        Args:
            task_description: The original task.
            failed_solution: The solution that was evaluated as incorrect.
            evaluation_feedback: Feedback from the evaluator.
            previous_reflections: Formatted string of earlier reflections (may be empty).
            attempt_number: The attempt that just failed (1-based).

        Returns:
            A dict with keys: ``what_went_wrong``, ``root_cause``,
            ``key_insight``, ``strategy``, ``full_text``.
        """
        retry_note = ""
        if attempt_number > 1 and previous_reflections:
            retry_note = (
                "\nPrevious reflections have already been collected. "
                "Provide a NEW and DEEPER reflection with a DIFFERENT strategy.\n"
            )

        prev_section = ""
        if previous_reflections:
            prev_section = f"\n{previous_reflections}\n"

        prompt = f"""\
{prev_section}
Task:
{task_description}

Failed Solution (Attempt {attempt_number}):
{failed_solution}

Evaluator Feedback:
{evaluation_feedback}
{retry_note}
Reflect on why the attempt failed and provide structured guidance for the next try.
"""

        logger.info(
            "Reflector analyzing failure — attempt=%d", attempt_number
        )
        raw = self._client.generate_with_history(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )

        parsed = self._parse_reflection(raw)
        parsed["full_text"] = raw
        return parsed

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _parse_reflection(text: str) -> dict[str, str]:
        """Extract the four structured sections from the reflection output."""
        sections = {
            "what_went_wrong": "",
            "root_cause": "",
            "key_insight": "",
            "strategy": "",
        }

        patterns = {
            "what_went_wrong": re.compile(
                r"WHAT WENT WRONG[:\s]*(.*?)(?=ROOT CAUSE|$)", re.DOTALL | re.IGNORECASE
            ),
            "root_cause": re.compile(
                r"ROOT CAUSE[:\s]*(.*?)(?=KEY INSIGHT|$)", re.DOTALL | re.IGNORECASE
            ),
            "key_insight": re.compile(
                r"KEY INSIGHT[:\s]*(.*?)(?=STRATEGY|$)", re.DOTALL | re.IGNORECASE
            ),
            "strategy": re.compile(
                r"STRATEGY[:\s]*(.*?)$", re.DOTALL | re.IGNORECASE
            ),
        }

        for key, pattern in patterns.items():
            match = pattern.search(text)
            if match:
                sections[key] = match.group(1).strip()

        # Fallback: if no structured output, put everything in key_insight
        if not any(sections.values()):
            sections["key_insight"] = text.strip()

        return sections
