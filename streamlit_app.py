# Home.py   (landing / launcher page)

import streamlit as st

# ─────────────────── Page configuration ───────────────────
st.set_page_config(
    page_title="Welcome to Equity Insight Workbench",
    page_icon="🔗",
    layout="wide",
)

# (Optional) hide Streamlit’s auto-generated sidebar list:
st.markdown(
    """
    <style>
        .stApp [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────── Hero section ──────────────────────────
st.title("🔗 Equity Insight Workbench Launcher")

st.markdown(
    """
    Welcome! This application provides three core insights:
    
    1. **Valuation Advisor** — Is the stock cheap or expensive *right now*?  
    2. **Back-test** — How well has our simple EPS × PE model predicted price moves in the past?  
    3. **Company Snapshot** — What’s happening with the company and its stock price today?  

    Use the navigation menu or the **Launch** button below to explore each tool.
    """,
    unsafe_allow_html=True,
)

# ─────────────────── Data-universe score-cards ─────────────
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

# ─────────────────── Launch button & sidebar link ──────────
st.markdown("---")
if st.button("🚀 Launch Equity Insight Workbench", use_container_width=True):
    st.switch_page("pages/Workbench.py")

# custom sidebar link (so users can also navigate manually)
with st.sidebar:
    st.page_link("pages/Workbench.py", label="📊 Equity Insight Workbench", icon="🧮")
