import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 📥 Load Data
@st.cache_data
def load_data():
    file_path = 'data/Master data price eps etc.xlsx'

    # Company Dta sheet
    company_data = pd.read_excel(file_path, sheet_name='Company Dta', header=None)
    headers = company_data.iloc[3]
    company_data.columns = headers
    company_data = company_data.iloc[4:].reset_index(drop=True)

    # EPS & Price blocks
    eps_data = company_data.iloc[:, 9:24].apply(pd.to_numeric, errors='coerce')
    price_data = company_data.iloc[:, 25:40].apply(pd.to_numeric, errors='coerce')
    eps_data.columns = list(range(2010, 2025))
    price_data.columns = list(range(2010, 2025))

    # Ticker & gsubind
    ticker_data = company_data.iloc[:, 0].reset_index(drop=True)
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
    actual_price.index = analysis_trim.iloc[:, 0]

    return (
        company_data,
        eps_data,
        price_data,
        ticker_data,
        gsubind_data,
        gsubind_to_median_pe,
        actual_price,
    )

# 🚀 Load
(
    company_data,
    eps_data,
    price_data,
    ticker_data,
    gsubind_data,
    gsubind_to_median_pe,
    actual_price_data,
) = load_data()
years = list(range(2010, 2025))

# 📊 App header
st.title("📊 Company Stock Valuation Analysis")

# ▶️ Ticker dropdown
tickers = ticker_data.tolist()
ticker_input = st.selectbox("Choose a ticker", options=tickers)

