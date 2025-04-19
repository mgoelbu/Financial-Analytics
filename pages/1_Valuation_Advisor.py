import streamlit as st
from helpers.peer_lookup import get_peers
from helpers.valuation_logic import analyze_valuation, plot_peers, plot_price_range

st.title("📊 Valuation & Recommendation")

ticker_input = st.text_input("Enter a ticker symbol", "TGT")

if ticker_input:
    peers, sector, industry = get_peers(ticker_input.upper())
    
    if peers:
        st.markdown(f"**Sector:** {sector}  \n**Industry:** {industry}  \n**Peers:** {', '.join(peers)}")
        result = analyze_valuation(ticker_input.upper(), peers)
        
        st.metric("EPS (TTM)", f"{result['eps']:.2f}" if result['eps'] else "N/A")
        st.metric("Industry Avg P/E", f"{result['industry_pe_avg']:.2f}")
        
        st.subheader("Recommendation")
        st.success(result['recommendation'])

    else:
        st.warning("Could not fetch peer data.")

st.subheader("📉 Valuation Range Visualization")
plot_price_range(
    result['current_price'],
    result['implied_price_min'],
    result['implied_price_max'],
    result['implied_price']
)
