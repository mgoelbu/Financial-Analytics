import streamlit as st

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Equity Insight Workbench Launcher",
    layout="wide",
)

# ─── Data Universe Placeholders ───────────────────────────────────────────────
# 👉 Replace these with your actual numbers
TOTAL_TICKERS = 4_455    # e.g. 4,455 tickers
TOTAL_YEARS   = 15       # e.g. 15 years of data
TOTAL_FACTORS = 2        # EPS + PE

# compute derived metrics
HISTORICAL_DATA_POINTS = TOTAL_TICKERS * TOTAL_YEARS * TOTAL_FACTORS
BACKTEST_SAMPLES        = 6_150  # e.g. the number of t+1 & t+2 predictions you actually ran

# ─── Header & Overview ────────────────────────────────────────────────────────
st.title("🔗 Equity Insight Workbench Launcher")
st.write(
    """
    Welcome!  This application provides three core insights:
    
    1. **Valuation Advisor** — Is the stock cheap or expensive right now?  
    2. **Backtest** — How well has our simple EPS×PE model predicted price moves in the past?  
    3. **Company Snapshot** — What’s happening with the company and its stock price today?  
    
    Use the sidebar ticker selector and the tabs to explore each tool.
    """
)

st.markdown("---")

# ─── Data Universe & Sample Size ──────────────────────────────────────────────
st.subheader("📊 Data Universe & Sample Size")

c1, c2, c3 = st.columns(3)
c1.metric("Total Universe", f"{TOTAL_TICKERS:,} tickers")
c2.metric(
    "Historical Data Points",
    f"{TOTAL_TICKERS:,} tickers × {TOTAL_YEARS} years × {TOTAL_FACTORS} factors = {HISTORICAL_DATA_POINTS:,}"
)
c3.metric("Backtest Samples", f"{BACKTEST_SAMPLES:,} directional predictions")

st.markdown("---")

# ─── Quick Launch Link ─────────────────────────────────────────────────────────
st.markdown(
    """
    ## 🚀 Jump into the Workbench

    [➡️ Go to **Equity Insight Workbench**](Equity_Insight_Workbench.py)
    """
)
