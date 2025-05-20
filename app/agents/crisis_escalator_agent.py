import logging
import uuid
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
loader = WebBaseLoader(web_paths=["https://www.kansashealthsystem.com/news-room/blog/2020/03/managing-anxiety-during-crisis",
                                  "https://www.healthline.com/health/grounding-techniques#physical-techniques",
                                  "https://www.fcc.gov/988-suicide-and-crisis-lifeline",],)
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
    docs = retriever.invoke(query)
    texts = [doc.page_content for doc in docs]
    return "\n\n".join(texts),docs


## Create ReAct Agent w/ retriever tool ##


# Re-worded prompt with more specific instructions
prompt_template = ('''
            You are a crisis escalator who only functions when a situation has to be escalated immediately.
            Your main job is to try to make sure the user is okay.
            ONLY use the retrieved imformation to answer the user's question.
            If there isn't any relevant information available, just say "I don't know".'''
        )


# Build agent
llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=key)

crisis_escalator_agent = create_react_agent(
    llm,
    tools = [retrieve],
    name='crisis_escalator_agent',
    prompt = prompt_template,
)

# Stream agent conversation w/ user
'''
config = {"configurable": {"thread_id": "abc123"}}

while True:
    # Get user input
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Exiting the chat. Goodbye!")
        break

    final_response = None

    for step in crisis_escalator_agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode="values",
        config=config,
    ):
        final_response = step["messages"][-1]

    if final_response:
        final_response.pretty_print()
       
'''
