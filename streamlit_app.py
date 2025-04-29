import streamlit as st

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Equity Insight Workbench Launcher",
    layout="wide",
)

# ─── Constants ────────────────────────────────────────────────────────────────
TOTAL_TICKERS = 4_455    # your full ticker universe
TOTAL_YEARS   = 15       # years of data
TOTAL_FACTORS = 2        # EPS + PE
HISTORICAL_DATA_POINTS = TOTAL_TICKERS * TOTAL_YEARS * TOTAL_FACTORS
BACKTEST_SAMPLES        = 6_150  # your actual t+1 & t+2 samples

# ─── Intro ───────────────────────────────────────────────────────────────────
st.title("Equity Insight Workbench Launcher")
st.write(
    """
    **Welcome!** This application provides three core insights:

    1. **Valuation Advisor** — Is the stock cheap or rich right now?  
    2. **Backtest** — How well has our simple EPS×PE model predicted price moves in the past?  
    3. **Company Snapshot** — What’s happening with the company and its stock price today?  

    Use the **sidebar ticker selector** and **tabs** in the Workbench to explore each tool.
    """
)
st.markdown("---")

# ─── Data Universe & Sample Size ──────────────────────────────────────────────
st.header("📊 Data Universe & Sample Size")
col1, col2, col3 = st.columns([1, 1.5, 1])
col1.metric("Total Universe", f"{TOTAL_TICKERS:,} tickers")
col2.metric(
    "Historical Data Points",
    f"{TOTAL_TICKERS:,} × {TOTAL_YEARS} years × {TOTAL_FACTORS} factors = {HISTORICAL_DATA_POINTS:,}"
)
col3.metric("Backtest Samples", f"{BACKTEST_SAMPLES:,} predictions")
st.markdown("---")

# ─── Jump Instructions ────────────────────────────────────────────────────────
st.subheader("🚀 How to Launch the Workbench")
st.write(
    """
    • Select a ticker in the **sidebar**  
    • Switch between tabs (**Valuation Advisor**, **Backtest**, **Company Snapshot**)  
    """
)
