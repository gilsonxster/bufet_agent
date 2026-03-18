import yfinance as yf
import pandas as pd

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
