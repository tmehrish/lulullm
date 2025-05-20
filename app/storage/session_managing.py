from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import Checkpoint
from pymongo import MongoClient
from beanie import init_beanie
from models import SessionMetadata, UserSession  # Your Pydantic models
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MongoDB connection
async def init_database():
    client = MongoClient(os.getenv("MONGO_URI"))
    await init_beanie(
        database=client.lulullm,
        document_models=[UserSession]
    )

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.lock = asyncio.Lock()
    
    async def get_metadata(self, user_id: str) -> SessionMetadata:
        async with self.lock:
            if user_id not in self.active_sessions:
                # Try to load existing metadata
                session = await UserSession.find_one(UserSession.user_id == user_id)
                if session:
                    self.active_sessions[user_id] = session.metadata
                else:
                    self.active_sessions[user_id] = SessionMetadata(
                        user_id=user_id,
                        session_id=str(datetime.now().timestamp())
                    )
            return self.active_sessions[user_id]

