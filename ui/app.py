"""ThinkTwice — Interactive Streamlit Dashboard.

Launch with:
    streamlit run ui/app.py
"""

from __future__ import annotations

import os
import sys
import time

# ── Ensure project root is on sys.path so `src` imports work ─────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

from ui.styles import inject_css
from ui.components import (
    render_attempt_card,
    render_metric_cards,
    render_flow_diagram,
    render_benchmark_comparison,
)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="ThinkTwice — Self-Reflecting AI Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Lazy imports from src (only after path is set up) ────────────────────────

def _import_backend():
    """Import backend modules lazily so Streamlit can start before all deps are confirmed."""
    from src.utils.llm_client import LLMClient
    from src.agent.reflexion_agent import ReflexionAgent
    from src.tasks.math_reasoning import MathTaskLoader
    from src.tasks.code_generation import CodeTaskLoader
    from src.tasks.logic_puzzles import LogicTaskLoader
    from src.tasks.planning import PlanningTaskLoader
    return LLMClient, ReflexionAgent, MathTaskLoader, CodeTaskLoader, LogicTaskLoader, PlanningTaskLoader


# ── Provider constants ────────────────────────────────────────────────────────

PROVIDER_OPTIONS = {
    "Gemini (Google)": "gemini",
    "Groq (Llama 3.3)": "groq",
    "HuggingFace (Mistral)": "huggingface",
}

PROVIDER_ENV_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "huggingface": "HUGGINGFACE_API_KEY",
}

TASK_TYPE_LABELS = ["Math", "Code", "Logic", "Planning", "Custom"]

# ── Session state helpers ─────────────────────────────────────────────────────

def _init_session_state() -> None:
    defaults = {
        "llm_client": None,
        "provider_name": None,
        "connected": False,
        "last_result": None,
        "benchmark_baseline": None,
        "benchmark_reflexion": None,
        "page": "🏠 Interactive Solver",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_session_state()


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar() -> int:
    """Render sidebar; returns selected max_attempts."""
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🧠 ThinkTwice</div>', unsafe_allow_html=True)
        st.markdown("*Self-Reflecting LLM Agent*")
        st.divider()

        # ── API Key Configuration ──────────────────────────────────────────
        st.markdown("### 🔑 API Key Configuration")
        provider_label = st.selectbox(
            "Provider",
            list(PROVIDER_OPTIONS.keys()),
            key="sidebar_provider",
        )
        provider = PROVIDER_OPTIONS[provider_label]
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder=f"Enter your {provider_label} key",
            key="sidebar_api_key",
        )

        if st.button("🔗 Connect", use_container_width=True):
            if not api_key.strip():
                st.error("Please enter an API key.")
            else:
                env_var = PROVIDER_ENV_KEYS[provider]
                os.environ[env_var] = api_key.strip()
                os.environ["LLM_PROVIDER"] = provider
                try:
                    LLMClient, *_ = _import_backend()
                    client = LLMClient(provider=provider)
                    st.session_state["llm_client"] = client
                    st.session_state["provider_name"] = provider
                    st.session_state["connected"] = True
                    st.success(f"✅ Connected to **{provider_label}**!")
                except Exception as exc:
                    st.session_state["connected"] = False
                    st.error(f"Connection failed: {exc}")

        if st.session_state["connected"]:
            st.markdown(
                f"✅ **Connected:** `{st.session_state['provider_name']}`",
            )

        st.divider()

        # ── Agent Settings ─────────────────────────────────────────────────
        st.markdown("### ⚙️ Agent Settings")
        max_attempts = st.slider("Max Attempts", min_value=1, max_value=5, value=3, key="sidebar_max_attempts")

        st.divider()

        # ── Navigation ─────────────────────────────────────────────────────
        st.markdown("### 📍 Navigation")
        pages = ["🏠 Interactive Solver", "📊 Benchmark Dashboard", "🏗️ Architecture"]
        for page in pages:
            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                st.session_state["page"] = page

        st.divider()
        st.markdown(
            '<div style="font-size:0.75rem;opacity:0.5;text-align:center;">'
            'ThinkTwice · Reflexion Pattern<br>'
            '<a href="https://arxiv.org/abs/2303.11366" target="_blank">Shinn et al. 2023</a>'
            "</div>",
            unsafe_allow_html=True,
        )

    return max_attempts


