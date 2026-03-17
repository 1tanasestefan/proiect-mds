import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from duckduckgo_search import DDGS
from models import UserInput, AgentOneOutput, Activity, DailyItinerary
from loguru import logger

load_dotenv()

# Initialize Gemini Model
# PydanticAI will automatically pick up GEMINI_API_KEY from the environment
model = GeminiModel('gemini-1.5-flash')

experience_agent = Agent(
    model,
    output_type=AgentOneOutput,
    system_prompt=(
        "You are the 'Experience Guide', a Senior AI Travel Architect. "
        "Your goal is to create a curated experience itinerary based on user preferences. "
        "You must find real, highly-rated activities that match the user's vibe and budget. "
        "Use the provided search tool to find current information about the destination. "
        "Return the itinerary in a strictly structured format with NO conversational filler."
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
    Executes the Gemini-powered agent to generate a curated itinerary.
    """
    try:
        logger.info(f"Generating Gemini itinerary for: {user_input.destination}")
        result = await experience_agent.run(
            f"Plan a trip to {user_input.destination} for {user_input.travelers} travelers. "
            f"Vacation Type: {user_input.vacationType}, Lifestyle: {user_input.lifestyle}, Budget: {user_input.budget}.",
            deps=user_input
        )
        return result.data
    except Exception as e:
        logger.error(f"Error during agent execution: {e}")
        raise e
