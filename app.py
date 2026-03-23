import streamlit as st
import asyncio
import os
import re
from datetime import datetime
from bufet_agent import run_bufet_pipeline
from data_loader import get_index_sectors
from drive_utils import upload_to_drive, is_authenticated, list_drive_files, get_drive_file_content, get_drive_service

def add_ticker_links(report, tickers):
    for ticker in tickers:
        pattern = rf'(?<![=/\["-])\b{re.escape(ticker)}\b(?![\]<"-])'
        replacement = f'<a href="https://finance.yahoo.com/quote/{ticker}" target="_blank">{ticker}</a>'
        report = re.sub(pattern, replacement, report)
    return report

st.set_page_config(page_title="Bufet AI Agent", layout="wide")

# Secret navigation via query params
query_params = st.query_params
if "page" in query_params and query_params["page"] == "drive_reports":
    page = "Drive Reports"
else:
    page = "Analyst Panel"

if page == "Analyst Panel":
    st.title("📈 Bufet AI Agent")
    st.markdown("Select a market sector or type your own custom tickers. The **Screener Agent** will filter them, and the **Analyst Panel** will dive deep to find the Top 5 consensus buys, grounded with real-time news.")

    with st.sidebar:
        st.header("Settings")
        if "user_api_key" not in st.session_state:
            st.session_state.user_api_key = ""
        if "report_history" not in st.session_state:
            st.session_state.report_history = []
            
        user_key_input = st.text_input("Gemini API Key (Optional)", value=st.session_state.user_api_key, type="password", help="Leave blank to use the app's default shared API key.")
        if user_key_input:
            st.session_state.user_api_key = user_key_input
            
        st.markdown("---")
        st.header("Watchlist")
        
        input_mode = st.radio("Input Mode:", ["Market Index", "Custom Tickers"])
        
        selected_tickers = []
        
        if input_mode == "Market Index":
            indices = ["S&P 500", "Nasdaq 100", "Dow Jones 30", "Russell 1000 (Small/Mid Cap)", "FTSE 100 (UK)", "EURO STOXX 50 (Europe)"]
            index_choice = st.selectbox("Choose a Market Index:", indices)
            sector_dict = get_index_sectors(index_choice)
            sector = st.selectbox(f"Choose a Sector within {index_choice}:", list(sector_dict.keys()))
            selected_tickers = sector_dict[sector]
            st.write(f"**{len(selected_tickers)}** active tickers identified in this sector (These will individually be passed through the Fundamental Screener!):")
            
        else:
            custom_input = st.text_area("Enter Tickers (comma separated):", "MSTR, PLTR, COIN, RKLB, ASTS")
            if custom_input:
                selected_tickers = [x.strip().upper() for x in custom_input.split(",") if x.strip()]

        st.markdown("---")
        st.header("Session History")
        if not st.session_state.report_history:
            st.info("No prior reports generated.")
        else:
            for i, past_report in enumerate(reversed(st.session_state.report_history)):
                with st.expander(past_report['title']):
                    file_name = past_report.get('file_name', f"bufet_report_{i}.md")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download .md",
                            data=past_report['content'],
                            file_name=file_name,
                            mime="text/markdown",
                            key=f"hist_dl_{i}"
                        )
                    with col2:
                        if st.button("View", key=f"hist_view_{i}"):
                            st.session_state.view_report = past_report['content']

    if "view_report" in st.session_state and st.session_state.view_report:
        st.markdown("---")
        st.subheader("Viewing Past Report")
        if st.button("Close Viewer"):
            st.session_state.view_report = None
            st.rerun()
        st.markdown(st.session_state.view_report, unsafe_allow_html=True)
        st.markdown("---")

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
                        # 1. Format Ticker Links
                        final_report = add_ticker_links(final_report, selected_tickers)
                        
                        # 2. Dynamic Filename
                        timestamp = datetime.now().strftime("%Y%m%dT%H%M")
                        if input_mode == "Market Index":
                            safe_sector = sector.replace(' ', '_').replace('/', '_').lower()
                            dl_file_name = f"index_{safe_sector}_{timestamp}.md"
                        else:
                            dl_file_name = f"custom_{timestamp}.md"

                        title_name = sector if input_mode == "Market Index" else "Custom Watchlist"
                        st.session_state.report_history.append({
                            "title": f"Report: {title_name} - {timestamp}", 
                            "content": final_report,
                            "file_name": dl_file_name
                        })
                        
                        st.success("Analysis Complete!")
                        st.download_button(
                            label="Download Full Master Report (.md)",
                            data=final_report,
                            file_name=dl_file_name,
                            mime="text/markdown",
                            type="primary"
                        )
                        
                        # 3. Upload to Google Drive
                        folder_id = os.getenv("DRIVE_FOLDER_ID")
                        if folder_id:
                            with st.spinner("Uploading report to Google Drive..."):
                                drive_file_id = upload_to_drive(final_report, dl_file_name, folder_id)
                                if drive_file_id:
                                    st.success(f"Successfully uploaded to Google Drive! (File ID: {drive_file_id})")
                                else:
                                    st.warning("Google Drive upload failed. Please authenticate via Settings first.")
                        else:
                            st.warning("No DRIVE_FOLDER_ID found in environment variables.")
                        
                        st.markdown("---")
                        st.markdown(final_report, unsafe_allow_html=True)
                    else:
                        st.error("The pipeline finished but returned no report. Are you completely rate limited?")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