# ── Helper: load sample tasks ─────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _load_tasks(task_type: str) -> list:
    _, _, MathTaskLoader, CodeTaskLoader, LogicTaskLoader, PlanningTaskLoader = _import_backend()
    loaders = {
        "math": MathTaskLoader,
        "code": CodeTaskLoader,
        "logic": LogicTaskLoader,
        "planning": PlanningTaskLoader,
    }
    loader_cls = loaders.get(task_type)
    if loader_cls is None:
        return []
    return loader_cls().load_tasks()


# ── Page 1: Interactive Solver ────────────────────────────────────────────────

def page_interactive_solver(max_attempts: int) -> None:
    st.title("🏠 Interactive Solver")
    st.markdown(
        "Select a task, click **Solve with Reflexion**, and watch the agent reason through "
        "each attempt step-by-step."
    )

    if not st.session_state["connected"]:
        st.warning("⚠️ Please connect an API key in the sidebar before solving tasks.")
        return

    # ── Section 1: Task Input ──────────────────────────────────────────────
    st.markdown("## 1️⃣ Task Input")

    task_type_label = st.radio(
        "Task Type",
        TASK_TYPE_LABELS,
        horizontal=True,
        key="solver_task_type",
    )

    task_description = ""
    expected_answer = None
    task_id = "custom_task"
    task_type_str = task_type_label.lower()
    test_code = None

    if task_type_label == "Custom":
        task_description = st.text_area(
            "Task Description",
            placeholder="Describe the task you want the agent to solve…",
            height=150,
            key="solver_custom_desc",
        )
        expected_answer = st.text_input(
            "Expected Answer (optional)",
            placeholder="Leave blank to use LLM-as-judge",
            key="solver_custom_answer",
        ) or None
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
            """Truncate at word boundary to avoid cutting in the middle of a word."""
            if len(text) <= max_chars:
                return text
            truncated = text[:max_chars].rsplit(" ", 1)[0]
            return truncated + "…"

        task_labels = {f"[{t.id}] {_truncate(t.description)}": t for t in tasks}
        # Also allow custom text
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
            expected_answer = st.text_input(
                "Expected Answer (optional)",
                key="solver_custom_inline_answer",
            ) or None
            task_id = "custom_inline"
        else:
            task_description = selected_task.description
            expected_answer = selected_task.expected_answer
            task_id = selected_task.id
            test_code = selected_task.test_code
            with st.expander("📄 Task Details", expanded=False):
                st.write(f"**ID:** `{task_id}`")
                st.write(f"**Description:** {task_description}")
                if expected_answer:
                    st.write(f"**Expected Answer:** `{expected_answer}`")
                if test_code:
                    st.code(test_code, language="python")

    solve_clicked = st.button(
        "🚀 Solve with Reflexion",
        type="primary",
        use_container_width=False,
        disabled=not bool(task_description.strip()),
    )

    # ── Section 2: Live Reflexion Loop ─────────────────────────────────────
    if solve_clicked and task_description.strip():
        _, ReflexionAgent, *_ = _import_backend()
        LLMClient = _import_backend()[0]

        st.markdown("---")
        st.markdown("## 2️⃣ Reflexion Loop")

        client: object = st.session_state["llm_client"]

        progress_bar = st.progress(0, text="Starting Reflexion loop…")
        status_placeholder = st.empty()

        try:
            agent = ReflexionAgent(llm_client=client, max_attempts=max_attempts)

            status_placeholder.info("⏳ Running Reflexion agent… (this may take a moment)")
            start_ts = time.time()

            result = agent.solve(
                task_id=task_id,
                task_description=task_description,
                expected_answer=expected_answer or None,
                task_type=task_type_str,
                test_code=test_code,
            )
            elapsed = time.time() - start_ts
            progress_bar.progress(100, text=f"Completed in {elapsed:.1f}s")
            status_placeholder.empty()

            st.session_state["last_result"] = result

        except Exception as exc:
            progress_bar.empty()
            status_placeholder.error(f"❌ Agent error: {exc}")
            st.exception(exc)
            return

        # ── Display each attempt ───────────────────────────────────────────
        eval_history = result.evaluation_history
        reflections = result.reflections

        for i, eval_entry in enumerate(eval_history):
            attempt_num = eval_entry.get("attempt", i + 1)

            # Match reflection to this attempt (reflection is generated after each failed attempt)
            reflection = reflections[i] if i < len(reflections) else None

            # AgentResult only stores the final solution, not intermediate ones (by design —
            # ReflexionAgent overwrites last_solution on each attempt). We display the full
            # final solution for the last attempt; earlier attempts show a note directing the
            # user to the Results Summary section below.
            if attempt_num == result.attempts:
                solution = result.final_solution
            else:
                solution = (
                    f"[Attempt {attempt_num} solution — full final solution shown in Results Summary below]"
                )

            render_attempt_card(
                attempt_num=attempt_num,
                solution=solution,
                eval_result=eval_entry,
                reflection=reflection,
            )

            # Visual arrow between attempts
            if attempt_num < result.attempts:
                st.markdown(
                    '<div class="flow-arrow">⬇️ Reflecting… ⬇️</div>',
                    unsafe_allow_html=True,
                )

    # ── Section 3: Results Summary ──────────────────────────────────────────
    if st.session_state["last_result"] is not None:
        result = st.session_state["last_result"]
        st.markdown("---")
        st.markdown("## 3️⃣ Results Summary")
        render_metric_cards(result)

        # Highlight self-reflection improvement
        if result.is_correct and result.attempts > 1:
            st.markdown(
                '<div class="success-banner">'
                "🎯 Self-reflection improved the result! "
                f"Solved after {result.attempts} attempts."
                "</div>",
                unsafe_allow_html=True,
            )
        elif result.is_correct and result.attempts == 1:
            st.success("🎉 Solved on the first attempt!")
        else:
            st.error(
                f"The agent could not solve this task within {result.max_attempts} attempts."
            )

        with st.expander("📝 Final Solution", expanded=True):
            is_code = any(
                result.final_solution.lstrip().startswith(kw)
                for kw in ("def ", "class ", "import ", "from ", "#", "```")
            )
            if is_code:
                clean = (
                    result.final_solution.strip()
                    .removeprefix("```python")
                    .removeprefix("```")
                    .removesuffix("```")
                    .strip()
                )
                st.code(clean, language="python")
            else:
                st.write(result.final_solution)


