import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 📥 Load Data
@st.cache_data
def load_data():
    file_path = 'data/Master data price eps etc.xlsx'

    company_data = pd.read_excel(
        file_path, sheet_name='Company Dta', header=None
    )
    # Use row 4 (0-indexed row 3) as header
    headers = company_data.iloc[3]
    company_data.columns = headers
    company_data = company_data.iloc[4:].reset_index(drop=True)

    # EPS and Price blocks
    eps_data = company_data.iloc[:, 9:24].apply(
        pd.to_numeric, errors='coerce'
    )
    price_data = company_data.iloc[:, 25:40].apply(
        pd.to_numeric, errors='coerce'
    )
    eps_data.columns = list(range(2010, 2025))
    price_data.columns = list(range(2010, 2025))

    ticker_data  = company_data.iloc[:, 0].reset_index(drop=True)
    gsubind_data = company_data['gsubind'].reset_index(drop=True)

    # Median PE sheet
    median_pe = pd.read_excel(
        file_path, sheet_name='Median PE', header=None
    )
    median_pe_trim = median_pe.iloc[5:, :18].reset_index(drop=True)
    median_pe_trim.columns = [None, None, 'gsubind'] + list(range(2010, 2025))
    gsubind_to_median_pe = {
        row['gsubind']: row[3:].values
        for _, row in median_pe_trim.iterrows()
    }

    # Analysis sheet → actual price history
    analysis = pd.read_excel(
        file_path, sheet_name='Analysis', header=None
    )
    analysis_trim = analysis.iloc[5:, :40].reset_index(drop=True)
    actual_price = analysis_trim.iloc[:, 24:39].apply(
        pd.to_numeric, errors='coerce'
    )
    actual_price.columns = list(range(2010, 2025))
    actual_price.index   = analysis_trim.iloc[:, 0]

    return (
        company_data,
        eps_data,
        price_data,
        ticker_data,
        gsubind_data,
        gsubind_to_median_pe,
        actual_price,
    )

# 🚀 Load everything
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

# 📊 App UI
st.title("📊 Company Stock Valuation Analysis")

# ▶️ Ticker dropdown
tickers      = ticker_data.tolist()
ticker_input = st.selectbox("Choose a ticker", options=tickers)

if ticker_input and (ticker_input in ticker_data.values):
    idx      = ticker_data[ticker_data == ticker_input].index[0]
    gsubind  = gsubind_data[idx]
    industry = company_data.loc[idx, "Industry"]

    st.subheader(f"Details for: {ticker_input}")
    st.write(f"**gsubind:** {gsubind}   **Industry:** {industry}")

    # ▶️ Competitors
    all_peers   = ticker_data[gsubind_data == gsubind].tolist()
    competitors = [t for t in all_peers if t != ticker_input]
    st.write("**Competitors:**", ", ".join(competitors) or "None")

    # ▶️ Build price_df
    eps_row      = eps_data.loc[idx].mask(eps_data.loc[idx] <= 0)
    median_pe_row= pd.Series(
        gsubind_to_median_pe.get(gsubind, [None]*len(years)),
        index=years,
    )
    model_price  = eps_row * median_pe_row

    actual_price = actual_price_data.loc[ticker_input]

    price_df = pd.DataFrame({
        "Year": years,
        "EPS": eps_row.values,
        "Median PE": median_pe_row.values,
        "Model Price": model_price.values,
        "Actual Price": actual_price.values,
    })
    price_df["Prediction"] = np.where(
        model_price > actual_price, "Up", "Down"
    )

    # ▶️ Clean line chart
    st.subheader(f"📈 {ticker_input}: Model vs Actual Price")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(price_df["Year"], price_df["Model Price"],
            marker="o", label="Model")
    ax.plot(price_df["Year"], price_df["Actual Price"],
            marker="o", label="Actual")
    ax.set_title(f"{ticker_input} Price Comparison")
    ax.set_xlabel("Year"); ax.set_ylabel("Price")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xticks(price_df["Year"][::2])
    plt.xticks(rotation=45)
    ax.legend()
    st.pyplot(fig)

    # ▶️ Hit-rate calculation
    total_predictions = 0
    correct_predictions = 0

    for year in range(2010, 2024):
        if pd.isna(model_price.get(year)): continue

        model_pred = ("Up" if model_price[year] > actual_price[year]
                                else "Down")

        # one-year
        if (year+1 in actual_price.index and
            pd.notna(actual_price.get(year+1))):
            move = ("Up" if actual_price[year+1] > actual_price[year]
                             else "Down")
            if model_pred == move: correct_predictions += 1
            total_predictions += 1

        # two-year (optional)
        if (year+2 in actual_price.index and
            pd.notna(actual_price.get(year+2))):
            move2 = ("Up" if actual_price[year+2] > actual_price[year]
                              else "Down")
            if model_pred == move2: correct_predictions += 1
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

    # …continue your Gsubind and global accuracy blocks here…

else:
    st.warning("Please select a valid ticker from the dropdown.")
