"""Reusable UI components for the ThinkTwice Streamlit dashboard."""

from __future__ import annotations

import streamlit as st


# ── Single attempt card ───────────────────────────────────────────────────────

def render_attempt_card(
    attempt_num: int,
    solution: str,
    eval_result: dict,
    reflection: dict | None = None,
) -> None:
    """Render a single reflexion attempt as a styled expander."""
    is_correct = eval_result.get("is_correct", False)
    score = eval_result.get("score", 0.0)

    if is_correct:
        status_icon = "✅"
        status_label = "Passed"
    else:
        status_icon = "❌"
        status_label = "Failed"

    header = f"{status_icon} Attempt {attempt_num} — {status_label}  (score: {score:.0%})"
    with st.expander(header, expanded=True):
        # ── Actor output ──────────────────────────────────────────────────
        st.markdown("**🎭 Actor Output**")
        # Try to detect code blocks; if solution starts with a python keyword use code
        is_code = any(
            solution.lstrip().startswith(kw)
            for kw in ("def ", "class ", "import ", "from ", "#", "```")
        )
        if is_code:
            lang = "python"
            clean = solution.strip().removeprefix("```python").removeprefix("```").removesuffix("```").strip()
            st.code(clean, language=lang)
        else:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.04);border-radius:8px;'
                f'padding:0.8rem 1rem;font-size:0.92rem;line-height:1.6;">'
                f'{solution.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ── Evaluator result ──────────────────────────────────────────────
        render_evaluation_badge(eval_result)

        # ── Reflector analysis (only on failure) ─────────────────────────
        if not is_correct and reflection:
            st.markdown("---")
            st.markdown("**🔍 Reflector Analysis**")
            render_reflection_card(reflection)


# ── Evaluation badge ──────────────────────────────────────────────────────────

