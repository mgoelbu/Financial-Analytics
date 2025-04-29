import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── Streamlit page config MUST be the first Streamlit command ──────────────
st.set_page_config(
    page_title="Valuation Advisor",
    layout="wide"
)

# ─── Data‐loading functions ──────────────────────────────────────────────────
@st.cache_data
def load_company_data():
    file_path = 'data/Master data price eps etc.xlsx'
    df = pd.read_excel(file_path, sheet_name='Company Dta', header=None)
    # Row 4 (0-index = 3) holds your real column names
    df.columns = df.iloc[3]
    return df.iloc[4:].reset_index(drop=True)

@st.cache_data
def load_eps_price_and_meta(df):
    # EPS = cols J–W, Price = cols X–AI
    eps   = df.iloc[:, 9:24].apply(pd.to_numeric, errors='coerce')
    price = df.iloc[:, 24:39].apply(pd.to_numeric, errors='coerce')
    years = list(range(2010, 2025))
    eps.columns   = years
    price.columns = years

    tickers  = df['Ticker'].reset_index(drop=True)
    gsubinds = df['gsubind'].reset_index(drop=True)
    industry = df['Industry'].reset_index(drop=True)

    return eps, price, tickers, gsubinds, industry

# ─── Load all sheets once ─────────────────────────────────────────────────────
company_df = load_company_data()
eps_data, price_data, ticker_series, gsubind_series, industry_series = (
    load_eps_price_and_meta(company_df)
)

# ─── UI title + ticker selector in the sidebar ───────────────────────────────
st.title("💸 Valuation Advisor")
ticker = st.sidebar.selectbox("Choose a ticker", ticker_series.tolist())
if not ticker:
    st.sidebar.warning("Please pick a ticker to begin.")
    st.stop()

# ─── Common lookups ───────────────────────────────────────────────────────────
idx      = ticker_series[ticker_series == ticker].index[0]
gsubind  = gsubind_series[idx]
industry = industry_series[idx]
peer_idxs = gsubind_series[gsubind_series == gsubind].index
peers     = ticker_series.loc[peer_idxs].tolist()

# ─── Page header ──────────────────────────────────────────────────────────────
st.subheader(f"Details for {ticker}")
st.write(f"**gsubind:** {gsubind}    **Industry:** {industry}")
st.write("**Competitors:**", ", ".join([p for p in peers if p != ticker]) or "None")

# ─── Compute implied valuation for the latest year ────────────────────────────
years   = list(eps_data.columns)
val_yr  = years[-1]
pe_ratio= price_data.divide(eps_data).mask(lambda x: (x<=0)|x.isna())
peer_pes = pe_ratio.loc[peer_idxs, val_yr].dropna()

eps_t   = eps_data.loc[idx, val_yr]
price_t = price_data.loc[idx, val_yr]

if (eps_t>0) and (len(peer_pes)>0):
    med_pe   = peer_pes.median()
    low_pe   = peer_pes.min()
    high_pe  = peer_pes.max()
    imp_avg  = eps_t * med_pe
    imp_low  = eps_t * low_pe
    imp_high = eps_t * high_pe
else:
    med_pe = imp_avg = imp_low = imp_high = np.nan

# ─── Show key metrics ─────────────────────────────────────────────────────────
st.subheader("📊 Key Valuation Inputs")
c1, c2, c3 = st.columns(3)
c1.metric(f"EPS ({val_yr})", f"{eps_t:.2f}" if not np.isnan(eps_t) else "N/A")
c2.metric("Industry Median P/E", f"{med_pe:.2f}" if not np.isnan(med_pe) else "N/A")
c3.metric(f"Current Price ({val_yr})", f"${price_t:.2f}" if not np.isnan(price_t) else "N/A")

# ─── Recommendation banner ───────────────────────────────────────────────────
st.subheader("✅ Recommendation")
if not np.isnan(imp_avg):
    if imp_avg > price_t:
        st.success("📈 Likely Undervalued — Consider Buying")
    else:
        st.warning("📉 Likely Overvalued — Exercise Caution")
else:
    st.info("ℹ️ Not enough data to form a recommendation.")

# ─── Horizontal range visualization ──────────────────────────────────────────
st.subheader("📉 Valuation Range Visualization")
if not np.isnan(imp_avg):
    fig, ax = plt.subplots(figsize=(10, 2.5))
    ax.hlines(1, imp_low, imp_high, color='gray', linewidth=10, alpha=0.3)
    ax.vlines(imp_avg, 0.9, 1.1, color='blue', linewidth=3, label='Avg Implied')
    ax.plot(price_t, 1, 'ro', label='Current Price')
    ax.text(imp_low, 1.15,  f"Low:  ${imp_low:.2f}",  ha='center', fontsize=9)
    ax.text(imp_avg,1.27,   f"Avg:  ${imp_avg:.2f}", ha='center', fontsize=9, color='blue')
    ax.text(imp_high,1.15, f"High: ${imp_high:.2f}", ha='center', fontsize=9)
    ax.set_xlim(imp_low*0.85, imp_high*1.15)
    ax.set_ylim(0.8, 1.4)
    ax.axis('off')
    ax.legend(loc='upper center', ncol=2)
    st.pyplot(fig)

    gap = ((imp_avg - price_t) / imp_avg) * 100
    caption = f"Current price is **{abs(gap):.1f}% {'below' if gap>0 else 'above'}** implied average."
    st.caption(caption)
else:
    st.warning("⚠️ Not enough peer data for visualization.")
