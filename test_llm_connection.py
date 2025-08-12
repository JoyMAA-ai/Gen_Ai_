#!/usr/bin/env python3
"""
Test LLM connection directly
"""
import asyncio
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

async def test_llm_connection():
    load_dotenv('/app/backend/.env')
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    print(f"Testing LLM connection with API key: {api_key[:10]}...")
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id="test-session",
            system_message="You are a helpful assistant."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text="Hello, can you respond with just 'Connection successful'?")
        response = await chat.send_message(user_message)
        
        print(f"✅ LLM Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ LLM Connection Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm_connection())
    exit(0 if success else 1)