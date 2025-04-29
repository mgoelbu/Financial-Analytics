import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── Page config: MUST come first ──────────────────────────────────────────────
st.set_page_config(
    page_title="Valuation & Backtest",
    layout="wide"
)

# ─── Data‐loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    file_path = 'data/Master data price eps etc.xlsx'

    # --- Company Dta sheet
    df = pd.read_excel(file_path, sheet_name='Company Dta', header=None)
    df.columns = df.iloc[3]                   # row 4 as header
    df = df.iloc[4:].reset_index(drop=True)   # drop above rows

    # --- EPS and Price blocks (2010–2024)
    years      = list(range(2010, 2025))
    eps        = df.iloc[:, 9:24].apply(pd.to_numeric, errors='coerce')
    price      = df.iloc[:, 25:40].apply(pd.to_numeric, errors='coerce')
    eps.columns, price.columns = years, years

    # --- Metadata columns
    tickers    = df['Ticker'].reset_index(drop=True)
    gsubinds   = df['gsubind'].reset_index(drop=True)
    industries = df['Industry'].reset_index(drop=True)

    # --- Median PE mapping (same logic as Median PE sheet)
    med = pd.read_excel(file_path, sheet_name='Median PE', header=None)
    med_trim = med.iloc[5:, :18].reset_index(drop=True)
    med_trim.columns = [None, None, 'gsubind'] + years
    gsubind_to_medpe = {
        row['gsubind']: row[3:].values
        for _, row in med_trim.iterrows()
    }

    # --- Actual price history from Analysis sheet
    ana = pd.read_excel(file_path, sheet_name='Analysis', header=None)
    ana_trim = ana.iloc[5:, :40].reset_index(drop=True)
    actual_price = ana_trim.iloc[:, 24:39].apply(pd.to_numeric, errors='coerce')
    actual_price.columns = years
    actual_price.index = ana_trim.iloc[:, 0]

    return (
        df, eps, price, tickers, gsubinds,
        industries, gsubind_to_medpe, actual_price, years
    )

# load once
(
    company_df, eps_data, price_data, ticker_series,
    gsubind_series, industry_series, medpe_map,
    actual_price_data, years
) = load_data()

# ─── Sidebar ticker picker ─────────────────────────────────────────────────────
st.title("📊 P/E Valuation & Backtest Prototype")
ticker = st.sidebar.selectbox("Select a ticker", ticker_series.tolist())
if not ticker:
    st.sidebar.warning("Please choose a ticker to continue.")
    st.stop()

# common lookups
idx      = ticker_series[ticker_series == ticker].index[0]
gsubind  = gsubind_series[idx]
industry = industry_series[idx]
peer_idxs= gsubind_series[gsubind_series == gsubind].index
peers    = ticker_series.loc[peer_idxs].tolist()

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab_val, tab_bt = st.tabs(["Valuation Advisor", "Backtest Analysis"])

