import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 📥 Load Data
@st.cache_data
def load_data():
    file_path = 'data/Master data price eps etc.xlsx'

    company_data = pd.read_excel(file_path, sheet_name='Company Dta', header=None)
    headers = company_data.iloc[3]
    company_data.columns = headers
    company_data = company_data.iloc[4:].reset_index(drop=True)

    eps_data = company_data.iloc[:, 9:24].apply(pd.to_numeric, errors='coerce')
    price_data = company_data.iloc[:, 25:40].apply(pd.to_numeric, errors='coerce')
    eps_data.columns = list(range(2010, 2025))
    price_data.columns = list(range(2010, 2025))

    ticker_data = company_data.iloc[:, 0].reset_index(drop=True)
    gsubind_data = company_data['gsubind'].reset_index(drop=True)

    median_pe = pd.read_excel(file_path, sheet_name='Median PE', header=None)
    median_pe_data_trimmed = median_pe.iloc[5:, :18].reset_index(drop=True)
    median_pe_data_trimmed.columns = [None, None, 'gsubind'] + list(range(2010, 2025))
    gsubind_to_median_pe = {
        row['gsubind']: row[3:].values
        for _, row in median_pe_data_trimmed.iterrows()
    }

    analysis_data = pd.read_excel(file_path, sheet_name='Analysis', header=None)
    analysis_data_trimmed = analysis_data.iloc[5:, :40].reset_index(drop=True)
    actual_price_data = analysis_data_trimmed.iloc[:, 24:39].apply(
        pd.to_numeric, errors='coerce'
    )
    actual_price_data.columns = list(range(2010, 2025))
    actual_price_data.index = analysis_data_trimmed.iloc[:, 0]

    return (
        company_data,
        eps_data,
        price_data,
        ticker_data,
        gsubind_data,
        gsubind_to_median_pe,
        actual_price_data,
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

# 📊 Streamlit App
st.title("📊 Company Stock Valuation Analysis")
# ▶️ Let user pick from the known universe
tickers = ticker_data.tolist()
ticker_input = st.selectbox("Choose a ticker", options=tickers)


if ticker_input:
    if ticker_input in ticker_data.values:
        idx = ticker_data[ticker_data == ticker_input].index[0]

        st.subheader(f"Details for: {ticker_input}")
        gsubind = gsubind_data[idx]
        st.write("**gsubind:**", f"🧭 {gsubind}")

        eps_row = eps_data.loc[idx].mask(eps_data.loc[idx] <= 0)  # replace <=0 with NaN
        median_pe_row = pd.Series(
            gsubind_to_median_pe.get(gsubind, [None] * len(years)),
            index=years,
        )
        model_price = eps_row * median_pe_row

        try:
            actual_price = actual_price_data.loc[ticker_input]
        except KeyError:
            st.error(f"Ticker '{ticker_input}' not found in actual‐price data.")
            st.stop()

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

        # ▶️ Detailed line chart with annotations
        st.subheader(f"📈 {ticker_input}: Model vs Actual Price")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(price_df["Year"], price_df["Model Price"], marker="o", label="Model")
        ax.plot(price_df["Year"], price_df["Actual Price"], marker="o", label="Actual")
        
        ax.set_title(f"{ticker_input} Price Comparison")
        ax.set_xlabel("Year")
        ax.set_ylabel("Price")
        ax.grid(True, linestyle="--", alpha=0.5)
        
        # show every other year to avoid crowding
        years = price_df["Year"].tolist()
        ax.set_xticks(years[::2])
        plt.xticks(rotation=45)
        
        ax.legend()
        st.pyplot(fig)

        # 🎯 Hit Rate Calculation
        total_predictions = 0
        correct_predictions = 0

        for year in range(2010, 2024):
            if year not in price_df["Year"].values:
                continue
            if pd.isna(model_price.get(year)):
                continue

            model_pred = (
                "Up"
                if model_price[year] > actual_price[year]
                else "Down"
            )

            if (year + 1 in actual_price.index) and pd.notna(
                actual_price.get(year + 1)
            ):
                actual_move_next = (
                    "Up"
                    if actual_price[year + 1] > actual_price[year]
                    else "Down"
                )
                if model_pred == actual_move_next:
                    correct_predictions += 1
                total_predictions += 1

            if (year + 2 in actual_price.index) and pd.notna(
                actual_price.get(year + 2)
            ):
                actual_move_second = (
                    "Up"
                    if actual_price[year + 2] > actual_price[year]
                    else "Down"
                )
                if model_pred == actual_move_second:
                    correct_predictions += 1
                total_predictions += 1

        if total_predictions > 0:
            overall_hit_rate = (correct_predictions / total_predictions) * 100
        else:
            overall_hit_rate = np.nan

        st.subheader("🎯 Overall Prediction Hit Rate Analysis")
        st.markdown(f"**Total Valid Predictions:** {total_predictions}")
        st.markdown(f"**Correct Predictions:** {correct_predictions}")
        if not np.isnan(overall_hit_rate):
            st.success(
                f"✅ Overall Average Hit Rate: **{overall_hit_rate:.2f}%**"
            )
        else:
            st.warning("Not enough data to calculate hit rate.")

        st.dataframe(price_df, use_container_width=True)

        # 🔮 Final Prediction for 2024
        price_df.set_index("Year", inplace=True)
        if 2024 in price_df.index and not pd.isna(
            price_df.loc[2024, "Prediction"]
        ):
            st.success(
                f"🔮 Final Prediction for 2024: {price_df.loc[2024, 'Prediction']}"
            )
        else:
            st.warning("Prediction for 2024 not available.")

        # 🏆 Gsubind Average Accuracy
        peer_indices = gsubind_data[gsubind_data == gsubind].index
        gsubind_total = 0
        gsubind_correct = 0

        for peer_idx in peer_indices:
            peer_ticker = ticker_data[peer_idx]
            if peer_ticker not in actual_price_data.index:
                continue
            try:
                peer_eps = eps_data.loc[peer_idx].mask(eps_data.loc[peer_idx] <= 0)
                peer_actual = actual_price_data.loc[peer_ticker]
                peer_median = pd.Series(
                    gsubind_to_median_pe.get(gsubind, [None] * len(years)),
                    index=years,
                )
                peer_model = peer_eps * peer_median

                for year in range(2010, 2024):
                    if pd.isna(peer_model.get(year)):
                        continue
                    peer_pred = (
                        "Up"
                        if peer_model[year] > peer_actual[year]
                        else "Down"
                    )

                    if (year + 1 in peer_actual.index) and pd.notna(
                        peer_actual.get(year + 1)
                    ):
                        nxt = (
                            "Up"
                            if peer_actual[year + 1] > peer_actual[year]
                            else "Down"
                        )
                        if peer_pred == nxt:
                            gsubind_correct += 1
                        gsubind_total += 1

                    if (year + 2 in peer_actual.index) and pd.notna(
                        peer_actual.get(year + 2)
                    ):
                        nxt2 = (
                            "Up"
                            if peer_actual[year + 2] > peer_actual[year]
                            else "Down"
                        )
                        if peer_pred == nxt2:
                            gsubind_correct += 1
                        gsubind_total += 1

            except Exception:
                continue

        if gsubind_total > 0:
            gsubind_hit_rate = (gsubind_correct / gsubind_total) * 100
        else:
            gsubind_hit_rate = np.nan

        st.subheader("🏆 Gsubind Average Hit Rate Comparison")
        st.markdown(f"**Your Stock Hit Rate:** {overall_hit_rate:.2f}%")
        if not np.isnan(gsubind_hit_rate):
            st.success(f"🏆 Gsubind Average Hit Rate: **{gsubind_hit_rate:.2f}%**")
        else:
            st.warning("Not enough data for gsubind hit rate.")

        # 🌍 Overall Model Accuracy (All Stocks)
        global_total = 0
        global_correct = 0

        for peer_idx in range(len(ticker_data)):
            peer_ticker = ticker_data[peer_idx]
            peer_gsubind = gsubind_data[peer_idx]
            if peer_ticker not in actual_price_data.index:
                continue
            try:
                peer_eps = eps_data.loc[peer_idx].mask(eps_data.loc[peer_idx] <= 0)
                peer_actual = actual_price_data.loc[peer_ticker]
                peer_median = pd.Series(
                    gsubind_to_median_pe.get(peer_gsubind, [None] * len(years)),
                    index=years,
                )
                peer_model = peer_eps * peer_median

                for year in range(2010, 2024):
                    if pd.isna(peer_model.get(year)):
                        continue
                    peer_pred = (
                        "Up"
                        if peer_model[year] > peer_actual[year]
                        else "Down"
                    )

                    if (year + 1 in peer_actual.index) and pd.notna(
                        peer_actual.get(year + 1)
                    ):
                        nxt = (
                            "Up"
                            if peer_actual[year + 1] > peer_actual[year]
                            else "Down"
                        )
                        if peer_pred == nxt:
                            global_correct += 1
                        global_total += 1

                    if (year + 2 in peer_actual.index) and pd.notna(
                        peer_actual.get(year + 2)
                    ):
                        nxt2 = (
                            "Up"
                            if peer_actual[year + 2] > peer_actual[year]
                            else "Down"
                        )
                        if peer_pred == nxt2:
                            global_correct += 1
                        global_total += 1

            except Exception:
                continue

        if global_total > 0:
            global_hit_rate = (global_correct / global_total) * 100
        else:
            global_hit_rate = np.nan

        st.subheader("🌍 Overall Model Accuracy (All Stocks)")
        if not np.isnan(global_hit_rate):
            st.success(f"🌟 Global Model Accuracy: **{global_hit_rate:.2f}%**")
        else:
            st.warning("Not enough data for global model accuracy.")

    else:
        st.warning("Ticker not found. Please check again.")