if ticker_input and (ticker_input in ticker_data.values):
    # Identify row
    idx = ticker_data[ticker_data == ticker_input].index[0]

    # gsubind & industry
    gsubind = gsubind_data[idx]
    industry = company_data.loc[idx, "Industry"]
    st.subheader(f"Details for: {ticker_input}")
    st.write(f"**gsubind:** 🧭 {gsubind}    **Industry:** {industry}")

    # Competitors in same sub-industry
    all_peers = ticker_data[gsubind_data == gsubind].tolist()
    competitors = [t for t in all_peers if t != ticker_input]
    st.write("**Competitors:**", ", ".join(competitors) or "None")

    # Build the DataFrame of values
    eps_row = eps_data.loc[idx].mask(eps_data.loc[idx] <= 0)
    median_pe_row = pd.Series(
        gsubind_to_median_pe.get(gsubind, [None]*len(years)),
        index=years,
    )
    model_price = eps_row * median_pe_row
    actual_price = actual_price_data.loc[ticker_input]

    price_df = pd.DataFrame({
        "Year": years,
        "EPS": eps_row.values,
        "Median PE": median_pe_row.values,
        "Model Price": model_price.values,
        "Actual Price": actual_price.values,
    })
    price_df["Prediction"] = np.where(model_price > actual_price, "Up", "Down")

    # ▶️ 1-Year-Ahead Price Comparison Chart
    st.subheader(f"📈 {ticker_input}: Model vs Actual Price (1-Year Ahead)")
    years_actual = price_df["Year"]
    prices_actual = price_df["Actual Price"]
    years_model = price_df["Year"] + 1
    prices_model = price_df["Model Price"]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years_model, prices_model, marker="s", label="Model (t → t+1)")
    ax.plot(years_actual, prices_actual, marker="o", label="Actual (t)")
    ax.set_title(f"{ticker_input} Price Comparison")
    ax.set_xlabel("Year")
    ax.set_ylabel("Price")
    ax.grid(True, linestyle="--", alpha=0.5)
    xticks = list(range(int(years_actual.min()), int(years_model.max())+1))
    ax.set_xticks(xticks)
    plt.xticks(rotation=45)
    ax.legend()
    st.pyplot(fig)

    # ▶️ Hit-Rate Calculation
    total_predictions = 0
    correct_predictions = 0

    for year in range(2010, 2024):
        if pd.isna(model_price.get(year)):
            continue
        model_pred = "Up" if model_price[year] > actual_price[year] else "Down"

        # one-year ahead
        if (year+1 in actual_price.index) and pd.notna(actual_price.get(year+1)):
            move1 = "Up" if actual_price[year+1] > actual_price[year] else "Down"
            if model_pred == move1:
                correct_predictions += 1
            total_predictions += 1

        # two-year ahead
        if (year+2 in actual_price.index) and pd.notna(actual_price.get(year+2)):
            move2 = "Up" if actual_price[year+2] > actual_price[year] else "Down"
            if model_pred == move2:
                correct_predictions += 1
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

    # 🏆 Gsubind Average Hit Rate
    peer_indices = gsubind_data[gsubind_data == gsubind].index
    gsubind_total = 0
    gsubind_correct = 0
    for peer_idx in peer_indices:
        peer_tkr = ticker_data[peer_idx]
        if peer_tkr not in actual_price_data.index:
            continue
        peer_eps = eps_data.loc[peer_idx].mask(eps_data.loc[peer_idx] <= 0)
        peer_actual = actual_price_data.loc[peer_tkr]
        peer_median = pd.Series(gsubind_to_median_pe.get(gsubind, [None]*len(years)), index=years)
        peer_model = peer_eps * peer_median
        for year in range(2010, 2024):
            if pd.isna(peer_model.get(year)):
                continue
            peer_pred = "Up" if peer_model[year] > peer_actual[year] else "Down"
            if (year+1 in peer_actual.index) and pd.notna(peer_actual.get(year+1)):
                nxt1 = "Up" if peer_actual[year+1] > peer_actual[year] else "Down"
                if peer_pred == nxt1:
                    gsubind_correct += 1
                gsubind_total += 1
            if (year+2 in peer_actual.index) and pd.notna(peer_actual.get(year+2)):
                nxt2 = "Up" if peer_actual[year+2] > peer_actual[year] else "Down"
                if peer_pred == nxt2:
                    gsubind_correct += 1
                gsubind_total += 1

    gsubind_hit_rate = (gsubind_correct / gsubind_total) * 100 if gsubind_total else np.nan
    st.subheader("🏆 Gsubind Average Hit Rate Comparison")
    st.markdown(f"**Your Stock Hit Rate:** {overall_hit_rate:.2f}%")
    if not np.isnan(gsubind_hit_rate):
        st.success(f"🏆 Gsubind Average Hit Rate: **{gsubind_hit_rate:.2f}%**")
    else:
        st.warning("Not enough data for gsubind hit rate.")

    # 🌍 Global Model Accuracy
    global_total = 0
    global_correct = 0
    for peer_idx in range(len(ticker_data)):
        peer_tkr = ticker_data[peer_idx]
        peer_sub  = gsubind_data[peer_idx]
        if peer_tkr not in actual_price_data.index:
            continue
        peer_eps = eps_data.loc[peer_idx].mask(eps_data.loc[peer_idx] <= 0)
        peer_actual = actual_price_data.loc[peer_tkr]
        peer_median = pd.Series(gsubind_to_median_pe.get(peer_sub, [None]*len(years)), index=years)
        peer_model = peer_eps * peer_median
        for year in range(2010, 2024):
            if pd.isna(peer_model.get(year)):
                continue
            peer_pred = "Up" if peer_model[year] > peer_actual[year] else "Down"
            if (year+1 in peer_actual.index) and pd.notna(peer_actual.get(year+1)):
                nxt1 = "Up" if peer_actual[year+1] > peer_actual[year] else "Down"
                if peer_pred == nxt1:
                    global_correct += 1
                global_total += 1
            if (year+2 in peer_actual.index) and pd.notna(peer_actual.get(year+2)):
                nxt2 = "Up" if peer_actual[year+2] > peer_actual[year] else "Down"
                if peer_pred == nxt2:
                    global_correct += 1
                global_total += 1

    global_hit_rate = (global_correct / global_total) * 100 if global_total else np.nan
    st.subheader("🌍 Overall Model Accuracy (All Stocks)")
    if not np.isnan(global_hit_rate):
        st.success(f"🌟 Global Model Accuracy: **{global_hit_rate:.2f}%**")
    else:
        st.warning("Not enough data to calculate global model accuracy.")

else:
    st.warning("Please select a valid ticker from the dropdown.")
