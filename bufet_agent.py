import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

from data_loader import load_watchlist
from fundamentals import analyze_fundamentals

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Default watch list of 10 stocks across different sectors
DEFAULT_WATCHLIST = ["AAPL", "MSFT", "GOOG", "KO", "BAC", "AXP", "JNJ", "TSLA", "NVDA", "WMT"]

def main():
    print("Starting Bufet Agent...")
    print(f"Loading data for watchlist: {', '.join(DEFAULT_WATCHLIST)}")
    
    raw_data = load_watchlist(DEFAULT_WATCHLIST)
    
    print("Performing fundamental analysis...")
    analyzed_data = []
    for stock in raw_data:
        try:
            analysis = analyze_fundamentals(stock)
            
            # Extract minimal context for LLM to avoid token limits
            minimal_record = {
                "Ticker": analysis["ticker"],
                "Buffett_Rules": analysis["buffett_analysis"],
                "Lynch_Rules": analysis["lynch_analysis"]
            }
            analyzed_data.append(minimal_record)
        except Exception as e:
            print(f"Error analyzing {stock.get('ticker')}: {e}")
            
    print("Generating Buy Rate Summary with Gemini...")
    
    prompt = f"""
You are the "Bufet Agent", an AI financial analyst channeling the combined wisdom and investment strategies of Warren Buffett and Peter Lynch.

I will provide you with fundamental analysis data for a watchlist of stocks. We have programmatically evaluated them against key Buffett and Lynch rules of thumb (e.g., ROE, Debt to Equity, PEG Ratio, P/E).

Data:
{json.dumps(analyzed_data, indent=2)}

Your Core Instructions:
1. Review the provided programmatic rule checks.
2. Select the Top 5 best stocks for mid-to-long term investment based *strictly* on standard Buffett (value, moat, strong financials) and Lynch (growth at a reasonable price, low PEG) principles.
3. Provide a unified "Buy Rate Summary" containing your Top 5 picks.
4. For each pick, write a brief justification detailing which principles it satisfies and why it makes a good long-term hold based on the data. 
5. Conclude with a brief overall market sentiment or general advice based on the provided batch of stocks.

Format the output clearly using Markdown headers and bullet points.
"""
    
    response = model.generate_content(prompt)
    
    print("\n" + "="*50)
    print("BUFET AGENT ANALYSIS REPORT")
    print("="*50 + "\n")
    print(response.text)

if __name__ == "__main__":
    main()
