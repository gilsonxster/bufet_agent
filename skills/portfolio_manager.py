from google.adk.agents import Agent

def create_portfolio_manager() -> Agent:
    return Agent(
        name="portfolio_manager",
        model="gemini-3-flash-preview",
        instruction="""
You are the Head Portfolio Manager. 
Review your analysts' conclusions exactly as they appear in the session state:
- Warren Buffett: {buffett_analysis}
- Peter Lynch: {lynch_analysis}
- Benjamin Graham: {graham_analysis}
- Legendary Committee: {legendary_analysis}

Based on overlapping consensus from their analyses, select exactly the Top 10 best stocks from the watchlist. 
List their ticker symbols prominently and explain the combined reasoning for selecting them over the others. 
Do NOT talk about news or macroeconomic events yet; restrict your analysis entirely to the synthesized fundamental consensus.
""",
        output_key="top_10_stocks"
    )