# ── Page 2: Benchmark Dashboard ───────────────────────────────────────────────

def page_benchmark_dashboard(max_attempts: int) -> None:
    st.title("📊 Benchmark Dashboard")
    st.markdown(
        "Compare **Baseline** (1 attempt, no reflection) against "
        "**Reflexion** (up to N attempts) on selected task sets."
    )

    if not st.session_state["connected"]:
        st.warning("⚠️ Please connect an API key in the sidebar before running benchmarks.")
        return

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("### ⚙️ Benchmark Settings")
        selected_types = st.multiselect(
            "Task Types",
            ["Math", "Code", "Logic", "Planning"],
            default=["Math"],
            key="bench_types",
        )
        num_tasks = st.slider("Tasks per Type", min_value=1, max_value=5, value=2, key="bench_num_tasks")
        run_benchmark = st.button("▶️ Run Benchmark", type="primary", use_container_width=True)

    with col_right:
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

        all_tasks = []
        for type_label in selected_types:
            tasks = _load_tasks(type_label.lower())
            all_tasks.extend(tasks[:num_tasks])

        if not all_tasks:
            st.error("No tasks available for the selected types.")
            return

        total = len(all_tasks)
        progress = st.progress(0, text="Running baseline…")
        baseline_results = []
        reflexion_results = []

        # ── Baseline (1 attempt) ───────────────────────────────────────────
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

        # ── Reflexion (N attempts) ─────────────────────────────────────────
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


