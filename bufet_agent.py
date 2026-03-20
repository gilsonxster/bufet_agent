import os
import asyncio
from dotenv import load_dotenv

from google.adk.agents import SequentialAgent, ParallelAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import agents from skills module
from skills.screener import create_screener
from skills.researcher import create_researcher
from skills.analysts import create_buffett_agent, create_lynch_agent, create_graham_agent, create_legendary_agent
from skills.portfolio_manager import create_portfolio_manager
from skills.news_reviewer import create_news_reviewer

# Load environment variables
load_dotenv()

# Establish the multi-agent pipeline
pipeline = SequentialAgent(
    name="bufet_master_pipeline",
    sub_agents=[
        create_screener(),
        create_researcher(),
        ParallelAgent(
            name="analysts_panel",
            sub_agents=[create_buffett_agent(), create_lynch_agent(), create_graham_agent(), create_legendary_agent()]
        ),
        create_portfolio_manager(),
        create_news_reviewer()
    ]
)

async def run_bufet_pipeline(custom_watchlist: list, user_api_key: str = "") -> str:
    # Resolve the API Key efficiently
    system_key = os.getenv("GEMINI_API_KEY")
    active_key = user_api_key if user_api_key.strip() else system_key
    
    if not active_key:
        return "Error: No Gemini API Key was provided. Please enter one in the sidebar."
        
    # Force utilizing the chosen API key directly at runtime for ADK 
    os.environ["GOOGLE_API_KEY"] = active_key
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

    print(f"Starting Bufet Pipeline via Web UI for {len(custom_watchlist)} tickers...")
    
    my_session_id = os.urandom(8).hex()
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="bufet_app",
        user_id="user_1",
        session_id=my_session_id
    )
    
    # Initialize state variables
    session.state["initial_watchlist"] = custom_watchlist
    session.state["screened_tickers"] = []
    session.state["research_data"] = "Data not fetched."
    session.state["buffett_analysis"] = "Waiting on pipeline..."
    session.state["lynch_analysis"] = "Waiting on pipeline..."
    session.state["graham_analysis"] = "Waiting on pipeline..."
    session.state["top_5_stocks"] = "Waiting on pipeline..."
    
    runner = Runner(
        agent=pipeline,
        app_name="bufet_app",
        session_service=session_service
    )
    
    initial_message = types.Content(role="user", parts=[types.Part.from_text(text=f"The selected initial watchlist is: {custom_watchlist}. Please run the screener on my initial watchlist, fetch fundamentals for passing stocks, run the parallel analysis panel, select the Top 5 consensus picks, and give me the master report with your news review.")])
    
    final_output = ""
    async for event in runner.run_async(
        user_id="user_1",
        session_id=my_session_id,
        new_message=initial_message
    ):
        if event.is_final_response():
            if event.content and hasattr(event.content, "parts") and event.content.parts:
                final_output = event.content.parts[0].text
                
    return final_output

async def main_async():
    # Only for CLI fallback
    print("Running CLI fallback...")
    res = await run_bufet_pipeline(["AAPL", "PLTR", "MSFT"])
    print(res)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