# ── Tab 1: Valuation Advisor ──────────────────────────────────────────────────
with tab_val:
    st.subheader(f"Details for {ticker}")
    st.write(f"**gsubind:** {gsubind}    **Industry:** {industry}")
    st.write("**Peers:**", ", ".join([p for p in peers if p != ticker]) or "None")

    # latest year
    val_yr = years[-1]

    # build peer P/E table
    pe_table = price_data.divide(eps_data).mask(lambda x: (x <= 0) | x.isna())

    peer_pes = pe_table.loc[peer_idxs, val_yr].dropna()
    eps_t    = eps_data.loc[idx, val_yr]
    price_t  = price_data.loc[idx, val_yr]

    if (eps_t > 0) and len(peer_pes):
        med_pe   = peer_pes.median()
        low_pe   = peer_pes.min()
        high_pe  = peer_pes.max()
        imp_avg  = eps_t * med_pe
        imp_low  = eps_t * low_pe
        imp_high = eps_t * high_pe
    else:
        med_pe = imp_avg = imp_low = imp_high = np.nan

    # show metrics
    st.subheader("📊 Key Valuation Inputs")
    c1, c2, c3 = st.columns(3)
    c1.metric(f"EPS ({val_yr})", f"{eps_t:.2f}" if eps_t>0 else "N/A")
    c2.metric("Industry Median P/E", f"{med_pe:.2f}" if not np.isnan(med_pe) else "N/A")
    c3.metric(f"Current Price ({val_yr})", f"${price_t:.2f}")

    # recommendation
    st.subheader("✅ Recommendation")
    if not np.isnan(imp_avg):
        if imp_avg > price_t:
            st.success("Likely Undervalued — Consider Buying 📈")
        else:
            st.warning("Likely Overvalued — Exercise Caution ⚠️")
    else:
        st.info("Not enough data to form a recommendation.")

    # valuation range viz
    st.subheader("📉 Valuation Range Visualization")
    if not np.isnan(imp_avg):
        fig, ax = plt.subplots(figsize=(10,2.5))
        ax.hlines(1, imp_low, imp_high, color='gray', linewidth=10, alpha=0.3)
        ax.vlines(imp_avg, 0.9, 1.1, color='blue', linewidth=3, label='Median Implied')
        ax.plot(price_t, 1, 'ro', label='Current Price')
        ax.text(imp_low, 1.15,  f"Low:  ${imp_low:.2f}",  ha='center')
        ax.text(imp_avg,1.27,   f"Avg:  ${imp_avg:.2f}", ha='center', color='blue')
        ax.text(imp_high,1.15, f"High: ${imp_high:.2f}", ha='center')
        ax.set_xlim(imp_low*0.85, imp_high*1.15); ax.set_ylim(0.8,1.4)
        ax.axis('off'); ax.legend(loc='upper center', ncol=2)
        st.pyplot(fig)

        gap = ((imp_avg - price_t) / imp_avg) * 100
        st.caption(f"Current is **{abs(gap):.1f}% {'below' if gap>0 else 'above'}** implied median.")
    else:
        st.warning("⚠️ Not enough peer data for visualization.")

# ── Tab 2: Backtest Analysis ───────────────────────────────────────────────────
with tab_bt:
    # assemble history
    eps_row    = eps_data.loc[idx].mask(eps_data.loc[idx] <= 0)
    med_pe_row = pd.Series(medpe_map.get(gsubind, [None]*len(years)), index=years)
    model_price= eps_row * med_pe_row
    actual_row = actual_price_data.loc[ticker]

    price_df = pd.DataFrame({
        "Year":        years,
        "Model Price": model_price.values,
        "Actual Price": actual_row.values,
    }).dropna(subset=["Actual Price"])

    # shift model series forward by 1
    yrs_act = price_df["Year"]
    yrs_mod = yrs_act + 1
    prs_act = price_df["Actual Price"]
    prs_mod = price_df["Model Price"]

    st.subheader(f"📈 Backtest: {ticker} Model vs Actual (1-Year Ahead)")
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(yrs_mod, prs_mod, marker='s', label='Model (t→t+1)')
    ax.plot(yrs_act, prs_act, marker='o', label='Actual (t)')
    ax.set_xlabel("Year"); ax.set_ylabel("Price")
    ax.set_xticks(list(range(years[0], years[-1]+2, 2)))
    plt.xticks(rotation=45)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)

    # compute hit rate (1-year only)
    total = correct = 0
    for y in years[:-1]:
        if pd.isna(model_price[y]): continue
        pred = "Up" if model_price[y] > actual_row[y] else "Down"
        if (y+1 in actual_row.index) and pd.notna(actual_row[y+1]):
            actual_mv = "Up" if actual_row[y+1] > actual_row[y] else "Down"
            total += 1
            correct += (pred == actual_mv)

    hr = (correct/total*100) if total else np.nan
    st.subheader("🎯 Hit Rate Analysis")
    st.write(f"Total Signals: {total}   Correct: {correct}")
    if not np.isnan(hr):
        st.success(f"Overall Hit Rate: {hr:.1f}%")
    else:
        st.warning("Not enough data to calculate hit rate.")

    st.dataframe(price_df, use_container_width=True)
