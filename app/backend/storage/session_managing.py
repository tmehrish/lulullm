from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import Checkpoint
from pymongo import MongoClient
from beanie import init_beanie, PydanticObjectId
from app.backend.storage.models import UserMetadata
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid
import logging

# Load environment variables
load_dotenv()

class MetadataManager:
    def __init__(self):
        self.active_sessions = {}
        self.lock = asyncio.Lock()
    
    async def get_metadata(self, user_id) -> UserMetadata:
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
        
    async def add_metadata(self, user_id: str, metadata_instance: UserMetadata):
        print("Adding metadata")
        try:
    
            existing_metadata = await UserMetadata.find_one(UserMetadata.user_id == user_id)

            if existing_metadata:
                # Replace the existing document
                metadata_instance.id = existing_metadata.id  # Ensure the ID is preserved
                await metadata_instance.replace()
            else:
                # Insert a new document if no match is found
                await metadata_instance.insert()
            print("Metadata updated")
                
            # Update the active sessions
            self.active_sessions[user_id] = metadata_instance

            logging.info(f"Metadata for user {user_id} updated: {metadata_instance}")
            print(f"Metadata for user {user_id} updated: {metadata_instance}")
        except Exception as e:
            logging.error(f"Error adding metadata for user {user_id}: {e}", exc_info=True)
            print(f"Error adding metadata for user {user_id}: {e}")
         


metadata = MetadataManager()
