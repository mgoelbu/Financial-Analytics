import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Valuation & Backtest", layout="wide")

# ─── Data Loading ─────────────────────────────────────────────────────────────
file_path = 'data/Master data price eps etc.xlsx'

@st.cache_data
def load_data():
    # Company Dta sheet
    df = pd.read_excel(file_path, sheet_name='Company Dta', header=None)
    headers = df.iloc[3]
    df.columns = headers
    company_data = df.iloc[4:].reset_index(drop=True)

    # EPS & Price blocks
    eps_data = company_data.iloc[:, 9:24].apply(pd.to_numeric, errors='coerce')
    price_data = company_data.iloc[:, 24:39].apply(pd.to_numeric, errors='coerce')
    eps_data.columns = list(range(2010, 2025))
    price_data.columns = list(range(2010, 2025))

    # Tickers & gsubind
    ticker_data  = company_data['Ticker'].reset_index(drop=True)
    gsubind_data = company_data['gsubind'].reset_index(drop=True)

    # Median PE sheet
    median_pe = pd.read_excel(file_path, sheet_name='Median PE', header=None)
    median_pe_trim = median_pe.iloc[5:, :18].reset_index(drop=True)
    median_pe_trim.columns = [None, None, 'gsubind'] + list(range(2010, 2025))
    gsubind_to_median_pe = {
        row['gsubind']: row[3:].values
        for _, row in median_pe_trim.iterrows()
    }

    # Analysis sheet → actual prices
    analysis = pd.read_excel(file_path, sheet_name='Analysis', header=None)
    analysis_trim = analysis.iloc[5:, :40].reset_index(drop=True)
    actual_price = analysis_trim.iloc[:, 24:39].apply(pd.to_numeric, errors='coerce')
    actual_price.columns = list(range(2010, 2025))
    actual_price.index   = analysis_trim.iloc[:, 0]

    return (
        company_data,
        eps_data,
        price_data,
        ticker_data,
        gsubind_data,
        gsubind_to_median_pe,
        actual_price
    )

company_data, eps_data, price_data, ticker_data, gsubind_data, gsubind_to_median_pe, actual_price_data = load_data()
years = list(range(2010, 2025))

# ─── Sidebar Ticker Input ────────────────────────────────────────────────────
ticker_input = st.sidebar.selectbox("Choose a ticker", options=ticker_data.tolist())

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💸 Valuation Advisor", "📊 Backtest"])

# ─── Tab 1: Valuation Advisor ─────────────────────────────────────────────────
with tab1:
    st.title("💸 Valuation Advisor")

    if ticker_input in ticker_data.values:
        idx = ticker_data[ticker_data == ticker_input].index[0]
        company_gsubind = gsubind_data[idx]

        # Peers
        peer_indices = gsubind_data[gsubind_data == company_gsubind].index
        peers = ticker_data.loc[peer_indices].tolist()

        # Sector & Industry
        sector   = company_data.loc[idx, 'Sector']   if 'Sector'   in company_data.columns else "N/A"
        industry = company_data.loc[idx, 'Industry'] if 'Industry' in company_data.columns else "N/A"

        st.markdown(f"**Sector:** {sector}  ")
        st.markdown(f"**Industry:** {industry}  ")
        st.markdown(f"**Peers:** {', '.join(peers)}")

        # Median P/E for peers
        pe_ratio = price_data.divide(eps_data)
        pe_ratio = pe_ratio.mask((pe_ratio <= 0) | (pe_ratio.isna()))
        pe_ratio_with_gsubind = pe_ratio.copy()
        pe_ratio_with_gsubind['gsubind'] = gsubind_data.values
        peer_pe_ratios = pe_ratio_with_gsubind.loc[peer_indices]
        valid_peer_pe = peer_pe_ratios[2024].dropna()

        # EPS & Price 2024
        eps_2024      = eps_data.loc[idx, 2024]
        current_price = price_data.loc[idx, 2024]
        eps_valid     = (eps_2024 > 0) and not np.isnan(eps_2024)

        if eps_valid and not valid_peer_pe.empty:
            industry_pe_avg   = valid_peer_pe.median()
            implied_price_avg = eps_2024 * industry_pe_avg
            implied_price_min = eps_2024 * valid_peer_pe.min()
            implied_price_max = eps_2024 * valid_peer_pe.max()
        else:
            industry_pe_avg = implied_price_avg = implied_price_min = implied_price_max = np.nan

        # Key Inputs
        st.subheader("📊 Key Valuation Inputs")
        c1, c2, c3 = st.columns(3)
        c1.metric("EPS (2024)", f"{eps_2024:.2f}" if eps_valid else "N/A")
        c2.metric("Industry Median P/E", f"{industry_pe_avg:.2f}" if not np.isnan(industry_pe_avg) else "N/A")
        c3.metric("Current Price (2024)", f"${current_price:.2f}" if not np.isnan(current_price) else "N/A")

        # Recommendation
        st.subheader("✅ Recommendation")
        if not np.isnan(implied_price_avg) and implied_price_avg > current_price:
            st.success("📈 Likely Undervalued — Consider Buying")
        elif not np.isnan(implied_price_avg):
            st.warning("📉 Likely Overvalued — Exercise Caution")
        else:
            st.info("ℹ️ Not enough data to provide recommendation.")

        # Valuation Range Visualization
        st.subheader("📉 Valuation Range Visualization")
        if eps_valid and not valid_peer_pe.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5))
            ax.hlines(1, implied_price_min, implied_price_max,
                      color='gray', linewidth=10, alpha=0.4)
            ax.vlines(implied_price_avg, 0.9, 1.1,
                      color='blue', linewidth=2, label='Avg Implied Price')
            ax.plot(current_price, 1, 'ro', markersize=10, label='Current Price')
            ax.text(implied_price_min, 1.15, f"Low: ${implied_price_min:.2f}",
                    ha='center', fontsize=9)
            ax.text(implied_price_avg, 1.27, f"Avg: ${implied_price_avg:.2f}",
                    ha='center', fontsize=9, color='blue')
            ax.text(implied_price_max, 1.15, f"High: ${implied_price_max:.2f}",
                    ha='center', fontsize=9)
            ax.set_xlim(implied_price_min * 0.85, implied_price_max * 1.15)
            ax.set_ylim(0.8, 1.4)
            ax.axis('off')
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.35), ncol=2)
            st.pyplot(fig)

            gap = ((implied_price_avg - current_price) / implied_price_avg) * 100
            if gap > 0:
                st.caption(f"📉 Current price is **{gap:.1f}% below** the implied valuation average.")
            else:
                st.caption(f"📈 Current price is **{abs(gap):.1f}% above** the implied valuation average.")
        else:
            st.warning("⚠️ Not enough valid peer data to create a proper visualization.")
    else:
        if ticker_input:
            st.error("❌ Ticker not found. Please check and try again.")

