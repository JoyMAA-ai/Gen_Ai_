#!/usr/bin/env python3
"""
Test non-LLM endpoints to verify other functionality
"""
import asyncio
import aiohttp
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dreamteller-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_non_llm_endpoints():
    async with aiohttp.ClientSession() as session:
        print("Testing non-LLM endpoints...")
        
        # Test API root
        try:
            async with session.get(f"{API_BASE}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API Root: {data.get('message', '')}")
                else:
                    print(f"❌ API Root failed: {response.status}")
        except Exception as e:
            print(f"❌ API Root error: {e}")
        
        # Test status endpoints
        try:
            status_data = {"client_name": "test_client"}
            async with session.post(f"{API_BASE}/status", json=status_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Status creation: ID {data.get('id', 'unknown')}")
                else:
                    print(f"❌ Status creation failed: {response.status}")
        except Exception as e:
            print(f"❌ Status creation error: {e}")
        
        # Test status retrieval
        try:
            async with session.get(f"{API_BASE}/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Status retrieval: {len(data)} records")
                else:
                    print(f"❌ Status retrieval failed: {response.status}")
        except Exception as e:
            print(f"❌ Status retrieval error: {e}")
        
        # Test session dreams (should return empty list)
        try:
            test_session = str(uuid.uuid4())
            async with session.get(f"{API_BASE}/dreams/session/{test_session}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Session dreams: {len(data)} dreams (expected 0)")
                else:
                    print(f"❌ Session dreams failed: {response.status}")
        except Exception as e:
            print(f"❌ Session dreams error: {e}")
        
        # Test nonexistent dream retrieval
        try:
            fake_id = str(uuid.uuid4())
            async with session.get(f"{API_BASE}/dream/{fake_id}") as response:
                if response.status == 404:
                    print(f"✅ Nonexistent dream: Correctly returned 404")
                else:
                    print(f"❌ Nonexistent dream: Expected 404, got {response.status}")
        except Exception as e:
            print(f"❌ Nonexistent dream error: {e}")

if __name__ == "__main__":
    asyncio.run(test_non_llm_endpoints())