def render_evaluation_badge(eval_result: dict) -> None:
    """Show pass/fail badge with score bar and feedback."""
    is_correct = eval_result.get("is_correct", False)
    score = eval_result.get("score", 0.0)
    feedback = eval_result.get("feedback", "")
    errors = eval_result.get("errors", [])

    col_badge, col_score = st.columns([1, 2])
    with col_badge:
        st.markdown("**⚖️ Evaluator Result**")
        if is_correct:
            st.markdown(
                '<span class="badge badge-success">✓ CORRECT</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="badge badge-failure">✗ INCORRECT</span>',
                unsafe_allow_html=True,
            )

    with col_score:
        pct = int(score * 100)
        bar_color = "#22c55e" if score >= 0.7 else ("#eab308" if score >= 0.4 else "#ef4444")
        st.markdown(
            f"""
            <div class="score-bar-wrap">
                <small>Score: {pct}%</small>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if feedback:
        st.info(f"💬 **Feedback:** {feedback}")

    if errors:
        with st.expander("⚠️ Errors", expanded=False):
            for err in errors:
                st.error(str(err))


# ── Reflection card ───────────────────────────────────────────────────────────

def render_reflection_card(reflection_dict: dict) -> None:
    """Render the 4-part structured reflection in styled cards."""
    sections = [
        ("❓ What Went Wrong", reflection_dict.get("what_went_wrong", "")),
        ("🔎 Root Cause", reflection_dict.get("root_cause", "")),
        ("💡 Key Insight", reflection_dict.get("key_insight", "")),
        ("🗺️ Strategy", reflection_dict.get("strategy", "")),
    ]

    cols = st.columns(2)
    for i, (title, content) in enumerate(sections):
        with cols[i % 2]:
            if content:
                st.markdown(
                    f"""
                    <div class="reflection-card">
                        <h4>{title}</h4>
                        <p>{content}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="reflection-card">
                        <h4>{title}</h4>
                        <p><em>Not available</em></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ── Result metric cards ───────────────────────────────────────────────────────

def render_metric_cards(result) -> None:  # result: AgentResult
    """Render the summary metric cards in a 4-column layout."""
    cols = st.columns(4)

    outcome_class = "success" if result.is_correct else "failure"
    outcome_icon = "✅" if result.is_correct else "❌"
    outcome_text = "Solved!" if result.is_correct else "Not Solved"

    with cols[0]:
        st.markdown(
            f"""
            <div class="metric-card {outcome_class}">
                <div class="metric-value">{outcome_icon}</div>
                <div class="metric-label">{outcome_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[1]:
        st.markdown(
            f"""
            <div class="metric-card neutral">
                <div class="metric-value">{result.attempts}/{result.max_attempts}</div>
                <div class="metric-label">Attempts Used</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[2]:
        st.markdown(
            f"""
            <div class="metric-card neutral">
                <div class="metric-value">{result.total_time:.1f}s</div>
                <div class="metric-label">Time Taken</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[3]:
        st.markdown(
            f"""
            <div class="metric-card neutral">
                <div class="metric-value">{result.tokens_used:,}</div>
                <div class="metric-label">Tokens Used</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Flow diagram ──────────────────────────────────────────────────────────────

def render_flow_diagram() -> None:
    """Render the Reflexion architecture flow with emojis and markdown."""
    st.markdown(
        """
        <div style="font-family:monospace;font-size:0.9rem;line-height:2;
                    background:rgba(255,255,255,0.03);border-radius:10px;
                    padding:1.2rem 1.5rem;border:1px solid rgba(255,255,255,0.08);">
<pre>
              Task Input
                  │
                  ▼
        ┌─────────────────┐
        │   🎭  Actor     │  ──── generates a solution
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  ⚖️  Evaluator  │  ──── checks correctness
        └────────┬────────┘
                 │
         ┌───────┴────────┐
         │                │
       ✅ Correct       ❌ Wrong
         │                │
         ▼                ▼
       🎉 Done   ┌─────────────────┐
                 │  🔍 Reflector   │  ──── analyzes failure
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │ 🧠  Memory      │  ──── stores insight
                 └────────┬────────┘
                          │
                          └──────────────── back to Actor (retry)
</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Benchmark comparison ──────────────────────────────────────────────────────

def render_benchmark_comparison(
    baseline_results: list,
    reflexion_results: list,
) -> None:
    """Render side-by-side benchmark comparison cards and chart."""
    if not baseline_results or not reflexion_results:
        st.warning("No benchmark results to display.")
        return

    baseline_correct = sum(1 for r in baseline_results if r.is_correct)
    reflexion_correct = sum(1 for r in reflexion_results if r.is_correct)
    n = len(baseline_results)
    baseline_acc = baseline_correct / n if n else 0.0
    reflexion_acc = reflexion_correct / n if n else 0.0
    delta = reflexion_acc - baseline_acc
    delta_pct = delta * 100

    # ── Summary cards ─────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card {'success' if baseline_acc >= 0.5 else 'failure'}">
                <div class="metric-value">{baseline_acc:.0%}</div>
                <div class="metric-label">Baseline Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card {'success' if reflexion_acc >= 0.5 else 'failure'}">
                <div class="metric-value">{reflexion_acc:.0%}</div>
                <div class="metric-label">Reflexion Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        delta_class = "success" if delta >= 0 else "failure"
        delta_sign = "+" if delta >= 0 else ""
        st.markdown(
            f"""
            <div class="metric-card {delta_class}">
                <div class="metric-value">{delta_sign}{delta_pct:.1f}%</div>
                <div class="metric-label">Improvement</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bar chart ──────────────────────────────────────────────────────────
    # pandas is used for both the fallback chart and the per-task table below;
    # import once here so both blocks can share the same reference.
    try:
        import pandas as pd  # type: ignore[import]
        _pandas_available = True
    except ImportError:
        _pandas_available = False

    try:
        import plotly.graph_objects as go  # type: ignore[import]

        fig = go.Figure(
            data=[
                go.Bar(
                    name="Baseline",
                    x=["Accuracy"],
                    y=[baseline_acc * 100],
                    marker_color="#6366f1",
                    text=[f"{baseline_acc:.0%}"],
                    textposition="outside",
                ),
                go.Bar(
                    name="Reflexion",
                    x=["Accuracy"],
                    y=[reflexion_acc * 100],
                    marker_color="#22c55e",
                    text=[f"{reflexion_acc:.0%}"],
                    textposition="outside",
                ),
            ]
        )
        fig.update_layout(
            title="Baseline vs Reflexion Accuracy",
            yaxis_title="Accuracy (%)",
            yaxis_range=[0, 105],
            barmode="group",
            template="plotly_dark",
            height=350,
            margin={"t": 50, "b": 30},
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        # Fallback when plotly is unavailable: use st.bar_chart with pandas
        if _pandas_available:
            chart_data = pd.DataFrame(
                {"Accuracy (%)": [baseline_acc * 100, reflexion_acc * 100]},
                index=["Baseline", "Reflexion"],
            )
            st.bar_chart(chart_data)

    # ── Per-task table ─────────────────────────────────────────────────────
    st.markdown("#### Per-task Results")
    rows = []
    for b, r in zip(baseline_results, reflexion_results):
        rows.append(
            {
                "Task ID": b.task_id,
                "Baseline": "✅" if b.is_correct else "❌",
                "Reflexion": "✅" if r.is_correct else "❌",
                "Attempts Used": r.attempts,
            }
        )

    if _pandas_available:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        for row in rows:
            st.write(row)
