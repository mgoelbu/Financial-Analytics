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
# ─── Data Universe Summary ─────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📊 Data Universe & Sample Size")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Tickers Tracked",  "4 455")
c2.metric("Years of History", "15")
c3.metric("Raw Data Points",  "133 650")
c4.metric("Back-test Samples", "6 150")

st.caption(
    "Raw data points = EPS and price pairs (15 years × 4 455 tickers). "
    "Back-test samples equal 205 tickers × 30 predictions."
)

# bump the value font a bit larger
st.markdown(
    """
    <style>
        div[data-testid="metric-container"] > div > span {
            font-size: 2.5rem;            /* value text */
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Link to Main App ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🚀 Get Started")
st.markdown(
    "[👉 Go to Equity Insight Workbench]"
    "[👉 Go to Equity Insight Workbench](Equity Insight Workbench.py)"
)
