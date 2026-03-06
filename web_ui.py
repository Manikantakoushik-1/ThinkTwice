"""ThinkTwice — Interactive Streamlit Web Dashboard.

Launch with:
    streamlit run web_ui.py

This is the root-level entry point for the web dashboard.  It uses the
reusable UI components in ``ui/`` and the agent/task back-end in ``src/``.
"""

from __future__ import annotations

import os
import sys
import time

# ── Ensure project root is on sys.path so `src` and `ui` imports work ────────
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

# ── Page config (MUST be the first Streamlit call) ────────────────────────────
st.set_page_config(
    page_title="ThinkTwice — Reflexion Agent Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.styles import inject_css  # noqa: E402 — must come after set_page_config
from ui.components import (  # noqa: E402
    render_attempt_card,
    render_metric_cards,
    render_flow_diagram,
    render_benchmark_comparison,
)

inject_css()

# ── Provider metadata ─────────────────────────────────────────────────────────

_PROVIDER_META: dict[str, dict] = {
    "gemini": {
        "label": "Gemini (Google)",
        "env_var": "GEMINI_API_KEY",
        "model": "gemini-2.0-flash",
        "free_tier": "1,500 req/day · 1M tok/min",
        "get_key": "https://aistudio.google.com/apikey",
    },
    "groq": {
        "label": "Groq (Llama 3.3)",
        "env_var": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
        "free_tier": "14,400 req/day",
        "get_key": "https://console.groq.com/keys",
    },
    "huggingface": {
        "label": "HuggingFace (Mistral)",
        "env_var": "HUGGINGFACE_API_KEY",
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "free_tier": "1,000 req/day",
        "get_key": "https://huggingface.co/settings/tokens",
    },
}

_TASK_TYPE_LABELS = ["Math", "Code", "Logic", "Planning", "Custom"]


# ── Lazy back-end imports ─────────────────────────────────────────────────────

def _import_backend():
    """Import back-end modules.  Kept lazy so Streamlit can render the page
    even when some optional LLM provider libraries are missing."""
    from src.utils.llm_client import LLMClient
    from src.agent.reflexion_agent import ReflexionAgent
    from src.tasks.math_reasoning import MathTaskLoader
    from src.tasks.code_generation import CodeTaskLoader
    from src.tasks.logic_puzzles import LogicTaskLoader
    from src.tasks.planning import PlanningTaskLoader
    return (
        LLMClient,
        ReflexionAgent,
        MathTaskLoader,
        CodeTaskLoader,
        LogicTaskLoader,
        PlanningTaskLoader,
    )


# ── Session state ─────────────────────────────────────────────────────────────

def _init_session_state() -> None:
    defaults: dict = {
        "llm_client": None,
        "active_provider": None,
        "last_result": None,
        "baseline_result": None,
        "benchmark_baseline": None,
        "benchmark_reflexion": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_session_state()


# ── Helper: detect available providers from env ───────────────────────────────

def _detect_providers() -> dict[str, bool]:
    """Return {provider_id: True/False} based on whether an API key is set."""
    return {p: bool(os.getenv(meta["env_var"])) for p, meta in _PROVIDER_META.items()}


def _auto_provider() -> str | None:
    """Return the first provider that has a key set, or None."""
    for p, has_key in _detect_providers().items():
        if has_key:
            return p
    return None


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar() -> tuple[int, float]:
    """Render sidebar configuration panel.

    Returns:
        (max_attempts, temperature)
    """
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-logo">🧠 ThinkTwice</div>',
            unsafe_allow_html=True,
        )
        st.markdown("*Self-Reflecting LLM Agent*")
        st.divider()

        # ── Provider Status ────────────────────────────────────────────────
        st.markdown("### 🔑 LLM Provider")
        provider_states = _detect_providers()

        provider_options = [p for p, ok in provider_states.items() if ok]
        all_providers = list(_PROVIDER_META.keys())

        # Show status for each provider
        for p in all_providers:
            meta = _PROVIDER_META[p]
            has_key = provider_states[p]
            icon = "✅" if has_key else "❌"
            env_var = meta["env_var"]
            st.markdown(
                f"{icon} **{meta['label']}** — `{env_var}`",
                unsafe_allow_html=False,
            )

        if not provider_options:
            st.error(
                "No API key detected.  Set at least one of:\n"
                + "\n".join(f"• `{_PROVIDER_META[p]['env_var']}`" for p in all_providers)
                + "\nin your `.env` file and restart the app."
            )
        else:
            selected_provider = st.selectbox(
                "Active Provider",
                provider_options,
                format_func=lambda p: _PROVIDER_META[p]["label"],
                key="sidebar_provider",
            )

            # Initialize or reinitialize client if provider changed
            if (
                st.session_state["llm_client"] is None
                or st.session_state["active_provider"] != selected_provider
            ):
                try:
                    LLMClient, *_ = _import_backend()
                    client = LLMClient(provider=selected_provider)
                    st.session_state["llm_client"] = client
                    st.session_state["active_provider"] = selected_provider
                except Exception as exc:
                    st.error(f"Failed to initialize **{selected_provider}**: {exc}")

            if st.session_state["active_provider"]:
                meta = _PROVIDER_META[st.session_state["active_provider"]]
                st.success(
                    f"Connected — **{meta['label']}**  \n"
                    f"Model: `{meta['model']}`"
                )

        st.divider()

        # ── Agent Settings ─────────────────────────────────────────────────
        st.markdown("### ⚙️ Agent Settings")
        max_attempts = st.slider(
            "Max Attempts",
            min_value=1,
            max_value=5,
            value=3,
            key="sidebar_max_attempts",
            help="Maximum number of Attempt→Reflect iterations.",
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            key="sidebar_temperature",
            help="Informational — the Actor and Reflector use their own fixed temperatures internally.",
        )
        st.caption("ℹ️ Temperature is shown for reference; the agent uses its own internal settings.")

        st.divider()
        st.markdown(
            '<div style="font-size:0.75rem;opacity:0.5;text-align:center;">'
            "ThinkTwice · Reflexion Pattern<br>"
            '<a href="https://arxiv.org/abs/2303.11366" target="_blank">Shinn et al. 2023</a>'
            "</div>",
            unsafe_allow_html=True,
        )

    return max_attempts, temperature


# ── Task loader (cached) ──────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _load_tasks(task_type: str) -> list:
    _, _, MathTaskLoader, CodeTaskLoader, LogicTaskLoader, PlanningTaskLoader = _import_backend()
    loaders = {
        "math": MathTaskLoader,
        "code": CodeTaskLoader,
        "logic": LogicTaskLoader,
        "planning": PlanningTaskLoader,
    }
    cls = loaders.get(task_type)
    return cls().load_tasks() if cls else []


# ── Tab 1: Interactive Solver ─────────────────────────────────────────────────

def tab_interactive_solver(max_attempts: int) -> None:
    st.markdown("## 🏠 Interactive Solver")
    st.markdown(
        "Select a task, hit **🚀 Run Reflexion Loop**, and watch the agent reason "
        "through each attempt step-by-step."
    )

    if st.session_state["llm_client"] is None:
        st.warning(
            "⚠️ No LLM provider connected.  "
            "Please set an API key in your `.env` file and restart the app."
        )
        return

    # ── Task input ─────────────────────────────────────────────────────────
    st.markdown("### 1️⃣ Task Input")

    task_type_label = st.radio(
        "Task Type",
        _TASK_TYPE_LABELS,
        horizontal=True,
        key="solver_task_type",
    )

    task_description: str = ""
    expected_answer: str | None = None
    task_id: str = "custom_task"
    task_type_str: str = task_type_label.lower()
    test_code: str | None = None

    if task_type_label == "Custom":
        task_description = st.text_area(
            "Task Description",
            placeholder="Describe the task you want the agent to solve…",
            height=150,
            key="solver_custom_desc",
        )
        expected_answer = (
            st.text_input(
                "Expected Answer (optional)",
                placeholder="Leave blank to use LLM-as-judge",
                key="solver_custom_answer",
            )
            or None
        )
        task_type_str = st.selectbox(
            "Task category (for evaluation strategy)",
            ["general", "math", "logic", "planning"],
            key="solver_custom_type",
        )
    else:
        tasks = _load_tasks(task_type_str)
        if not tasks:
            st.error(f"No tasks found for type '{task_type_label}'.")
            return

        def _truncate(text: str, max_chars: int = 80) -> str:
            if len(text) <= max_chars:
                return text
            return text[:max_chars].rsplit(" ", 1)[0] + "…"

        task_labels = {f"[{t.id}] {_truncate(t.description)}": t for t in tasks}
        task_labels["✏️  Enter my own…"] = None

        selected_label = st.selectbox(
            "Select a sample task",
            list(task_labels.keys()),
            key="solver_task_select",
        )
        selected_task = task_labels[selected_label]

        if selected_task is None:
            task_description = st.text_area(
                "Custom Task Description",
                height=120,
                key="solver_custom_inline",
            )
            expected_answer = (
                st.text_input(
                    "Expected Answer (optional)",
                    key="solver_custom_inline_answer",
                )
                or None
            )
            task_id = "custom_inline"
        else:
            task_description = selected_task.description
            expected_answer = selected_task.expected_answer
            task_id = selected_task.id
            test_code = selected_task.test_code

            with st.container(border=True):
                st.markdown("**📄 Task Card**")
                st.write(f"**ID:** `{task_id}`")
                st.write(task_description)
                if expected_answer:
                    st.write(f"**Expected Answer:** `{expected_answer}`")
                if test_code:
                    with st.expander("🧪 Test Code", expanded=False):
                        st.code(test_code, language="python")

    run_clicked = st.button(
        "🚀 Run Reflexion Loop",
        type="primary",
        disabled=not bool(task_description.strip()),
        key="solver_run_btn",
    )

    # ── Live Reflexion Loop ────────────────────────────────────────────────
    if run_clicked and task_description.strip():
        _run_reflexion_loop(
            task_id=task_id,
            task_description=task_description,
            expected_answer=expected_answer,
            task_type_str=task_type_str,
            test_code=test_code,
            max_attempts=max_attempts,
        )

    # ── Results (persisted in session_state) ──────────────────────────────
    if st.session_state["last_result"] is not None:
        _render_results_section(task_type_str=task_type_str)


def _run_reflexion_loop(
    task_id: str,
    task_description: str,
    expected_answer: str | None,
    task_type_str: str,
    test_code: str | None,
    max_attempts: int,
) -> None:
    """Execute the agent and store results in session_state."""
    _, ReflexionAgent, *_ = _import_backend()
    client = st.session_state["llm_client"]

    st.markdown("---")
    st.markdown("### 2️⃣ Reflexion Loop")

    progress_bar = st.progress(0, text="Starting Reflexion loop…")
    status_box = st.empty()

    try:
        agent = ReflexionAgent(llm_client=client, max_attempts=max_attempts)
        status_box.info(
            f"⏳ Running Reflexion agent — up to {max_attempts} attempt(s)…"
        )
        start_ts = time.time()

        result = agent.solve(
            task_id=task_id,
            task_description=task_description,
            expected_answer=expected_answer,
            task_type=task_type_str,
            test_code=test_code,
        )

        elapsed = time.time() - start_ts
        progress_bar.progress(100, text=f"Completed in {elapsed:.1f}s")
        status_box.empty()

        st.session_state["last_result"] = result

        # Also run baseline (1 attempt) for comparison
        baseline_agent = ReflexionAgent(llm_client=client, max_attempts=1)
        baseline_result = baseline_agent.solve(
            task_id=task_id,
            task_description=task_description,
            expected_answer=expected_answer,
            task_type=task_type_str,
            test_code=test_code,
        )
        st.session_state["baseline_result"] = baseline_result

    except Exception as exc:
        progress_bar.empty()
        status_box.error(f"❌ Agent error: {exc}")
        st.exception(exc)
        return

    # ── Per-attempt timeline ───────────────────────────────────────────────
    eval_history = result.evaluation_history
    reflections = result.reflections

    for i, eval_entry in enumerate(eval_history):
        attempt_num = eval_entry.get("attempt", i + 1)
        reflection = reflections[i] if i < len(reflections) else None

        # ReflexionAgent only stores the final solution; display it on the
        # last attempt and a placeholder for earlier ones.
        if attempt_num == result.attempts:
            solution = result.final_solution
        else:
            solution = (
                f"[Attempt {attempt_num} — intermediate solution. "
                "Full final solution shown in Results Summary below.]"
            )

        render_attempt_card(
            attempt_num=attempt_num,
            solution=solution,
            eval_result=eval_entry,
            reflection=reflection,
        )

        if attempt_num < result.attempts:
            st.markdown(
                '<div class="flow-arrow">⬇️ Reflecting… ⬇️</div>',
                unsafe_allow_html=True,
            )


def _render_results_section(task_type_str: str) -> None:
    result = st.session_state["last_result"]
    baseline = st.session_state.get("baseline_result")

    st.markdown("---")
    st.markdown("### 3️⃣ Results Summary")

    # ── Metric cards ───────────────────────────────────────────────────────
    render_metric_cards(result)

    # ── Outcome message ────────────────────────────────────────────────────
    if result.is_correct and result.attempts > 1:
        st.markdown(
            '<div class="success-banner">'
            "🎯 Self-reflection improved the result! "
            f"Solved after {result.attempts} attempt(s)."
            "</div>",
            unsafe_allow_html=True,
        )
    elif result.is_correct:
        st.success("🎉 Solved on the first attempt!")
    else:
        st.error(
            f"The agent could not solve this task within {result.max_attempts} attempt(s)."
        )

    # ── Final solution ─────────────────────────────────────────────────────
    with st.expander("📝 Final Solution", expanded=True):
        sol = result.final_solution
        is_code = any(
            sol.lstrip().startswith(kw)
            for kw in ("def ", "class ", "import ", "from ", "#", "```")
        )
        if is_code:
            clean = (
                sol.strip()
                .removeprefix("```python")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            st.code(clean, language="python")
        else:
            st.write(sol)

    # ── Baseline vs Reflexion comparison ──────────────────────────────────
    if baseline is not None:
        st.markdown("---")
        st.markdown("### 4️⃣ Baseline vs Reflexion Comparison")
        st.markdown(
            "Side-by-side view: **Without Reflection** (1 attempt) vs "
            "**With Reflection** (up to N attempts)."
        )

        col_base, col_refx = st.columns(2)
        with col_base:
            outcome = "✅ Correct" if baseline.is_correct else "❌ Incorrect"
            st.markdown(
                f"""
                <div class="metric-card {'success' if baseline.is_correct else 'failure'}">
                    <div class="metric-value">{outcome}</div>
                    <div class="metric-label">Without Reflection (baseline)</div>
                    <div style="font-size:0.8rem;opacity:0.7;margin-top:0.4rem;">
                        Score: {baseline.score:.0%} · {baseline.attempts} attempt
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_refx:
            outcome = "✅ Correct" if result.is_correct else "❌ Incorrect"
            delta = result.score - baseline.score
            delta_str = f"+{delta:.0%}" if delta >= 0 else f"{delta:.0%}"
            st.markdown(
                f"""
                <div class="metric-card {'success' if result.is_correct else 'failure'}">
                    <div class="metric-value">{outcome}</div>
                    <div class="metric-label">With Reflection</div>
                    <div style="font-size:0.8rem;opacity:0.7;margin-top:0.4rem;">
                        Score: {result.score:.0%} · {result.attempts}/{result.max_attempts} attempts
                        · Δ score: {delta_str}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if result.is_correct and not baseline.is_correct:
            st.markdown(
                '<div class="success-banner">'
                "🚀 Reflection loop FIXED this task!  "
                "The baseline failed but Reflexion succeeded."
                "</div>",
                unsafe_allow_html=True,
            )


# ── Tab 2: Batch Benchmark ────────────────────────────────────────────────────

def tab_batch_benchmark(max_attempts: int) -> None:
    st.markdown("## 📊 Batch Benchmark")
    st.markdown(
        "Compare **Baseline** (1 attempt, no reflection) vs **Reflexion** "
        "(up to N attempts) across multiple tasks."
    )

    if st.session_state["llm_client"] is None:
        st.warning("⚠️ No LLM provider connected.  Please set an API key and restart.")
        return

    col_settings, col_results = st.columns([1, 2])

    with col_settings:
        st.markdown("#### ⚙️ Benchmark Settings")
        selected_types = st.multiselect(
            "Task Types",
            ["Math", "Code", "Logic", "Planning"],
            default=["Math"],
            key="bench_types",
        )
        num_tasks = st.slider(
            "Tasks per Type",
            min_value=1,
            max_value=5,
            value=2,
            key="bench_num_tasks",
        )
        run_benchmark = st.button(
            "▶️ Run Benchmark",
            type="primary",
            use_container_width=True,
            key="bench_run_btn",
        )

    with col_results:
        if st.session_state["benchmark_baseline"] is not None:
            render_benchmark_comparison(
                st.session_state["benchmark_baseline"],
                st.session_state["benchmark_reflexion"],
            )

    if run_benchmark:
        if not selected_types:
            st.warning("Please select at least one task type.")
            return

        _, ReflexionAgent, *_ = _import_backend()
        client = st.session_state["llm_client"]

        all_tasks: list = []
        for type_label in selected_types:
            tasks = _load_tasks(type_label.lower())
            all_tasks.extend(tasks[:num_tasks])

        if not all_tasks:
            st.error("No tasks available for the selected types.")
            return

        total = len(all_tasks)
        progress = st.progress(0, text="Running baseline…")
        baseline_results: list = []
        reflexion_results: list = []

        # Baseline (1 attempt)
        baseline_agent = ReflexionAgent(llm_client=client, max_attempts=1)
        for idx, task in enumerate(all_tasks):
            progress.progress(
                int((idx / (total * 2)) * 100),
                text=f"Baseline {idx + 1}/{total}: {task.id}",
            )
            try:
                res = baseline_agent.solve(
                    task_id=task.id,
                    task_description=task.description,
                    expected_answer=task.expected_answer,
                    task_type=task.task_type,
                    test_code=task.test_code,
                )
                baseline_results.append(res)
                baseline_agent.reset()
            except Exception as exc:
                st.warning(f"Baseline failed for {task.id}: {exc}")

        # Reflexion (N attempts)
        reflexion_agent = ReflexionAgent(llm_client=client, max_attempts=max_attempts)
        for idx, task in enumerate(all_tasks):
            progress.progress(
                int(((total + idx) / (total * 2)) * 100),
                text=f"Reflexion {idx + 1}/{total}: {task.id}",
            )
            try:
                res = reflexion_agent.solve(
                    task_id=task.id,
                    task_description=task.description,
                    expected_answer=task.expected_answer,
                    task_type=task.task_type,
                    test_code=task.test_code,
                )
                reflexion_results.append(res)
                reflexion_agent.reset()
            except Exception as exc:
                st.warning(f"Reflexion failed for {task.id}: {exc}")

        progress.progress(100, text="Benchmark complete!")
        st.session_state["benchmark_baseline"] = baseline_results
        st.session_state["benchmark_reflexion"] = reflexion_results
        st.rerun()


# ── Tab 3: Architecture ───────────────────────────────────────────────────────

def tab_architecture() -> None:
    st.markdown("## 🏗️ How It Works")
    st.markdown(
        "ThinkTwice implements the **Reflexion** pattern from "
        "[Shinn et al. (2023)](https://arxiv.org/abs/2303.11366)."
    )

    st.markdown("### 🔄 The Reflexion Loop")
    render_flow_diagram()

    st.markdown("### 🧩 Components")

    _COMPONENTS = [
        (
            "🎭 Actor",
            "Generates a solution to the task using the LLM.  On retries the "
            "Actor's prompt is augmented with structured reflections from memory.",
            "src/agent/actor.py",
        ),
        (
            "⚖️ Evaluator",
            "Checks correctness via three strategies: exact numeric match (math), "
            "code execution + test assertions (code), or LLM-as-judge (logic/planning).",
            "src/agent/evaluator.py",
        ),
        (
            "🔍 Reflector",
            "On failure, prompts the LLM to produce a structured analysis: "
            "What Went Wrong, Root Cause, Key Insight, Strategy for next attempt.",
            "src/agent/reflector.py",
        ),
        (
            "🧠 Episodic Memory",
            "Stores structured reflections keyed by task ID.  Provides formatted "
            "context to inject into the Actor's next prompt.",
            "src/memory/episodic_memory.py",
        ),
        (
            "🔌 LLM Client",
            "Unified multi-provider client supporting Gemini, Groq, and HuggingFace.  "
            "Auto-detects provider from environment variables.",
            "src/utils/llm_client.py",
        ),
        (
            "🤖 Reflexion Agent",
            "Orchestrates the full Attempt → Evaluate → Reflect → Retry loop, "
            "calling each component in sequence up to max_attempts.",
            "src/agent/reflexion_agent.py",
        ),
    ]

    cols = st.columns(2)
    for i, (title, desc, path) in enumerate(_COMPONENTS):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="arch-card" style="margin-bottom:1rem;">
                    <h3>{title}</h3>
                    <p>{desc}</p>
                    <p><code>{path}</code></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### 📚 Free API Providers")
    st.table(
        {
            "Provider": [m["label"] for m in _PROVIDER_META.values()],
            "Free Tier": [m["free_tier"] for m in _PROVIDER_META.values()],
            "Env Variable": [m["env_var"] for m in _PROVIDER_META.values()],
            "Get Key": [m["get_key"] for m in _PROVIDER_META.values()],
        }
    )

    st.markdown("### 📖 Reference")
    st.markdown(
        "> **Reflexion: Language Agents with Verbal Reinforcement Learning**  \n"
        "> Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, "
        "Karthik Narasimhan, Shunyu Yao  \n"
        "> [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    max_attempts, _temperature = render_sidebar()

    tab1, tab2, tab3 = st.tabs(
        ["🏠 Interactive Solver", "📊 Batch Benchmark", "🏗️ How It Works"]
    )

    with tab1:
        tab_interactive_solver(max_attempts)

    with tab2:
        tab_batch_benchmark(max_attempts)

    with tab3:
        tab_architecture()


if __name__ == "__main__":
    main()
