import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel


# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")


prompt_template = '''
        You are an extractor agent that takes a chat history
        and extracts the following information based on the conversation:
        - Stress triggers
        - Indecisiveness triggers
        - Preferred tools
        - Decision patterns
        - Other relevant information
        then returns it in a format similar to this:
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
llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=key)

extractor_agent = create_react_agent(
    llm,
    tools=[],
    prompt=prompt_template,
    checkpointer=MemorySaver(),
)


