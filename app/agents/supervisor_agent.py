from langgraph_supervisor import create_supervisor
#from crisis_escalator_agent import crisis_escalator_agent
from lifestyle_coach_agent import lifestyle_coach_agent
from app.agents.initial_stress_agent import init_stress_agent
from app.agents.decision_maker_agent import decision_maker_agent
from app.agents.indecision_analyst_agent import indecision_analyst_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv

print("Supervisor agent loaded")
# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=key)

prompt_template = ('''
            You are a team supervisor managing an initial stress agent,
            a decision maker agent, an indecision analyst agent, a 
            lifestyle coach agent, a crisis escalator agent, and a
            general chat agent. Use these rough guidelines to decide
            which agent to delegate to:
                    - Initial Stress Agent : If the user is experiencing stress/anxiety and they want to get rid of it/ need an opinion on it
                    - Decision Maker Agent : If the user is experiencing indecision and they need guidance in making a decision
                    - Indecision Analyst Agent: If the user wants to find the cause of their indecison and overcome it or if they want to find the root cause of a problem
                    - Lifestyle Coach Agent: If the user wants to reduce stress/anxiety/indecision in the long run and they want to be informed about it
                    - Crisis Escalator Agent: If the user is in a crisis and they need immediate help
                    - General Chat Agent: If the user is asking a supplemental question that doesn't fit into any of the above categories but is needed for context for a follow up or if the user wants a general convo
            
            Also, tell the agents to answer the question in a way that is digestible for the user.
                   ''')



orchestrator = create_supervisor(
    [init_stress_agent,
     decision_maker_agent,
     indecision_analyst_agent,
     lifestyle_coach_agent],
     model=llm,
     prompt=prompt_template,
     output_mode="full history",
)

app = orchestrator.compile(
    checkpointer=MemorySaver(),
)

# Test the agent with a sample query 

config = {"configurable": {"thread_id": "abc123"}}

