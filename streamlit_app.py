import streamlit as st

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Welcome to Equity Insight Workbench",
    layout="wide"
)

# ─── Title and Note ───────────────────────────────────────────────────────────
st.title("🔗 Equity Insight Workbench Launcher")

st.markdown(
    """
    Welcome! This application provides three core insights:

    1. **Valuation Advisor** — Is the stock cheap or expensive right now?
    2. **Backtest** — How well has our simple EPS×PE model predicted price moves in the past?
    3. **Company Snapshot** — What’s happening with the company and its stock price today?

    Use the tabs or navigation menu to explore each tool.
    """,
    unsafe_allow_html=True
)

# ─── Link to Main App ──────────────────────────────────────────────────────────
st.markdown(
    "---"
)
st.markdown(
    "## 🚀 Get Started"
)
st.markdown(
    "[👉 Go to Equity Insight Workbench](Equity Insight Workbench.py)"
)

