#!/usr/bin/env python3
"""
Simple API test to isolate the LLM issue
"""
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dreamteller-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_simple_dream():
    async with aiohttp.ClientSession() as session:
        dream_data = {
            "dream_text": "I was flying",
            "format_type": "video",
            "include_audio": True
        }
        
        print("Testing simple dream generation...")
        
        try:
            async with session.post(f"{API_BASE}/generate-dream", json=dream_data) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success! Generated story length: {len(data.get('generated_story', ''))}")
                    print(f"Story preview: {data.get('generated_story', '')[:100]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_dream())
    exit(0 if success else 1)