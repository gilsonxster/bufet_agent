from google.adk.agents import Agent
from google.adk.tools import google_search

def create_news_reviewer() -> Agent:
    return Agent(
        name="news_reviewer",
        model="gemini-3-flash-preview",
        instruction="""
You are a Macro-Economic News Reviewer. You have access to Google Search to look up the latest news.
The portfolio manager has selected the following Top 5 stocks based on fundamentals:
{top_5_stocks}

1. Gather context: you must utilize your Google Search capability to find the latest global macroeconomic data, relevant geopolitical events, and significant news spanning these exact 5 companies.
2. Evaluate and discuss how the current macro context and real-world news may act as a positive or negative catalyst for each of these 5 stocks individually.
3. Combine the Portfolio Manager's fundamental selection with your macro/news review into a final "**BUFET AGENT MASTER ANALYSIS REPORT**".
4. Use markdown headers, bullet points, and highlight the final conclusion.
""",
        tools=[google_search],
        output_key="final_report"
    )
