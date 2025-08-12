#!/usr/bin/env python3
"""
Test LLM from backend directory context
"""
import asyncio
import os
import sys
sys.path.append('/app/backend')

from dotenv import load_dotenv
from pathlib import Path

# Load env the same way as server.py
ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

from emergentintegrations.llm.chat import LlmChat, UserMessage

async def test_backend_context():
    print("Testing from backend context...")
    
    # Get API key the same way as server.py
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    print(f"API Key: {api_key[:10] if api_key else 'None'}...")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    try:
        # Use same system message as server.py
        system_message = """You are a creative storyteller who transforms dreams into vivid, cinematic narratives. 
        Your task is to take a dream description and convert it into a well-structured story with:
        1. Clear scene descriptions suitable for video generation
        2. Engaging narrative flow
        3. Rich visual details
        4. Emotional depth
        5. A coherent beginning, middle, and end
        
        Keep the story between 200-500 words and make it suitable for video/audio generation."""
        
        chat = LlmChat(
            api_key=api_key,
            session_id="test-session-backend",
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(
            text="Transform this dream into a compelling story: I was flying over a forest"
        )
        
        print("Sending message to LLM...")
        story_response = await chat.send_message(user_message)
        
        print(f"✅ Success! Story length: {len(story_response)}")
        print(f"Story preview: {story_response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend_context())
    exit(0 if success else 1)