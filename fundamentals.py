def assess_buffett_rules(stock_data: dict) -> dict:
    info = stock_data.get("info", {})
    
    # 1. Consistent earnings growth and high margins. 
    profit_margin = info.get("profitMargins", 0)
    operating_margin = info.get("operatingMargins", 0)
    
    # 2. High Return on Equity (ROE consistently > 15%).
    roe = info.get("returnOnEquity", 0)
    
    # 3. Low Debt-to-Equity ratio.
    # Note: yfinance often returns it as a percentage e.g., 50 for 0.5. We look for < 100.
    debt_to_equity = info.get("debtToEquity", 0)
    
    # 4. Strong Current Ratio (> 1.5)
    current_ratio = info.get("currentRatio", 0)
    
    results = {
        "roe_pass": roe is not None and roe > 0.15,
        "debt_to_equity_pass": debt_to_equity is not None and debt_to_equity < 100,
        "margins_pass": profit_margin is not None and profit_margin > 0.1,
        "current_ratio_pass": current_ratio is not None and current_ratio > 1.5,
        "summary_metrics": {
            "ROE": roe,
            "Debt_To_Equity": debt_to_equity,
            "Profit_Margin": profit_margin,
            "Current_Ratio": current_ratio
        }
    }
    return results

def assess_lynch_rules(stock_data: dict) -> dict:
    info = stock_data.get("info", {})
    
    # 1. PEG Ratio (Price/Earnings-to-Growth): Ideally <= 1
    peg_ratio = info.get("pegRatio", 0)
    
    # 2. P/E Ratio reasonable compared to growth
    pe_ratio = info.get("trailingPE", 0)
    forward_pe = info.get("forwardPE", 0)
    
    # 3. Strong earnings growth
    earnings_growth = info.get("earningsGrowth", 0)
    
    results = {
        "peg_pass": peg_ratio is not None and 0 < peg_ratio <= 1.2, # slightly more permissive
        "pe_reasonable": pe_ratio is not None and pe_ratio < 25,
        "growth_pass": earnings_growth is not None and earnings_growth > 0.10,
        "summary_metrics": {
            "PEG_Ratio": peg_ratio,
            "Trailing_PE": pe_ratio,
            "Forward_PE": forward_pe,
            "Earnings_Growth": earnings_growth
        }
    }
    return results

def analyze_fundamentals(stock_data: dict) -> dict:
    """Wrapper to run both analyses."""
    return {
        "ticker": stock_data.get("ticker"),
        "buffett_analysis": assess_buffett_rules(stock_data),
        "lynch_analysis": assess_lynch_rules(stock_data)
    }

if __name__ == "__main__":
    # A dummy test to make sure syntax is okay
    dummy_data = {
        "ticker": "AAPL",
        "info": {
            "pegRatio": 0.8,
            "returnOnEquity": 0.35,
            "debtToEquity": 120,
            "currentRatio": 1.1
        }
    }
    res = analyze_fundamentals(dummy_data)
    print(res)
