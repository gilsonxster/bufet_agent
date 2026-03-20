import streamlit as st
import asyncio
from bufet_agent import run_bufet_pipeline
from data_loader import get_sp500_sectors

st.set_page_config(page_title="Bufet AI System", layout="wide")

st.title("📈 Bufet AI Agent System")
st.markdown("Select a market sector or type your own custom tickers. The **Screener Agent** will filter them, and the **Analyst Panel** will dive deep to find the Top 5 consensus buys, grounded with real-time news.")

with st.sidebar:
    st.header("Settings")
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""
        
    user_key_input = st.text_input("Gemini API Key (Optional)", value=st.session_state.user_api_key, type="password", help="Leave blank to use the app's default shared API key.")
    if user_key_input:
        st.session_state.user_api_key = user_key_input
        
    st.markdown("---")
    st.header("Watchlist")
    
    input_mode = st.radio("Input Mode:", ["Market Sector", "Custom Tickers"])
    
    selected_tickers = []
    
    if input_mode == "Market Sector":
        sector_dict = get_sp500_sectors()
        sector = st.selectbox("Choose an S&P 500 Sector:", list(sector_dict.keys()))
        selected_tickers = sector_dict[sector]
        st.write(f"**{len(selected_tickers)}** active S&P 500 tickers identified in this sector (These will individually be passed through the Fundamental Screener!):")
        
    else:
        custom_input = st.text_area("Enter Tickers (comma separated):", "MSTR, PLTR, COIN, RKLB, ASTS")
        if custom_input:
            selected_tickers = [x.strip().upper() for x in custom_input.split(",") if x.strip()]

run_btn = st.button("Run Multi-Agent Pipeline", type="primary")

if run_btn:
    if not selected_tickers:
        st.error("Please provide at least one ticker.")
    else:
        with st.spinner(f"Agents are currently analyzing {len(selected_tickers)} stocks... (This may take several minutes)"):
            try:
                # Streamlit runs in a synchronous loop, so we use asyncio.run
                final_report = asyncio.run(run_bufet_pipeline(selected_tickers, st.session_state.user_api_key))
                
                if final_report:
                    st.success("Analysis Complete!")
                    st.markdown("---")
                    st.markdown(final_report)
                else:
                    st.error("The pipeline finished but returned no report. Are you completely rate limited?")
            except Exception as e:
                st.error(f"An error occurred: {e}")
