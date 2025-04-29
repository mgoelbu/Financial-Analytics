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

# ─── Data Universe Summary ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 Data Universe & Sample Size")
st.markdown(
    """
    - **Total Universe:** `4,455` tickers (all publicly listed companies we track)
    - **Historical Data Points:** `15` years of annual EPS and price data per ticker, equating to `133,650` data points
    - **Backtest Samples:** Ultimately we went ahead with `205 tickers` and `6,150` data points for our project prototype to evalaute one and two-year directional predictions

    """,
    unsafe_allow_html=True
)

# ─── Link to Main App ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🚀 Get Started")
st.markdown(
    "[👉 Go to Equity Insight Workbench](Equity Insight Workbench.py)"
)
