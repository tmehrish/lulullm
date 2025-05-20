from pydantic import BaseModel
from beanie import Document
from datetime import datetime, timedelta
import asyncio

class SessionMetadata(BaseModel):
    user_id: str
    session_id: str
    stress_triggers: list[str] = []
    indecisiveness_triggers: list[str] = []
    preferred_tools: list[str] = []
    decision_patterns: dict = {}
    last_interaction: datetime = datetime.now()

class UserSession(Document):
    user_id: str
    metadata: SessionMetadata
    raw_chat: str
    timestamp: datetime = datetime.now()

    class Settings:
        name = "user_sessions"


async def session_cleanup_task():
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        stale_sessions = await UserSession.find(
            UserSession.timestamp < datetime.now() - timedelta(minutes=30)
        ).to_list()
        
        for session in stale_sessions:
            await session.delete()


