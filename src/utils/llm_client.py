"""Multi-provider LLM client supporting Google Gemini, Groq, and HuggingFace.

All three providers offer FREE tiers:
- Gemini:      1,500 req/day — https://aistudio.google.com/apikey
- Groq:       14,400 req/day — https://console.groq.com/keys
- HuggingFace: 1,000 req/day — https://huggingface.co/settings/tokens
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod

from dotenv import load_dotenv

from src.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

# ── Default models per provider ──────────────────────────────────────────────
DEFAULT_MODELS: dict[str, str] = {
    "gemini": "gemini-2.0-flash",
    "groq": "llama-3.3-70b-versatile",
    "huggingface": "mistralai/Mistral-7B-Instruct-v0.3",
}

# Rate-limit guard: pause (seconds) when approaching free-tier limits
_RATE_LIMIT_PAUSE = 1.0


# ── Base provider ABC ────────────────────────────────────────────────────────

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Generate a response for a single prompt."""

    @abstractmethod
    def generate_with_history(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a response given a conversation history."""


# ── Gemini provider ──────────────────────────────────────────────────────────

class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider via ``google-generativeai``."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODELS["gemini"]) -> None:
        import google.generativeai as genai  # type: ignore[import]

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self._model_name = model

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        import google.generativeai as genai  # type: ignore[import]

        config = genai.GenerationConfig(temperature=temperature, max_output_tokens=max_tokens)
        response = self._model.generate_content(prompt, generation_config=config)
        return response.text

    def generate_with_history(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        import google.generativeai as genai  # type: ignore[import]

        # Convert OpenAI-style messages to Gemini history format
        history = []
        system_prompt = ""
        for msg in messages[:-1]:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})

        last_user_content = messages[-1]["content"]
        if system_prompt:
            last_user_content = f"{system_prompt}\n\n{last_user_content}"

        config = genai.GenerationConfig(temperature=temperature, max_output_tokens=max_tokens)
        chat = self._model.start_chat(history=history)
        response = chat.send_message(last_user_content, generation_config=config)
        return response.text


# ── Groq provider ────────────────────────────────────────────────────────────

class GroqProvider(BaseLLMProvider):
    """Groq provider via the ``groq`` package."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODELS["groq"]) -> None:
        from groq import Groq  # type: ignore[import]

        self._client = Groq(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        return self.generate_with_history(
            [{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def generate_with_history(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""


# ── HuggingFace provider ─────────────────────────────────────────────────────

class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace Inference API provider via ``huggingface-hub``."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODELS["huggingface"]) -> None:
        from huggingface_hub import InferenceClient  # type: ignore[import]

        self._client = InferenceClient(model=model, token=api_key)
        self._model = model

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        response = self._client.text_generation(
            prompt,
            max_new_tokens=max_tokens,
            temperature=max(temperature, 0.01),
        )
        return response

    def generate_with_history(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        # Build a simple conversational prompt from message history
        parts: list[str] = []
        for msg in messages:
            role = msg["role"].capitalize()
            parts.append(f"{role}: {msg['content']}")
        parts.append("Assistant:")
        prompt = "\n".join(parts)
        return self.generate(prompt, temperature=temperature, max_tokens=max_tokens)


# ── Provider registry ────────────────────────────────────────────────────────

PROVIDER_CLASSES: dict[str, type[BaseLLMProvider]] = {
    "gemini": GeminiProvider,
    "groq": GroqProvider,
    "huggingface": HuggingFaceProvider,
}

_ENV_KEYS: dict[str, str] = {
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "huggingface": "HUGGINGFACE_API_KEY",
}


# ── Main LLMClient ───────────────────────────────────────────────────────────

class LLMClient:
    """Unified LLM client that auto-detects or accepts an explicit provider.

    Usage::

        client = LLMClient()                   # auto-detect from env
        client = LLMClient(provider="groq")    # explicit provider
        text = client.generate("Hello!")
    """

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        if provider is None:
            provider = os.getenv("LLM_PROVIDER") or self._auto_detect_provider()

        provider = provider.lower()
        if provider not in PROVIDER_CLASSES:
            raise ValueError(
                f"Unknown provider '{provider}'. Choose from: {list(PROVIDER_CLASSES)}"
            )

        api_key = os.getenv(_ENV_KEYS[provider], "")
        if not api_key:
            raise EnvironmentError(
                f"No API key found for provider '{provider}'. "
                f"Set the {_ENV_KEYS[provider]} environment variable."
            )

        selected_model = model or DEFAULT_MODELS[provider]
        self._provider_name = provider
        self._provider: BaseLLMProvider = PROVIDER_CLASSES[provider](
            api_key=api_key, model=selected_model
        )
        self.total_tokens_used: int = 0
        self._request_count: int = 0
        logger.info("LLMClient initialized — provider=%s model=%s", provider, selected_model)

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a response for a single prompt string."""
        self._rate_limit_guard()
        response = self._provider.generate(
            prompt, temperature=temperature, max_tokens=max_tokens
        )
        self._request_count += 1
        # Approximate token count using whitespace split (not exact tokenization)
        self.total_tokens_used += len(response.split())
        return response

    def generate_with_history(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a response given a list of ``{role, content}`` messages."""
        self._rate_limit_guard()
        response = self._provider.generate_with_history(
            messages, temperature=temperature, max_tokens=max_tokens
        )
        self._request_count += 1
        # Approximate token count using whitespace split (not exact tokenization)
        self.total_tokens_used += len(response.split())
        return response

    @property
    def provider_name(self) -> str:
        return self._provider_name

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _auto_detect_provider() -> str:
        """Return the name of the first provider whose API key is set."""
        for name, env_var in _ENV_KEYS.items():
            if os.getenv(env_var):
                logger.info("Auto-detected provider: %s", name)
                return name
        raise EnvironmentError(
            "No LLM API key found. Please set one of: "
            + ", ".join(_ENV_KEYS.values())
        )

    def _rate_limit_guard(self) -> None:
        """Briefly pause every 50 requests to avoid free-tier rate limits."""
        if self._request_count > 0 and self._request_count % 50 == 0:
            logger.info("Rate-limit guard: pausing %.1fs after %d requests", _RATE_LIMIT_PAUSE, self._request_count)
            time.sleep(_RATE_LIMIT_PAUSE)
