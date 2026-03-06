"""Evaluator — checks correctness of agent solutions (Critic)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile

from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

EvalResult = dict  # {is_correct: bool, score: float, feedback: str, errors: list[str]}


class Evaluator:
    """Evaluates solutions using exact-match, code execution, or LLM-as-judge.

    Args:
        llm_client: Used for LLM-as-judge evaluation mode.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self._client = llm_client

    def evaluate(
        self,
        solution: str,
        expected_answer: str | None,
        task_type: str = "general",
        task_description: str = "",
        test_code: str | None = None,
    ) -> EvalResult:
        """Dispatch to the appropriate evaluation strategy.

        Returns:
            A dict with keys ``is_correct``, ``score``, ``feedback``, ``errors``.
        """
        if task_type == "math":
            return self._evaluate_math(solution, expected_answer or "")
        if task_type == "code":
            return self._evaluate_code(solution, test_code or "")
        if task_type in ("logic", "planning") or expected_answer is None:
            return self._evaluate_with_llm(solution, task_description, expected_answer)
        # Default: exact/numeric match
        return self._evaluate_math(solution, expected_answer)

    # ── Math evaluation ───────────────────────────────────────────────────────

    def _evaluate_math(self, solution: str, expected_answer: str) -> EvalResult:
        """Extract 'FINAL ANSWER:' from solution and compare numerically."""
        pattern = re.compile(r"FINAL ANSWER[:\s]+(.+)", re.IGNORECASE)
        match = pattern.search(solution)

        if not match:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "No 'FINAL ANSWER:' found in the solution.",
                "errors": ["missing_final_answer"],
            }

        raw = match.group(1).strip()
        predicted = self._normalize_number(raw)
        expected = self._normalize_number(expected_answer)

        if predicted is None or expected is None:
            # Fall back to string comparison
            is_correct = raw.lower() == expected_answer.strip().lower()
            return {
                "is_correct": is_correct,
                "score": 1.0 if is_correct else 0.0,
                "feedback": f"Predicted: '{raw}', Expected: '{expected_answer}'",
                "errors": [] if is_correct else ["wrong_answer"],
            }

        is_correct = abs(predicted - expected) < 1e-6
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": f"Predicted: {predicted}, Expected: {expected}",
            "errors": [] if is_correct else ["wrong_answer"],
        }

    @staticmethod
    def _normalize_number(text: str) -> float | None:
        """Parse a number string, removing commas and currency symbols."""
        cleaned = re.sub(r"[,$£€]", "", text.strip())
        # Take the first numeric token
        match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None

    # ── Code evaluation ───────────────────────────────────────────────────────

    def _evaluate_code(self, solution: str, test_code: str) -> EvalResult:
        """Extract Python code from the solution and run it with test assertions."""
        code = self._extract_code(solution)
        if not code:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "No Python code block found in the solution.",
                "errors": ["no_code_found"],
            }

        full_code = f"{code}\n\n# ── Tests ──\n{test_code}"

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as tmp:
                tmp.write(full_code)
                tmp_path = tmp.name

            result = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Code execution timed out (30s limit).",
                "errors": ["timeout"],
            }
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        if result.returncode == 0:
            return {
                "is_correct": True,
                "score": 1.0,
                "feedback": "All tests passed.",
                "errors": [],
            }

        stderr = result.stderr.strip()
        return {
            "is_correct": False,
            "score": 0.0,
            "feedback": f"Tests failed.\n{stderr}",
            "errors": [stderr[:500]],
        }

    @staticmethod
    def _extract_code(solution: str) -> str:
        """Extract the first ```python ... ``` block, or bare code if none found."""
        pattern = re.compile(r"```python\s*(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(solution)
        if match:
            return match.group(1).strip()
        # Try generic code fence
        generic = re.compile(r"```\s*(.*?)```", re.DOTALL)
        match = generic.search(solution)
        if match:
            return match.group(1).strip()
        return ""

    # ── LLM-as-judge evaluation ───────────────────────────────────────────────

    def _evaluate_with_llm(
        self,
        solution: str,
        task_description: str,
        expected_answer: str | None,
    ) -> EvalResult:
        """Use the LLM to judge correctness; returns structured JSON."""
        expected_section = (
            f"Expected answer: {expected_answer}" if expected_answer else "No reference answer provided — judge quality and completeness."
        )
        prompt = f"""\
You are a strict evaluator. Assess whether the solution correctly answers the task.

Task:
{task_description}

{expected_section}

Solution to evaluate:
{solution}

Respond ONLY with valid JSON in this exact format (no markdown fences):
{{
  "is_correct": true or false,
  "score": 0.0 to 1.0,
  "feedback": "brief explanation",
  "errors": ["list", "of", "issues"]
}}
"""
        try:
            raw = self._client.generate(prompt, temperature=0.0)
            # Strip possible markdown fences
            raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
            raw = re.sub(r"\s*```$", "", raw.strip())
            data = json.loads(raw)
            return {
                "is_correct": bool(data.get("is_correct", False)),
                "score": float(data.get("score", 0.0)),
                "feedback": str(data.get("feedback", "")),
                "errors": list(data.get("errors", [])),
            }
        except Exception as exc:
            logger.warning("LLM-as-judge failed: %s", exc)
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": f"Evaluation error: {exc}",
                "errors": [str(exc)],
            }
