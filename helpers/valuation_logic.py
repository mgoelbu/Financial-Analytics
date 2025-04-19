import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st

import yfinance as yf

def analyze_valuation(ticker_symbol, peers):
    all_pe_ratios = {}
    eps = None

    tickers = [ticker_symbol] + peers
    for t in tickers:
        info = yf.Ticker(t).info
        pe = info.get("trailingPE", None)
        eps_val = info.get("trailingEps", None)
        if t == ticker_symbol:
            eps = eps_val
        if pe is not None and pe > 0:
            all_pe_ratios[t] = pe

    pe_values = list(all_pe_ratios.values())
    industry_pe_avg = sum(pe_values) / len(pe_values)
    min_pe = min(pe_values)
    max_pe = max(pe_values)

    implied_price = industry_pe_avg * eps if eps else None
    implied_price_min = min_pe * eps if eps else None
    implied_price_max = max_pe * eps if eps else None
    current_price = yf.Ticker(ticker_symbol).history(period="1d")['Close'][-1]

    if implied_price:
        if current_price < 0.95 * implied_price:
            decision = "✅ Likely Undervalued — Consider Buying"
        elif current_price > 1.1 * implied_price:
            decision = "❌ Overvalued Compared to Peers"
        else:
            decision = "🤔 Fairly Priced — Hold or Watch"
    else:
        decision = "⚠️ EPS or P/E unavailable"

    return {
        "peers": all_pe_ratios,
        "eps": eps,
        "industry_pe_avg": industry_pe_avg,
        "min_pe": min_pe,
        "max_pe": max_pe,
        "implied_price": implied_price,
        "implied_price_min": implied_price_min,
        "implied_price_max": implied_price_max,
        "current_price": current_price,
        "recommendation": decision
    }


def plot_peers(peers_dict, highlight):
    fig, ax = plt.subplots()
    labels = list(peers_dict.keys())
    values = list(peers_dict.values())
    colors = ['#ff7f0e' if lbl == highlight else '#1f77b4' for lbl in labels]
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("P/E Ratio")
    ax.set_title("P/E Ratio vs Peers")
    st.pyplot(fig)

