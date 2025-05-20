from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import Checkpoint
from pymongo import MongoClient
from beanie import init_beanie
from models import UserMetadata
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid
import logging

# Load environment variables
load_dotenv()

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.lock = asyncio.Lock()
    
    async def get_metadata(self, user_id: str) -> UserMetadata:
        async with self.lock:
            if user_id not in self.active_sessions:
                # Try to load existing metadata
                metadata = await UserMetadata.find_one(UserMetadata.user_id == user_id)
                if metadata:
                    self.active_sessions[user_id] = metadata
                else:
                    self.active_sessions[user_id] = UserMetadata(
                        user_id=user_id,
                        session_id=str(uuid.uuid4()),
                    )
            return self.active_sessions[user_id]
        
    async def add_metadata(self, user_id: str, **kwargs):
         async with self.lock:
            # Retrieve the metadata for the user
            metadata = await self.get_metadata(user_id)
            
            # Update the metadata with the provided kwargs
            for key, value in kwargs.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            
            # Save the updated metadata to the database
            await metadata.save()
            logging.info(f"Metadata for user {user_id} updated: {metadata}")