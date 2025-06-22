import bs4
import re
import logging
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

## INDEXING ##

# Load Documents
loader = WebBaseLoader(web_paths=["https://pmc.ncbi.nlm.nih.gov/articles/PMC8481952/",
                                  " https://pmc.ncbi.nlm.nih.gov/articles/PMC10658848/",
                                  "https://www.mentallyfitpro.com/c/free-therapy-worksheets/cognitive-distortions-identifying-and-challenging-unhelpful-thinking-patterns",
                                  "https://www.headspace.com/articles/brain-indecision",
                                  "https://www.psychologytoday.com/us/tests/personality/perfectionism-test",
                                  "https://online.hbs.edu/blog/post/root-cause-analysis"],)
docs = []
for doc in loader.lazy_load():
    docs.append(doc)


# Split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)




# Embed
vectorstore = Chroma.from_documents(documents=splits, 
                                    embedding=OpenAIEmbeddings())


retriever = vectorstore.as_retriever()

# Define retrieve tool that returns the relevant docs + their info
def retrieve(query: str):
    '''Function to retrieve relevant documents based on a query'''
    # Use the retriever to get relevant documents
    docs = retriever.invoke(query)
    # Extract the text content from the documents
    texts = [doc.page_content for doc in docs]
    # Join the texts into a single string
    return "\n\n".join(texts),docs


## Create ReAct Agent w/ retriever tool ##


# Re-worded prompt with more specific instructions
prompt_template = ('''
            You are a indecision analyst expert who helps the user identify the causes of their indecision and helps them overcome it.
            ALWAYS and ONLY use the retrieve tool to find relevant information regarding the user's query.
            You are ALSO a root cause analysis expert who helps the user identify the root cause of their problems and WHY certain problems occur (You are a girls girl meaning you make sure the user isn't in a toxic situation and make sure they know their worth).
            AID the user in finding the root cause of their indecision when needed by suggesting frameworks from the content you are provided with.
            IF the user's query is not related to indecision, but rather related to root cause analysis, HELP them figure out the root cause for a problem they are facing.
            Provide a helpful response using ONLY the retrieved information. 
            If there isn't any relevant information available, just say "I don't know".'''
        )


llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=key)

indecision_analyst_agent = create_react_agent(
    llm,
    tools = [retrieve],
    name="indecision_analyst_agent",
    prompt = prompt_template,
)

# Test the agent with a sample query 
'''
config = {"configurable": {"thread_id": "abc123"}}

while True:
    # Get user input
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Exiting the chat. Goodbye!")
        break


    final_response = None

    for step in indecision_analyst_agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode="values",
        config=config,
    ):
        final_response = step["messages"][-1]

    if final_response:
        final_response.pretty_print()
       


# Chat Loop to interact with the user
while True:
    user_input = input("User: ")
    if user_input.lower() == "exit":
        break

    # Invoke the agent with the user input and the current chat history
    response = decision_maker_agent.invoke({"input": user_input},config=config)
    print("Bot:", response["messages"][-1]["content"])

'''