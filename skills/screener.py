import json
from google.adk.agents import Agent
from google.adk.tools import ToolContext

from data_loader import buffett_lynch_screener

async def run_screener(tickers: list[str], tool_context: ToolContext) -> dict:
    """Runs a programmatic screener over the provided list of tickers."""
    print(f"Running fundamental screener on {len(tickers)} tickers...")
    
    if not tickers:
        return {"status": "error", "message": "No tickers provided in tool argument"}
        
    screened_data = buffett_lynch_screener(tickers)
    
    screened_tickers = [item["ticker"] for item in screened_data]
    
    # Save the output back to state for the researcher
    tool_context.state["screened_tickers"] = screened_tickers
    
    print(f"Screener finished. Found {len(screened_tickers)} passing candidates.")
    return {"status": "success", "passing_count": len(screened_tickers), "candidates": screened_data}

def create_screener() -> Agent:
    return Agent(
        name="screener_agent",
        model="gemini-2.5-flash",
        instruction="You are the Primary Fundamental Screener. You will be provided with an initial watchlist by the user. Call the `run_screener` tool and pass the ENTIRE list of tickers into the `tickers` argument to programmatically filter them. Output a summary of the stocks that passed.",
        tools=[run_screener],
        output_key="screener_output"
    )
