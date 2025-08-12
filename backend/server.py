from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class DreamRequest(BaseModel):
    dream_text: str
    format_type: str = "video"  # "video" or "podcast"
    include_audio: bool = True
    session_id: Optional[str] = None

class DreamGeneration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dream_text: str
    generated_story: str
    format_type: str
    include_audio: bool
    status: str = "processing"  # "processing", "completed", "failed"
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Dream generation endpoint
@api_router.post("/generate-dream", response_model=DreamGeneration)
async def generate_dream_content(request: DreamRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize LLM chat for story generation
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="LLM API key not configured")
        
        # Create story generation prompt
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
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
        
        # Generate story from dream
        user_message = UserMessage(
            text=f"Transform this dream into a compelling story: {request.dream_text}"
        )
        
        story_response = await chat.send_message(user_message)
        generated_story = story_response
        
        # Create dream generation record
        dream_gen = DreamGeneration(
            dream_text=request.dream_text,
            generated_story=generated_story,
            format_type=request.format_type,
            include_audio=request.include_audio,
            session_id=session_id,
            status="story_generated"
        )
        
        # Save to database
        await db.dream_generations.insert_one(dream_gen.dict())
        
        # For now, simulate video/audio generation (placeholder)
        # In production, this would call actual video generation APIs
        if request.format_type == "video":
            dream_gen.video_url = f"https://example.com/video/{dream_gen.id}.mp4"
            if request.include_audio:
                dream_gen.audio_url = f"https://example.com/audio/{dream_gen.id}.mp3"
        else:  # podcast
            dream_gen.audio_url = f"https://example.com/podcast/{dream_gen.id}.mp3"
        
        dream_gen.status = "completed"
        
        # Update in database
        await db.dream_generations.update_one(
            {"id": dream_gen.id},
            {"$set": dream_gen.dict()}
        )
        
        return dream_gen
        
    except Exception as e:
        logging.error(f"Error generating dream content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dream content: {str(e)}")

# Get dream generation by ID
@api_router.get("/dream/{dream_id}", response_model=DreamGeneration)
async def get_dream_generation(dream_id: str):
    dream = await db.dream_generations.find_one({"id": dream_id})
    if not dream:
        raise HTTPException(status_code=404, detail="Dream generation not found")
    return DreamGeneration(**dream)

# Get all dreams for a session
@api_router.get("/dreams/session/{session_id}", response_model=List[DreamGeneration])
async def get_session_dreams(session_id: str):
    dreams = await db.dream_generations.find({"session_id": session_id}).to_list(100)
    return [DreamGeneration(**dream) for dream in dreams]

# Original endpoints
@api_router.get("/")
async def root():
    return {"message": "Dream Teller API - Transform your dreams into videos and podcasts"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()