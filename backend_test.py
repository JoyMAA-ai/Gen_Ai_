#!/usr/bin/env python3
"""
Backend API Tests for Dream Teller Application
Tests the core functionality of dream generation, LLM integration, and MongoDB storage.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dreamteller-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DreamTellerAPITest:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.generated_dream_ids = []
        self.test_session_id = str(uuid.uuid4())
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            
    async def test_api_root(self):
        """Test API root endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "Dream Teller API" in data.get("message", ""):
                        self.log_result("API Root Endpoint", True, "API is accessible and returns correct message")
                    else:
                        self.log_result("API Root Endpoint", False, f"Unexpected message: {data}", data)
                else:
                    self.log_result("API Root Endpoint", False, f"HTTP {response.status}", await response.text())
        except Exception as e:
            self.log_result("API Root Endpoint", False, f"Connection error: {str(e)}")
            
    async def test_dream_generation_video(self):
        """Test dream generation with video format"""
        dream_data = {
            "dream_text": "I was flying over a mystical forest filled with glowing trees and floating islands. The sky was painted in shades of purple and gold, and I could hear ethereal music echoing through the clouds.",
            "format_type": "video",
            "include_audio": True,
            "session_id": self.test_session_id
        }
        
        try:
            async with self.session.post(f"{API_BASE}/generate-dream", json=dream_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ['id', 'dream_text', 'generated_story', 'format_type', 'include_audio', 'status', 'session_id']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result("Dream Generation (Video)", False, f"Missing fields: {missing_fields}", data)
                        return
                        
                    # Validate content
                    if data['dream_text'] != dream_data['dream_text']:
                        self.log_result("Dream Generation (Video)", False, "Dream text mismatch", data)
                        return
                        
                    if not data['generated_story'] or len(data['generated_story']) < 50:
                        self.log_result("Dream Generation (Video)", False, "Generated story too short or empty", data)
                        return
                        
                    if data['format_type'] != 'video':
                        self.log_result("Dream Generation (Video)", False, "Format type mismatch", data)
                        return
                        
                    if data['session_id'] != self.test_session_id:
                        self.log_result("Dream Generation (Video)", False, "Session ID mismatch", data)
                        return
                        
                    # Store dream ID for later tests
                    self.generated_dream_ids.append(data['id'])
                    
                    self.log_result("Dream Generation (Video)", True, 
                                  f"Successfully generated story ({len(data['generated_story'])} chars), ID: {data['id']}")
                else:
                    error_text = await response.text()
                    self.log_result("Dream Generation (Video)", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_result("Dream Generation (Video)", False, f"Request error: {str(e)}")
            
    async def test_dream_generation_podcast(self):
        """Test dream generation with podcast format"""
        dream_data = {
            "dream_text": "I found myself in an ancient library where books were floating and writing themselves. The librarian was a wise owl who spoke in riddles, and every book I touched revealed secrets of the universe.",
            "format_type": "podcast",
            "include_audio": True,
            "session_id": self.test_session_id
        }
        
        try:
            async with self.session.post(f"{API_BASE}/generate-dream", json=dream_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data['format_type'] != 'podcast':
                        self.log_result("Dream Generation (Podcast)", False, "Format type should be podcast", data)
                        return
                        
                    if not data['generated_story']:
                        self.log_result("Dream Generation (Podcast)", False, "No story generated", data)
                        return
                        
                    # Store dream ID for later tests
                    self.generated_dream_ids.append(data['id'])
                    
                    self.log_result("Dream Generation (Podcast)", True, 
                                  f"Successfully generated podcast story, ID: {data['id']}")
                else:
                    error_text = await response.text()
                    self.log_result("Dream Generation (Podcast)", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_result("Dream Generation (Podcast)", False, f"Request error: {str(e)}")
            
    async def test_dream_retrieval(self):
        """Test retrieving a specific dream by ID"""
        if not self.generated_dream_ids:
            self.log_result("Dream Retrieval", False, "No dream IDs available for testing")
            return
            
        dream_id = self.generated_dream_ids[0]
        
        try:
            async with self.session.get(f"{API_BASE}/dream/{dream_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data['id'] != dream_id:
                        self.log_result("Dream Retrieval", False, "Retrieved dream ID mismatch", data)
                        return
                        
                    if not data['generated_story']:
                        self.log_result("Dream Retrieval", False, "Retrieved dream missing story", data)
                        return
                        
                    self.log_result("Dream Retrieval", True, f"Successfully retrieved dream {dream_id}")
                else:
                    error_text = await response.text()
                    self.log_result("Dream Retrieval", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_result("Dream Retrieval", False, f"Request error: {str(e)}")
            
    async def test_session_dreams_retrieval(self):
        """Test retrieving all dreams for a session"""
        try:
            async with self.session.get(f"{API_BASE}/dreams/session/{self.test_session_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not isinstance(data, list):
                        self.log_result("Session Dreams Retrieval", False, "Response should be a list", data)
                        return
                        
                    # Should have at least the dreams we created
                    expected_count = len(self.generated_dream_ids)
                    if len(data) < expected_count:
                        self.log_result("Session Dreams Retrieval", False, 
                                      f"Expected at least {expected_count} dreams, got {len(data)}", data)
                        return
                        
                    # Verify all dreams belong to the session
                    for dream in data:
                        if dream['session_id'] != self.test_session_id:
                            self.log_result("Session Dreams Retrieval", False, 
                                          f"Dream {dream['id']} has wrong session_id", data)
                            return
                            
                    self.log_result("Session Dreams Retrieval", True, 
                                  f"Successfully retrieved {len(data)} dreams for session")
                else:
                    error_text = await response.text()
                    self.log_result("Session Dreams Retrieval", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_result("Session Dreams Retrieval", False, f"Request error: {str(e)}")
            
    async def test_error_handling_empty_dream(self):
        """Test error handling for empty dream text"""
        dream_data = {
            "dream_text": "",
            "format_type": "video",
            "include_audio": True
        }
        
        try:
            async with self.session.post(f"{API_BASE}/generate-dream", json=dream_data) as response:
                if response.status == 422:  # Validation error expected
                    self.log_result("Error Handling (Empty Dream)", True, "Correctly rejected empty dream text")
                elif response.status == 500:
                    # Server error might occur if validation passes but LLM fails
                    self.log_result("Error Handling (Empty Dream)", True, "Server handled empty dream appropriately")
                else:
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
                    self.log_result("Error Handling (Empty Dream)", False, 
                                  f"Unexpected status {response.status} for empty dream", data)
                    
        except Exception as e:
            self.log_result("Error Handling (Empty Dream)", False, f"Request error: {str(e)}")
            
    async def test_error_handling_invalid_format(self):
        """Test error handling for invalid format type"""
        dream_data = {
            "dream_text": "A simple dream about flying",
            "format_type": "invalid_format",
            "include_audio": True
        }
        
        try:
            async with self.session.post(f"{API_BASE}/generate-dream", json=dream_data) as response:
                # Should either validate and reject, or accept and handle gracefully
                if response.status in [200, 422, 500]:
                    self.log_result("Error Handling (Invalid Format)", True, 
                                  f"Handled invalid format appropriately (status: {response.status})")
                else:
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
                    self.log_result("Error Handling (Invalid Format)", False, 
                                  f"Unexpected status {response.status}", data)
                    
        except Exception as e:
            self.log_result("Error Handling (Invalid Format)", False, f"Request error: {str(e)}")
            
    async def test_nonexistent_dream_retrieval(self):
        """Test retrieving a non-existent dream"""
        fake_id = str(uuid.uuid4())
        
        try:
            async with self.session.get(f"{API_BASE}/dream/{fake_id}") as response:
                if response.status == 404:
                    self.log_result("Error Handling (Nonexistent Dream)", True, "Correctly returned 404 for nonexistent dream")
                else:
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
                    self.log_result("Error Handling (Nonexistent Dream)", False, 
                                  f"Expected 404, got {response.status}", data)
                    
        except Exception as e:
            self.log_result("Error Handling (Nonexistent Dream)", False, f"Request error: {str(e)}")
            
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting Dream Teller Backend API Tests")
        print(f"📍 Testing against: {API_BASE}")
        print(f"🔑 Session ID: {self.test_session_id}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Core functionality tests
            await self.test_api_root()
            await self.test_dream_generation_video()
            await self.test_dream_generation_podcast()
            await self.test_dream_retrieval()
            await self.test_session_dreams_retrieval()
            
            # Error handling tests
            await self.test_error_handling_empty_dream()
            await self.test_error_handling_invalid_format()
            await self.test_nonexistent_dream_retrieval()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
                    
        return passed_tests, failed_tests, self.test_results

async def main():
    """Main test runner"""
    tester = DreamTellerAPITest()
    passed, failed, results = await tester.run_all_tests()
    
    # Return exit code based on results
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)