# ─── Tab 2: Backtest ───────────────────────────────────────────────────────────
with tab2:
    st.title("📊 Company Stock Valuation Analysis")

    if ticker_input in ticker_data.values:
        idx       = ticker_data[ticker_data == ticker_input].index[0]
        gsubind   = gsubind_data[idx]
        industry  = company_data.loc[idx, "Industry"]
        st.subheader(f"Details for: {ticker_input}")
        st.write(f"**gsubind:** 🧭 {gsubind}    **Industry:** {industry}")

        # Competitors
        all_peers   = ticker_data[gsubind_data == gsubind].tolist()
        competitors = [t for t in all_peers if t != ticker_input]
        st.write("**Competitors:**", ", ".join(competitors) or "None")

        # Build price_df
        eps_row       = eps_data.loc[idx].mask(eps_data.loc[idx] <= 0)
        median_pe_row = pd.Series(
            gsubind_to_median_pe.get(gsubind, [None]*len(years)),
            index=years,
        )
        model_price   = eps_row * median_pe_row
        actual_price  = actual_price_data.loc[ticker_input]

        price_df = pd.DataFrame({
            "Year": years,
            "EPS": eps_row.values,
            "Median PE": median_pe_row.values,
            "Model Price": model_price.values,
            "Actual Price": actual_price.values,
        })
        price_df["Prediction"] = np.where(model_price > actual_price, "Up", "Down")

        # Price Comparison Chart
        st.subheader(f"📈 {ticker_input}: Model vs Actual Price (1-Year Ahead)")
        years_actual = price_df["Year"]
        prices_actual = price_df["Actual Price"]
        years_model  = price_df["Year"] + 1
        prices_model = price_df["Model Price"]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(years_model, prices_model, marker="s", label="Model (t → t+1)")
        ax.plot(years_actual, prices_actual, marker="o", label="Actual (t)")
        ax.set_title(f"{ticker_input} Price Comparison")
        ax.set_xlabel("Year"); ax.set_ylabel("Price")
        ax.grid(True, linestyle="--", alpha=0.5)
        xticks = list(range(int(years_actual.min()), int(years_model.max())+1))
        ax.set_xticks(xticks); plt.xticks(rotation=45)
        ax.legend()
        st.pyplot(fig)

        # Hit-Rate Calculation
        total_predictions = 0
        correct_predictions = 0
        for year in range(2010, 2024):
            if pd.isna(model_price.get(year)): continue
            model_pred = "Up" if model_price[year] > actual_price[year] else "Down"
            if (year+1 in actual_price.index and pd.notna(actual_price.get(year+1))):
                m1 = "Up" if actual_price[year+1] > actual_price[year] else "Down"
                if model_pred == m1: correct_predictions += 1
                total_predictions += 1
            if (year+2 in actual_price.index and pd.notna(actual_price.get(year+2))):
                m2 = "Up" if actual_price[year+2] > actual_price[year] else "Down"
                if model_pred == m2: correct_predictions += 1
                total_predictions += 1

        overall_hit_rate = (
            (correct_predictions / total_predictions) * 100
            if total_predictions else np.nan
        )
        st.subheader("🎯 Overall Prediction Hit Rate Analysis")
        st.markdown(f"**Total Valid Predictions:** {total_predictions}")
        st.markdown(f"**Correct Predictions:** {correct_predictions}")
        if not np.isnan(overall_hit_rate):
            st.success(f"✅ Overall Average Hit Rate: **{overall_hit_rate:.2f}%**")
        else:
            st.warning("Not enough data to calculate hit rate.")

        st.dataframe(price_df, use_container_width=True)

        # 🔮 Final Prediction for 2024
        price_df.set_index("Year", inplace=True)
        if 2024 in price_df.index and not pd.isna(price_df.loc[2024, "Prediction"]):
            st.success(f"🔮 Final Prediction for 2024: {price_df.loc[2024, 'Prediction']}")
        else:
            st.warning("Prediction for 2024 not available.")

        # 🏆 Gsubind Average Hit Rate Comparison
        peer_indices = gsubind_data[gsubind_data == gsubind].index
        gsubind_total = 0
        gsubind_correct = 0
        for peer_idx in peer_indices:
            peer_tkr = ticker_data[peer_idx]
            if peer_tkr not in actual_price_data.index: continue
            peer_eps = eps_data.loc[peer_idx].mask(eps_data.loc[peer_idx] <= 0)
            peer_actual = actual_price_data.loc[peer_tkr]
            peer_median = pd.Series(
                gsubind_to_median_pe.get(gsubind, [None]*len(years)),
                index=years,
            )
            peer_model = peer_eps * peer_median
            for year in range(2010, 2024):
                if pd.isna(peer_model.get(year)): continue
                peer_pred = "Up" if peer_model[year] > peer_actual[year] else "Down"
                if (year+1 in peer_actual.index and pd.notna(peer_actual.get(year+1))):
                    n1 = "Up" if peer_actual[year+1] > peer_actual[year] else "Down"
                    if peer_pred == n1: gsubind_correct += 1
                    gsubind_total += 1
                if (year+2 in peer_actual.index and pd.notna(peer_actual.get(year+2))):
                    n2 = "Up" if peer_actual[year+2] > peer_actual[year] else "Down"
                    if peer_pred == n2: gsubind_correct += 1
                    gsubind_total += 1

        gsubind_hit_rate = (gsubind_correct / gsubind_total) * 100 if gsubind_total else np.nan
        st.subheader("🏆 Gsubind Average Hit Rate Comparison")
        st.markdown(f"**Your Stock Hit Rate:** {overall_hit_rate:.2f}%")
        if not np.isnan(gsubind_hit_rate):
            st.success(f"🏆 Gsubind Average Hit Rate: **{gsubind_hit_rate:.2f}%**")
        else:
            st.warning("Not enough data for gsubind hit rate.")

        # 🌍 Global Model Accuracy (All Stocks)
        global_total = 0
        global_correct = 0
        for peer_idx in range(len(ticker_data)):
            peer_tkr = ticker_data[peer_idx]
            peer_sub = gsubind_data[peer_idx]
            if peer_tkr not in actual_price_data.index: continue
            peer_eps = eps_data.loc[peer_idx].mask(eps_data.loc[peer_idx] <= 0)
            peer_actual = actual_price_data.loc[peer_tkr]
            peer_median = pd.Series(
                gsubind_to_median_pe.get(peer_sub, [None]*len(years)),
                index=years,
            )
            peer_model = peer_eps * peer_median
            for year in range(2010, 2024):
                if pd.isna(peer_model.get(year)): continue
                peer_pred = "Up" if peer_model[year] > peer_actual[year] else "Down"
                if (year+1 in peer_actual.index and pd.notna(peer_actual.get(year+1))):
                    nn1 = "Up" if peer_actual[year+1] > peer_actual[year] else "Down"
                    if peer_pred == nn1: global_correct += 1
                    global_total += 1
                if (year+2 in peer_actual.index and pd.notna(peer_actual.get(year+2))):
                    nn2 = "Up" if peer_actual[year+2] > peer_actual[year] else "Down"
                    if peer_pred == nn2: global_correct += 1
                    global_total += 1

        global_hit_rate = (global_correct / global_total) * 100 if global_total else np.nan
        st.subheader("🌍 Overall Model Accuracy (All Stocks)")
        if not np.isnan(global_hit_rate):
            st.success(f"🌟 Global Model Accuracy: **{global_hit_rate:.2f}%**")
        else:
            st.warning("Not enough data to calculate global model accuracy.")

    else:
        st.warning("❌ Ticker not found. Please select a valid ticker.")
