import os
import uuid
import logging
import json
import ast
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
from app.backend.storage.models import UserMetadata
from app.backend.storage.session_managing import MetadataManager


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
        then returns it looking like this (the original metadata) in a Python dictionary format:
        {
            'user_id': 'yash_khanna',
            'session_id': '123456',
            'stress_triggers': ['perfectionism', 'time pressure'],
            'indecisiveness_triggers': ['fear of failure', 'overthinking'],
            'preferred_tools': ['weighted scoring', 'body scan'],
            'decision_patterns': ['avoids financial decisions'],
            'last_interaction': '2025-05-16T16:03:00Z'
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
    {metadata.model_dump()}

    Chat History:
    {history}
    """

    config = {"configurable":
              {"thread_id": str(uuid.uuid4())}}

    response = await metadata_agent.ainvoke({"messages": context}, config=config)
    logging.info(f"Metadata {response} extracted")
    print(f"Metadata {response} extracted")
    
    new_metadata = None
    # Extract the AIMessage from the response
    try:
        messages = response.get("messages", [])
        ai_message = next(
            (message for message in messages if isinstance(message, AIMessage)), None
        )
        print(f"AIMessage content type: {type(ai_message.content)}")
        print(f"AIMessage content: {ai_message.content}")
        cleaned_content = ai_message.content.strip("```python").strip("```").strip()
        llm_response = ast.literal_eval(cleaned_content)
        print(f"LLM response: {llm_response}")
        new_metadata = UserMetadata(
            user_id=llm_response["user_id"],
            session_id=llm_response["session_id"],
            stress_triggers=llm_response["stress_triggers"],
            indecisiveness_triggers=llm_response["indecisiveness_triggers"],
            preferred_tools=llm_response["preferred_tools"],
            decision_patterns=llm_response["decision_patterns"],
            last_interaction=llm_response["last_interaction"]
        )
        print(f"New metadata created: {new_metadata}")
    except (ValueError, SyntaxError) as e:
        logging.error(f"Error parsing AIMessage content: {e}")
        print(f"Error parsing AIMessage content: {e}")
        raise ValueError("Failed to parse AIMessage content into metadata.")
    try:
        print("Calling add_metadata")  
        await metadata_manager.add_metadata(user_id, new_metadata)
        print(f"Metadata {new_metadata} updated")
    except Exception as e:
        logging.error(f"Error updating metadata: {e}")
        print(f"Error updating metadata: {e}")
        raise e