# ── Page 3: Architecture ──────────────────────────────────────────────────────

def page_architecture() -> None:
    st.title("🏗️ Architecture")
    st.markdown(
        "ThinkTwice implements the **Reflexion** pattern from "
        "[Shinn et al. (2023)](https://arxiv.org/abs/2303.11366)."
    )

    st.markdown("## 🔄 The Reflexion Loop")
    render_flow_diagram()

    st.markdown("## 🧩 Components")
    cols = st.columns(2)

    components_info = [
        (
            "🎭 Actor",
            "Generates a solution to the task using the LLM. On retries, the Actor's "
            "prompt is augmented with structured reflections from memory.",
            "src/agent/actor.py",
        ),
        (
            "⚖️ Evaluator",
            "Checks correctness using one of three strategies: exact numeric match "
            "(math), code execution with test assertions (code), or LLM-as-judge "
            "(logic/planning).",
            "src/agent/evaluator.py",
        ),
        (
            "🔍 Reflector",
            "On failure, prompts the LLM to produce a structured analysis: "
            "What Went Wrong, Root Cause, Key Insight, and Strategy for next attempt.",
            "src/agent/reflector.py",
        ),
        (
            "🧠 Episodic Memory",
            "Stores structured reflections keyed by task ID. Provides formatted "
            "context to inject into the Actor's next prompt.",
            "src/memory/episodic_memory.py",
        ),
        (
            "🔌 LLM Client",
            "Unified multi-provider client supporting Google Gemini, Groq, and "
            "HuggingFace. Auto-detects provider from environment variables.",
            "src/utils/llm_client.py",
        ),
        (
            "🤖 Reflexion Agent",
            "Orchestrates the full Attempt → Evaluate → Reflect → Retry loop, "
            "calling each component in sequence and capping iterations at max_attempts.",
            "src/agent/reflexion_agent.py",
        ),
    ]

    for i, (title, desc, path) in enumerate(components_info):
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

    st.markdown("## 📚 Free API Providers")
    st.table(
        {
            "Provider": ["Google Gemini", "Groq (Llama 3.3)", "HuggingFace (Mistral)"],
            "Free Tier": ["1,500 req/day · 1M tok/min", "14,400 req/day", "1,000 req/day"],
            "Env Variable": ["GEMINI_API_KEY", "GROQ_API_KEY", "HUGGINGFACE_API_KEY"],
            "Get Key": [
                "https://aistudio.google.com/apikey",
                "https://console.groq.com/keys",
                "https://huggingface.co/settings/tokens",
            ],
        }
    )

    st.markdown("## 📖 Reference")
    st.markdown(
        "> **Reflexion: Language Agents with Verbal Reinforcement Learning**  \n"
        "> Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao  \n"
        "> [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)"
    )


# ── Main entry point ──────────────────────────────────────────────────────────

def main() -> None:
    max_attempts = render_sidebar()
    page = st.session_state.get("page", "🏠 Interactive Solver")

    if page == "🏠 Interactive Solver":
        page_interactive_solver(max_attempts)
    elif page == "📊 Benchmark Dashboard":
        page_benchmark_dashboard(max_attempts)
    elif page == "🏗️ Architecture":
        page_architecture()
    else:
        page_interactive_solver(max_attempts)


if __name__ == "__main__":
    main()
