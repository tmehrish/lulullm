
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.storage.models import UserMetadata
from app.storage.session_managing import MetadataManager
from app.agents.supervisor_agent import orchestrator
from app.agents.metadata_agent import metadata_agent, process_history
from app.agents.supervisor_agent import orchestrator
from motor.motor_asyncio import AsyncIOMotorClient
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from uuid import uuid4
from passlib.context import CryptContext
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import uvicorn
import asyncio
from beanie import init_beanie

# Load environment variables
load_dotenv()
MONGO_URL = os.getenv("MONGO_URI")

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URL)
db = client["lulullm"]
user_collection = db["users"]

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    user_id: str

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB connection
async def init_database():
    client = AsyncIOMotorClient(MONGO_URL)  # Use AsyncIOMotorClient for async operations
    await init_beanie(
        database=client.lulullm,
        document_models=[UserMetadata],
    )
    return client.lulullm  # Return the database instance

@app.on_event("startup")
async def startup_event():
    # Initialize database and metadata manager
    global metadata_manager
    db = await init_database()
    metadata_manager = MetadataManager()

    # Start background task to check user idle status
    asyncio.create_task(check_user_idle())

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}

# Sign-up endpoint
@app.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    # Check if username already exists
    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash the password and create a new user
    hashed_password = pwd_context.hash(user.password)
    user_id = str(uuid4())
    new_user = {"username": user.username, "password_hash": hashed_password, "user_id": user_id}
    await user_collection.insert_one(new_user)
    return {"username": user.username, "user_id": user_id}

# Sign-in endpoint
chat_history = {}
@app.post("/signin", response_model=UserResponse)
async def signin(user: UserCreate):
    global chat_history
    # Check if username exists
    existing_user = await user_collection.find_one({"username": user.username})
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # Verify the password
    if not pwd_context.verify(user.password, existing_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    chat_history['user_id'] = existing_user['user_id']
    print(f"User's chat history {chat_history} loaded")
    print(chat_history['user_id'])
    return {"username": existing_user["username"], "user_id": existing_user["user_id"]}

# Invoke endpoint
@app.post("/invoke")
async def invoke(user_input: str):
    global chat_history
    config = {"thread_id": str(uuid4())}
    user_id = chat_history["user_id"]
    metadata = await metadata_manager.get_metadata(user_id)
    # Create context-aware input
    context = f"""
    User Metadata:
    {metadata.model_dump_json()}
    
    Chat History:
    {user_input}
    """
    response = await orchestrator.ainvoke({"messages": context}, config=config)
    # Extract the content of the AIMessage
    ai_message_content = None
    for message in response['messages']:
        if isinstance(message, AIMessage) and message.content:
            ai_message_content = message.content
            break
    
    if ai_message_content:
        chat_history[user_input] = ai_message_content
        return ai_message_content
    else:
        print("Supervisor: No relevant AIMessage found.")

# Track user activity
user_activity = {"last_activity": datetime.now(), "is_idle": False}

# Refactor metadata
async def refactor():
    global chat_history, metadata_manager
    print(chat_history)
    user_id = chat_history["user_id"]
    if not user_id:
        raise HTTPException(status_code=400, detail="User not signed in")
    
    try:
        await process_history(user_id, chat_history, metadata_manager)
        print(f"Metadata updated for user {user_id}")
        return {"message": "Metadata updated successfully"}
    except Exception as e:
        logging.error(f"Error updating metadata: {e}")
        print(f"Error updating metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Check user idle status
async def check_user_idle():
    while True:
        await asyncio.sleep(60)  # Check every minute
        last_active = user_activity.get("last_activity")
        if last_active and datetime.now() - last_active > timedelta(minutes=5):
            # Trigger metadata refactor
            if not user_activity["is_idle"]:
                user_activity["is_idle"] = True
                print("User is idle, triggering metadata refactor")
                await refactor()

# Middleware to update user activity
@app.middleware("http")
async def update_user_activity(request: Request, call_next):
    user_activity["last_activity"] = datetime.now()  
    user_activity["is_idle"] = False
    response = await call_next(request)  
    return response

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
