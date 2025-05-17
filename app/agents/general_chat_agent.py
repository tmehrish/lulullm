import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

# Re-worded prompt with more specific instructions
prompt_template = ('''
            You are a smart assistant who helps the user with general questions'''
        )


llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=key)

general_chat_agent = create_react_agent(
    llm,
    tools = [],
    prompt = prompt_template,
    checkpointer=MemorySaver()
)

# Test the agent with a sample query 

config = {"configurable": {"thread_id": "abc123"}}

while True:
    # Get user input
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Exiting the chat. Goodbye!")
        break

    final_response = None

    for step in general_chat_agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode="values",
        config=config,
    ):
        final_response = step["messages"][-1]

    if final_response:
        final_response.pretty_print()
       
