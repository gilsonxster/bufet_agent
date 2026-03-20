import yfinance as yf
import pandas as pd
import streamlit as st
import requests
import io

@st.cache_data(ttl=86400)
def get_sp500_sectors() -> dict:
    """Scrapes Wikipedia with a User-Agent to bypass 403 Forbidden blockers."""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        
        table = pd.read_html(io.StringIO(response.text))
        df = table[0]
        df['Symbol'] = df['Symbol'].str.replace('.', '-', regex=False)
        
        sectors_dict = {}
        for sector in df['GICS Sector'].unique():
            tickers = df[df['GICS Sector'] == sector]['Symbol'].tolist()
            sectors_dict[sector] = tickers
        return sectors_dict
    except Exception as e:
        print(f"Failed to scrape sectors: {e}")
        return {
            "Information Technology": ["AAPL", "MSFT", "NVDA"],
            "Financials": ["JPM", "BAC", "V", "MA"],
            "Energy": ["XOM", "CVX", "COP"]
        }

def buffett_lynch_screener(ticker_list: list) -> list:
    """Finds candidates meeting baseline ROE, PEG, and Debt-to-Equity rules"""
    candidates = []
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Use safety gets
            roe = info.get('returnOnEquity', 0)
            peg = info.get('pegRatio', 2.0)
            
            d_to_e_raw = info.get('debtToEquity', 200)
            # handle percentages vs decimals from yfinance
            d_to_e = d_to_e_raw / 100 if d_to_e_raw > 10 else d_to_e_raw
            
            if roe > 0.15 and peg < 1.2 and d_to_e < 0.8:
                candidates.append({
                    "ticker": ticker,
                    "ROE": f"{roe:.2%}" if roe else "N/A",
                    "PEG": peg,
                    "Debt_to_Equity": d_to_e
                })
        except Exception as e:
            print(f"Error screening {ticker}: {e}")
            continue
            
    return candidates

def get_stock_data(ticker_symbol: str) -> dict:
    """Fetches key financial data for a given ticker."""
    stock = yf.Ticker(ticker_symbol)
    
    # yfinance `.info` often contains multiple ratios including PEG, ROE, debtToEquity
    try:
        info = stock.info
    except Exception as e:
        print(f"Error fetching info for {ticker_symbol}: {e}")
        info = {}
        
    try:
        financials = stock.financials
    except:
        financials = pd.DataFrame()
        
    try:
        balance_sheet = stock.balance_sheet
    except:
        balance_sheet = pd.DataFrame()
        
    try:
        cashflow = stock.cashflow
    except:
        cashflow = pd.DataFrame()
        
    return {
        "ticker": ticker_symbol.upper(),
        "info": info,
        "financials": financials,
        "balance_sheet": balance_sheet,
        "cashflow": cashflow
    }

def load_watchlist(symbols: list) -> list:
    """Given a list of symbols, fetch data for all of them."""
    data = []
    for sym in symbols:
        print(f"Fetching data for {sym}...")
        stock_data = get_stock_data(sym)
        data.append(stock_data)
    return data

if __name__ == "__main__":
    # Test data loader with a sample ticker
    sample_data = load_watchlist(["AAPL"])
    
    if sample_data:
        appl_info = sample_data[0]["info"]
        print(f"Name: {appl_info.get('shortName')}")
        print(f"Sector: {appl_info.get('sector')}")
        print(f"PEG Ratio: {appl_info.get('pegRatio')}")
        print(f"Return on Equity: {appl_info.get('returnOnEquity')}")
        print(f"Debt to Equity: {appl_info.get('debtToEquity')}")
