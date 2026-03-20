import json
from google.adk.agents import Agent
from google.adk.tools import ToolContext

from data_loader import load_watchlist
from fundamentals import analyze_fundamentals

DEFAULT_WATCHLIST = ["AAPL", "MSFT", "GOOG", "KO", "BAC", "AXP", "JNJ", "TSLA", "NVDA", "WMT"]

async def get_watchlist_fundamentals(tool_context: ToolContext) -> dict:
    """Collects programmatic fundamental analysis for the default watchlist."""
    target_watchlist = tool_context.state.get("screened_tickers")
    if not target_watchlist:
        print("No screened tickers found in state. Falling back to default.")
        target_watchlist = DEFAULT_WATCHLIST
        
    print(f"Loading deep fundamental data for {len(target_watchlist)} candidates...")
    raw_data = load_watchlist(target_watchlist)
    
    analyzed_data = []
    print("Performing fundamental analysis...")
    for stock in raw_data:
        try:
            analysis = analyze_fundamentals(stock)
            minimal_record = {
                "Ticker": analysis.get("ticker", "Unknown"),
                "Buffett_Rules": analysis.get("buffett_analysis", {}),
                "Lynch_Rules": analysis.get("lynch_analysis", {}),
                "Legendary_Rules": analysis.get("legendary_analysis", {})
            }
            analyzed_data.append(minimal_record)
        except Exception as e:
             print(f"Error analyzing {stock.get('ticker', 'Unknown')}: {e}")

    # Store in session state for downstream agents
    tool_context.state["research_data"] = json.dumps(analyzed_data, indent=2)
    
    return {"status": "success", "analyzed_data_count": len(analyzed_data), "data": analyzed_data}

def create_researcher() -> Agent:
    return Agent(
        name="researcher_agent",
        model="gemini-2.5-flash",
        instruction="You are a data collection researcher. Call the `get_watchlist_fundamentals` tool exactly once to collect programmatic fundamental analysis for a stock watchlist, then output 'Data collected successfully'.",
        description="Responsible for pulling the raw programmatic data on the watchlist.",
        tools=[get_watchlist_fundamentals],
        output_key="research_done"
    )
