import os
import uuid
import logging
import json
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import Checkpoint
from pymongo import MongoClient
from beanie import init_beanie
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from app.storage.models import UserMetadata
from app.storage.session_managing import MetadataManager


# Serves as cross-thread memory setup 

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
mongo_key = os.getenv("MONGO_URI")

# Initialize MongoDB connection
async def init_database():
    client = MongoClient(mongo_key)
    await init_beanie(
        database=client.lulullm,
        document_models=[UserMetadata],
    )

prompt_template = '''
        You are an extractor agent that takes a chat history and metadata
        and updates the metadata by extracting info from the chat history such as:
        - Stress triggers
        - Indecisiveness triggers
        - Preferred tools
        - Decision patterns
        - Other relevant information
        then returns it in a format similar to this (the metadata):
        {
            "user_id": "yash_khanna",
            "session_id": "123456",
            "stress_triggers": ["perfectionism", "time pressure"],
            "indecisiveness_triggers": ["fear of failure", "overthinking"],
            "preferred_tools": ["weighted scoring", "body scan"],
            "decision_patterns": ["avoids financial decisions"],
            "last_interaction": "2025-05-16T16:03:00Z"
        }
    '''

# Build agent
llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=os.getenv(openai_key))

metadata_agent = create_react_agent(
    llm,
    tools=[],
    prompt=prompt_template,
    checkpointer=MemorySaver(),
)


async def process_history(user_id:str, history: str, metadata_manager: MetadataManager):

    metadata = await metadata_manager.get_metadata(user_id)
    # Create context-aware input
    context = f"""
    User Metadata:
    {metadata.model_dump_json()}
    
    Chat History:
    {history}
    """

    config = {"configurable":
              {"thread_id": str(uuid.uuid4())}}

    response = await metadata_agent.ainvoke({"messages": context}, config=config)
    logging.info(f"Metadata {response} extracted")
    print(f"Metadata {response} extracted")
    # Extract the AIMessage from the response
    try:
        messages = response.get("messages", [])
        ai_message = next(
            (message for message in messages if isinstance(message, AIMessage)), None
        )
        if ai_message:
            updated_message = json.loads(ai_message.content)
            print("Extracted AIMessage content:")
            print(updated_message)     
        else:
            print("No AIMessage found in the response.")
    except Exception as e:
        logging.error(f"Error extracting AIMessage: {e}")
        print(f"Error extracting AIMessage: {e}")
    try:

        await metadata_manager.add_metadata(user_id, updated_message)
        logging.info(f"Metadata {updated_message} updated")
        print(f"Metadata {updated_message} updated")
    except Exception as e:
        logging.error(f"Error updating metadata: {e}")
        print(f"Error updating metadata: {e}")
        raise e
