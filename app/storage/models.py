from beanie import Document
from datetime import datetime, timedelta
from typing import List, Dict

class UserMetadata(Document):  # Inherit from Beanie's Document
    user_id: str
    session_id: str
    stress_triggers: List[str] = []
    indecisiveness_triggers: List[str] = []
    preferred_tools: List[str] = []
    decision_patterns: Dict = {}
    last_interaction: datetime = datetime.now()

    class Settings:
        collection = "user_metadata"  # Specify the MongoDB collection name





