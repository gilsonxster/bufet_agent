import pandas as pd

def assess_buffett_rules(stock_data: dict) -> dict:
    info = stock_data.get("info", {})
    profit_margin = info.get("profitMargins", 0)
    operating_margin = info.get("operatingMargins", 0)
    roe = info.get("returnOnEquity", 0)
    debt_to_equity = info.get("debtToEquity", 0)
    current_ratio = info.get("currentRatio", 0)
    
    return {
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

def assess_lynch_rules(stock_data: dict) -> dict:
    info = stock_data.get("info", {})
    peg_ratio = info.get("pegRatio", 0)
    pe_ratio = info.get("trailingPE", 0)
    forward_pe = info.get("forwardPE", 0)
    earnings_growth = info.get("earningsGrowth", 0)
    
    return {
        "peg_pass": peg_ratio is not None and 0 < peg_ratio <= 1.2,
        "pe_reasonable": pe_ratio is not None and pe_ratio < 25,
        "growth_pass": earnings_growth is not None and earnings_growth > 0.10,
        "summary_metrics": {
            "PEG_Ratio": peg_ratio,
            "Trailing_PE": pe_ratio,
            "Forward_PE": forward_pe,
            "Earnings_Growth": earnings_growth
        }
    }

def assess_legendary_rules(stock_data: dict) -> dict:
    info = stock_data.get("info", {})
    financials = stock_data.get("financials")
    balance_sheet = stock_data.get("balance_sheet")
    cashflow = stock_data.get("cashflow")

    # Helper to safely extract from DataFrame
    def get_df_value(df, row_name, default=0):
        if df is not None and not df.empty and row_name in df.index:
            try:
                val = df.loc[row_name].iloc[0]
                return float(val) if not pd.isna(val) else default
            except:
                pass
        return default

    net_income = info.get("netIncomeToCommon") or get_df_value(financials, "Net Income", 0)
    d_and_a = get_df_value(cashflow, "Depreciation And Amortization", 0)
    capex = abs(get_df_value(cashflow, "Capital Expenditure", 0))
    lt_debt = info.get("totalDebt") or get_df_value(balance_sheet, "Long Term Debt", 0)
    eps_growth = info.get("earningsGrowth", 0)
    div_yield = info.get("dividendYield") or 0
    pe_ratio = info.get("trailingPE") or info.get("forwardPE", 0)
    rev_growth = info.get("revenueGrowth", 0)
    
    # Inventory growth
    inv_t0 = get_df_value(balance_sheet, "Inventory", 0)
    inv_t1 = 0
    if balance_sheet is not None and not balance_sheet.empty and "Inventory" in balance_sheet.index and len(balance_sheet.columns) > 1:
        val = balance_sheet.loc["Inventory"].iloc[1]
        inv_t1 = float(val) if not pd.isna(val) else 0

    inv_growth = (inv_t0 - inv_t1) / inv_t1 if inv_t1 else 0
    
    # Approximation for ROIC
    roic = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0

    ticker_data = {
        "net_income": net_income,
        "d_and_a": d_and_a,
        "capex": capex,
        "lt_debt": lt_debt,
        "eps_growth": eps_growth,
        "div_yield": div_yield,
        "pe_ratio": pe_ratio,
        "rev_growth": rev_growth,
        "inv_growth": inv_growth,
        "roic": roic
    }

    score = 0
    
    # 1. BUFFETT: Owner Earnings
    owner_earnings = ticker_data['net_income'] + ticker_data['d_and_a'] - ticker_data['capex']
    if owner_earnings > (ticker_data['net_income'] * 0.9): score += 20
    
    # 2. BUFFETT: 3-Year Debt Rule
    if ticker_data['net_income'] > 0 and (ticker_data['lt_debt'] / ticker_data['net_income']) < 3: 
        score += 20
    elif ticker_data['lt_debt'] == 0:
        score += 20
        
    # 3. LYNCH: PEGY Ratio
    denom = (ticker_data['eps_growth'] + ticker_data['div_yield'])
    if denom > 0:
        pegy = ticker_data['pe_ratio'] / denom
        if pegy < 1.0: score += 20
    
    # 4. LYNCH: Inventory Check
    if ticker_data['inv_growth'] <= ticker_data['rev_growth']: score += 20
    
    # 5. MOAT: Consistent ROIC
    if ticker_data['roic'] > 15: score += 20

    return {
        "extracted_data": ticker_data,
        "final_score": score,
        "verdict": "Strong Buy" if score >= 80 else "Hold/Pass"
    }

def analyze_fundamentals(stock_data: dict) -> dict:
    return {
        "ticker": stock_data.get("ticker"),
        "buffett_analysis": assess_buffett_rules(stock_data),
        "lynch_analysis": assess_lynch_rules(stock_data),
        "legendary_analysis": assess_legendary_rules(stock_data)
    }
