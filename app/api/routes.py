import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.storage.models import UserMetadata
from app.storage.session_managing import MetadataManager
from app.agents.supervisor_agent import orchestrator
from app.agents.metadata_agent import metadata_agent, process_history
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from uuid import uuid4
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import uvicorn

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
@app.post("/signin", response_model=UserResponse)
async def signin(user: UserCreate):
    # Check if username exists
    existing_user = await user_collection.find_one({"username": user.username})
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # Verify the password
    if not pwd_context.verify(user.password, existing_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"username": existing_user["username"], "user_id": existing_user["user_id"]}


# invoke



if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port = 8000)
