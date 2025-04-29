# 1_Financial_Fundamentals.py
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📂 Financial Fundamentals")

ticker_input = st.text_input("Enter a ticker symbol", "DELL").upper()

if ticker_input:
    ticker = yf.Ticker(ticker_input)

    # 1) Pull the 4 financial tables:
    fin  = ticker.financials        # Income statement (TTM)
    bal  = ticker.balance_sheet     # Balance sheet (TTM)
    cf   = ticker.cashflow          # Cash flow (TTM)
    info = ticker.info              # for ratios, growth, etc.

    # helper to safely pick the most recent column, or 0 if missing
    def most_recent(df, line_item):
        try:
            return df.loc[line_item].dropna().iloc[0]
        except Exception:
            return 0

    # ── Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Income Statement",
        "📉 Balance Sheet",
        "💵 Cash Flow",
        "📈 Growth & Ratios"
    ])

    # ========== Income Statement ==========  
    with tab1:
        st.subheader("📊 Key Income Metrics")
        rev      = most_recent(fin, "Total Revenue")
        gross    = most_recent(fin, "Gross Profit")
        ebitda   = most_recent(fin, "Ebitda")
        net_inc  = most_recent(fin, "Net Income") or most_recent(fin, "Net Income Applicable To Common Shares")
        margin   = info.get("profitMargins", 0) * 100

        st.metric("Revenue (TTM)",       f"${rev/1e9:.2f}B")
        st.metric("Gross Profit (TTM)",  f"${gross/1e9:.2f}B")
        st.metric("EBITDA (TTM)",        f"${ebitda/1e9:.2f}B")
        st.metric("Net Income (TTM)",    f"${net_inc/1e9:.2f}B")
        st.metric("Profit Margin (TTM)", f"{margin:.2f}%")

    # ========== Balance Sheet ==========  
    with tab2:
        st.subheader("📉 Key Balance Sheet Metrics")
        assets    = most_recent(bal, "Total Assets")
        liab      = most_recent(bal, "Total Liab")
        equity    = most_recent(bal, "Total Stockholder Equity")
        current   = info.get("currentRatio", 0)
        d2e       = info.get("debtToEquity", 0)

        st.metric("Total Assets",        f"${assets/1e9:.2f}B")
        st.metric("Total Liabilities",   f"${liab/1e9:.2f}B")
        st.metric("Shareholder Equity",  f"${equity/1e9:.2f}B")
        st.metric("Current Ratio",       f"{current:.2f}")
        st.metric("Debt to Equity",      f"{d2e:.2f}")

    # ========== Cash Flow ==========  
    with tab3:
        st.subheader("💵 Key Cash Flow Metrics")
        op_cf     = most_recent(cf, "Operating Cash Flow")
        capex     = most_recent(cf, "Capital Expenditures")
        free_cf   = op_cf + capex    # yfinance cashflow is negative on capex already

        st.metric("Operating Cash Flow", f"${op_cf/1e9:.2f}B")
        st.metric("Capital Expenditures", f"${-capex/1e9:.2f}B")
        st.metric("Free Cash Flow",      f"${free_cf/1e9:.2f}B")

    # ========== Growth & Ratios ==========  
    with tab4:
        st.subheader("📈 Growth & Efficiency Metrics")
        roa   = info.get("returnOnAssets", 0) * 100
        roe   = info.get("returnOnEquity", 0) * 100
        rev_g = info.get("revenueGrowth", 0) * 100
        eps_g = info.get("earningsGrowth", 0) * 100
        pe    = info.get("trailingPE", 0)
        pb    = info.get("priceToBook", 0)
        ev_eb = info.get("enterpriseToEbitda", 0)
        ps    = info.get("priceToSalesTrailing12Months", 0)

        st.metric("ROA",        f"{roa:.2f}%")
        st.metric("ROE",        f"{roe:.2f}%")
        st.metric("Rev Growth", f"{rev_g:.2f}%")
        st.metric("EPS Growth", f"{eps_g:.2f}%")
        st.metric("P/E Ratio",  f"{pe:.2f}")
        st.metric("P/B Ratio",  f"{pb:.2f}")
        st.metric("EV/EBITDA",  f"{ev_eb:.2f}")
        st.metric("P/S Ratio",  f"{ps:.2f}")

    st.caption("📌 Data sourced from Yahoo Finance via yfinance")
