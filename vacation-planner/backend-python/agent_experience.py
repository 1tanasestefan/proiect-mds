import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
# from pydantic_ai.models.openai import OpenAIModel (No longer needed with string identifier)
from duckduckgo_search import DDGS
from models import UserInput, AgentOneOutput, Activity, DailyItinerary
from loguru import logger

load_dotenv()

# The Agent will automatically use the GROQ_API_KEY from environment 
# when using the 'groq:' prefix.
experience_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    output_type=AgentOneOutput,
    system_prompt=(
        "You are the 'Experience Guide', a world-class Luxury Travel Concierge. "
        "Your mission is to provide an authentic, high-end itinerary for the specified destination. "
        "CRITICAL RULE: Never use placeholder text like 'Visit a local museum' or 'Have dinner at a nice restaurant'. "
        "Instead, you MUST use the `search_web` tool to find EXACT names of venues, restaurants, and tours that exist TODAY. "
        "Each activity must include: "
        "- A specific, real-world name (e.g., 'Grotto Bar' instead of 'A cocktail bar'). "
        "- A realistic description based on actual reviews found via search. "
        "- Accurate time-of-day slots. "
        "Return the itinerary in a strictly structured format with NO conversational filler. "
        "If you cannot find a specific detail, search again or use your extensive latent knowledge of the area to provide a name that is ICONIC to that location."
    ),
)

@experience_agent.tool
async def search_web(ctx: RunContext[UserInput], query: str) -> str:
    """
    Search the web for real-time information about activities, places, and local vibes.
    This tool uses DuckDuckGo Search.
    """
    try:
        logger.info(f"Searching DuckDuckGo for: {query}")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            
        if not results:
            return "No results found for this query."
            
        context_str = ""
        for r in results:
            context_str += f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nURL: {r.get('href')}\n\n"
        return context_str
        
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return "Search tool is temporarily unavailable. Proceed with general knowledge if possible or return a minimal valid itinerary."

async def generate_experience_itinerary(user_input: UserInput) -> AgentOneOutput:
    """
    Executes the Groq-powered agent to generate a curated itinerary.
    """
    try:
        logger.info(f"Generating Groq itinerary for: {user_input.destination}")
        result = await experience_agent.run(
            f"Mandatory: Use the `search_web` tool to find REAL, specifically named venues and experiences in {user_input.destination} "
            f"that fit a '{user_input.lifestyle}' lifestyle with a '{user_input.budget}' budget and '{user_input.vacationType}' vibe. "
            f"The trip is for {user_input.travelers} people. Ensure every activity name is a specific, existing location.",
            deps=user_input
        )
        return result.output
    except Exception as e:
        logger.error(f"Error during agent execution: {e}")
        raise e
