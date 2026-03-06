"""Custom CSS styles for the ThinkTwice Streamlit UI."""

CUSTOM_CSS = """
<style>
/* ── General ──────────────────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* ── Metric cards ─────────────────────────────────────────────────────────── */
.metric-card {
    background: var(--background-color, #1e1e2e);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    border: 2px solid transparent;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    margin-bottom: 0.5rem;
}
.metric-card.success {
    border-color: #22c55e;
    background: linear-gradient(135deg, rgba(34,197,94,0.08) 0%, rgba(34,197,94,0.03) 100%);
}
.metric-card.failure {
    border-color: #ef4444;
    background: linear-gradient(135deg, rgba(239,68,68,0.08) 0%, rgba(239,68,68,0.03) 100%);
}
.metric-card.neutral {
    border-color: #6366f1;
    background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(99,102,241,0.03) 100%);
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.2;
}
.metric-card .metric-label {
    font-size: 0.85rem;
    opacity: 0.7;
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Reflection cards ─────────────────────────────────────────────────────── */
.reflection-card {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    border-left: 4px solid #6366f1;
    background: linear-gradient(135deg, rgba(99,102,241,0.06) 0%, rgba(99,102,241,0.02) 100%);
}
.reflection-card h4 {
    margin: 0 0 0.4rem 0;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    opacity: 0.7;
}
.reflection-card p {
    margin: 0;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* ── Attempt status badges ────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.8rem;
    font-weight: 600;
    margin-left: 0.5rem;
}
.badge-success {
    background: rgba(34,197,94,0.15);
    color: #22c55e;
    border: 1px solid #22c55e;
}
.badge-failure {
    background: rgba(239,68,68,0.15);
    color: #ef4444;
    border: 1px solid #ef4444;
}
.badge-running {
    background: rgba(234,179,8,0.15);
    color: #eab308;
    border: 1px solid #eab308;
}

/* ── Flow arrows ──────────────────────────────────────────────────────────── */
.flow-arrow {
    text-align: center;
    font-size: 1.5rem;
    opacity: 0.5;
    margin: 0.25rem 0;
}

/* ── Success banner ───────────────────────────────────────────────────────── */
.success-banner {
    background: linear-gradient(135deg, rgba(34,197,94,0.12) 0%, rgba(34,197,94,0.04) 100%);
    border: 1px solid #22c55e;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 600;
    color: #22c55e;
    margin: 1rem 0;
}

/* ── Score bar ────────────────────────────────────────────────────────────── */
.score-bar-wrap {
    margin: 0.3rem 0;
}
.score-bar-bg {
    background: rgba(255,255,255,0.1);
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.6s ease;
}

/* ── Sidebar logo area ────────────────────────────────────────────────────── */
.sidebar-logo {
    font-size: 2rem;
    font-weight: 800;
    text-align: center;
    padding: 0.5rem 0 1rem 0;
    letter-spacing: -0.03em;
}

/* ── Architecture component cards ────────────────────────────────────────── */
.arch-card {
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    border: 1px solid rgba(99,102,241,0.3);
    background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(99,102,241,0.02) 100%);
    height: 100%;
}
.arch-card h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
}
.arch-card p {
    margin: 0;
    font-size: 0.9rem;
    opacity: 0.8;
    line-height: 1.5;
}
</style>
"""


def inject_css() -> None:
    """Inject custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
