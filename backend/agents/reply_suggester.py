# GET /ai/suggest-replies?chat_id=...
#         ↓
# Fetch last 20 messages from DB
#         ↓
# Fetch contact's profile
#         ↓
# LangGraph agent analyzes conversation
#         ↓ 
# Returns 3 suggestions + conversation health

#The agent needs to:
# - Take last 20 messages + contact profile as input
# - Analyze the conversation tone and context
# - Detect if conversation is dying (last message > 24 hours ago)
# - Generate 3 reply suggestions with different tones

import os
import json
from datetime import datetime, timezone
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(
    model="qwen/qwen3.6-27b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.8,
)

async def suggest_replies(messages: list, contact_name: str) -> dict:
    """Will use LangGraph + GROQ to analyze the conversation and suggest replies"""
    
    # Format Conversation according to the sender of a particular message
    convo_text = ""
    for msg in messages:
        sender = "You" if msg.sender_id != contact_name else contact_name
        convo_text += f"{sender}: {msg.content}\n"
    
    #detect conversation health ("healthy"/"dying"/"needs_revival")
    
    health = "healthy"
    revival_message = None

    if messages:
        last_msg = messages[-1]
        hours_since = (datetime.now(timezone.utc) - last_msg.created_at).total_seconds() / 3600
        if hours_since > 48:
            health = "dying"
            revival_message = f"You haven't spoken in {int(hours_since)} hours. Time to reach out!"
        elif hours_since > 24:
            health = "needs_revival"
            revival_message = "Conversation has slowed down. A quick message could revive it!"

    # Call LLM for suggestions 
    prompt = f"""
You are a helpful chat assistant. Analyze this conversation and suggest 3 different replies.

Contact name: {contact_name}

Conversation:
{convo_text}

Generate exactly 3 reply suggestions with different tones:
1. Casual and fridendly
2. Enthusiastic
3. Thoughtful

Respond in this exact JSON format:
{{"suggestions": ["reply1", "reply2", "reply3"]}}

Only return the JSON, nothing else.
"""
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    # Parse and Return in json
    
    try:
        content = response.content.strip()

        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)
        suggestions = parsed.get("suggestions", [])
    except:
        suggestions = ["That's interesting!", "Tell me more!","Sounds great!"]

    return {
        "suggestions": suggestions,
        "conversation_health": health,
        "revival_message": revival_message,
    }

