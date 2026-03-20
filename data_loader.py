import yfinance as yf
import logging
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

import pandas as pd
import streamlit as st
import requests
import io

@st.cache_data(ttl=86400)
def get_index_sectors(index_name: str) -> dict:
    """Scrapes Wikipedia mapping tickers by Sector for S&P 500, Nasdaq 100, or Dow Jones."""
    try:
        urls = {
            "S&P 500": 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            "Nasdaq 100": 'https://en.wikipedia.org/wiki/Nasdaq-100',
            "Dow Jones 30": 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average',
            "Russell 1000 (Small/Mid Cap)": 'https://en.wikipedia.org/wiki/Russell_1000_Index',
            "FTSE 100 (UK)": 'https://en.wikipedia.org/wiki/FTSE_100_Index',
            "EURO STOXX 50 (Europe)": 'https://en.wikipedia.org/wiki/EURO_STOXX_50'
        }
        url = urls.get(index_name, urls["S&P 500"])
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        
        tables = pd.read_html(io.StringIO(response.text))
        df = None
        ticker_col = None
        for t in tables:
            for col in ['Symbol', 'Ticker', 'EPIC']:
                if col in t.columns:
                    df = t
                    ticker_col = col
                    break
            if df is not None:
                break
                
        if df is None:
            return {"Error": []}
            
        sector_col = 'GICS Sector' if 'GICS Sector' in df.columns else None
        if not sector_col and 'Sector' in df.columns:
            sector_col = 'Sector'
        if not sector_col and 'Industry' in df.columns:
            sector_col = 'Industry'
            
        df[ticker_col] = df[ticker_col].astype(str).str.replace('.', '-', regex=False)
        
        # Fix yfinance parsing for London Stock Exchange
        if index_name == "FTSE 100 (UK)":
            df[ticker_col] = df[ticker_col].apply(lambda x: f"{x}.L" if not x.endswith(".L") else x)
        
        sectors_dict = {}
        if sector_col:
            for sector in df[sector_col].unique():
                if pd.isna(sector): continue
                tickers = df[df[sector_col] == sector][ticker_col].tolist()
                sectors_dict[sector] = tickers
        else:
            sectors_dict["All Sectors"] = df[ticker_col].tolist()
            
        return sectors_dict
    except Exception as e:
        print(f"Failed to scrape index {index_name}: {e}")
        return {"Fallback": []}

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