elif page == "Drive Reports":
    st.title("📂 Google Drive Reports")
    from dotenv import load_dotenv
    load_dotenv()
    
    st.markdown("---")
    st.header("Drive Authentication Settings")
    
    if not os.path.exists('credentials.json') and not os.path.exists('service_account.json'):
        st.info("No credentials found. Please upload your Google Drive `credentials.json` or `service_account.json`.")
        uploaded_file = st.file_uploader("Upload Credentials (JSON)", type=["json"])
        if uploaded_file is not None:
            file_name = uploaded_file.name
            if file_name in ["credentials.json", "service_account.json"]:
                with open(file_name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Saved {file_name} successfully!")
                st.rerun()
            else:
                st.error("Please ensure the uploaded file is named exactly 'credentials.json' or 'service_account.json'")

    if is_authenticated():
        st.success("✅ Google Drive is Authenticated")
    else:
        st.warning("⚠️ Google Drive not authenticated.")
        if st.button("Authenticate Drive"):
            with st.spinner("Follow the instructions in the popup/terminal..."):
                get_drive_service()
                st.rerun()
        st.caption("You will be prompted to log in. Provide credentials.json if missing.")
    st.markdown("---")

    folder_id = os.getenv("DRIVE_FOLDER_ID")
    
    if not is_authenticated():
        st.warning("Google Drive is not authenticated. Please authenticate above.")
    elif not folder_id:
        st.warning("No DRIVE_FOLDER_ID found in .env. Please configure your target Drive Folder.")
    else:
        with st.spinner("Fetching files from Google Drive..."):
            files = list_drive_files(folder_id)
            
        if not files:
            st.info("No reports found in the designated Drive Folder.")
        else:
            st.success(f"Found {len(files)} reports in Drive.")
            
            # Simple list and view selection
            file_options = {f"{f['name']} (Created: {f.get('createdTime', 'Unknown')})": f['id'] for f in files}
            selected_file = st.selectbox("Select a report to view", list(file_options.keys()))
            
            if st.button("Fetch and View Report", type="primary"):
                file_id = file_options[selected_file]
                with st.spinner("Downloading report content..."):
                    content = get_drive_file_content(file_id)
                if content:
                    st.download_button(
                        label="Download Local Copy",
                        data=content,
                        file_name=selected_file.split(" (")[0],
                        mime="text/markdown"
                    )
                    st.markdown("---")
                    st.markdown(content, unsafe_allow_html=True)
                else:
                    st.error("Failed to fetch report content.")
