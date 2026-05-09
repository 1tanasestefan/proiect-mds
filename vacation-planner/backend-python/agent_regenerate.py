import os
import json
import re
import asyncio
from pydantic_ai import Agent
from models import Activity
from loguru import logger
from fastapi import HTTPException
from agent_experience import fetch_image_for_activity

regenerate_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    output_type=str,
    retries=3,
    system_prompt=(
        "You are the 'Experience Guide', tasked to replace exactly ONE rejected activity in a user's itinerary. "
        "The users have democratically voted to remove this activity, so you must provide an alternative that fits seamlessly "
        "into the existing day and matches the specified overall vibe. "

        "CRITICAL OUTPUT RULES: "
        "1. Your ENTIRE response must be a single valid JSON object representing exactly ONE new activity. "
        "2. The JSON object MUST have exactly these keys: "
        "   'title' (str), 'description' (str), 'time' (str), 'cost' (str), 'location' (str), "
        "   'image_url' (empty string ''), and 'type' (str from the Allowed Types). "
        "3. Allowed Types: 'experience', 'dining', 'tour', 'cruise', 'cookingclass', 'festival', 'adventure', 'culture', 'relaxation', 'shopping', 'nightlife', 'transport'. "
        "4. Do NOT output function calls, XML tags, or <function=...> syntax. "
        "5. Begin your response with '{' immediately."
    ),
)


async def regenerate_single_activity(vibe_summary: str, day_context: str, destination: str, old_activity_json: str) -> Activity:
    """Invokes the regenerate agent for a single activity replacement and fetches a new image."""
    try:
        logger.info(f"Regenerating activity replacement for: {destination}")

        prompt = (
            f"Destination: {destination}\n"
            f"Overall Vibe: {vibe_summary}\n"
            f"Context of the Rest of the Day (do not duplicate these): {day_context}\n"
            f"\nREJECTED ACTIVITY TO REPLACE:\n{old_activity_json}\n\n"
            "Provide a fresh, entirely different replacement activity."
        )

        result = await asyncio.wait_for(
            regenerate_agent.run(prompt),
            timeout=60
        )

        raw_text = str(getattr(result, 'output', result))

        def extract_json(text: str):
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            cleaned = re.sub(r"```(json)?", "", text).strip()
            # aggressive strip
            cleaned = re.sub(r"<function.*?>.*?</function>", "", cleaned, flags=re.DOTALL).strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return None

        # Clean JSON
        data = extract_json(raw_text)
        if not data:
            raise ValueError(f"No valid JSON found in regenerate agent output: {raw_text[:200]}")

        parsed_act = Activity(**data)

        # Append new Image using our fast sniper!
        new_img_url = await fetch_image_for_activity(parsed_act.title, destination)
        
        return parsed_act.model_copy(update={"image_url": new_img_url})

    except Exception as e:
        logger.error(f"Activity regeneration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Regeneration error: {str(e)}")
