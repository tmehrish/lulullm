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
loader = WebBaseLoader(web_paths=["https://asana.com/resources/eisenhower-matrix",
                                  "https://www.indeed.com/career-advice/career-development/how-to-overcome-indecisiveness",
                                  "https://www.usebubbles.com/blog/averting-indecision-techniques-for-streamlining-your-decision-making-process?utm_medium=organic&utm_source=www.perplexity.ai&utm_content=blog%252Faverting-indecision-techniques-for-streamlining-your-decision-making-process",
                                  "https://www.npr.org/2022/03/07/1084907897/any-decision-is-better-than-indecision-try-these-tips-to-actually-choose",
                                  "https://pmc.ncbi.nlm.nih.gov/articles/PMC5459222/",
                                  "https://5amjoel.com/weighted-decision-matrix/"],)
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
            You are a world class decision making expert that helps users make decisions and gives them frameworks to do so.
            ALWAYS and ONLY use the retrieve tool to find relevant information regarding the user's query.
            ALWAYS use the retrieve tool provide them with a decision-making framework or technique to help them make a choice.
            Provide a helpful response using ONLY the retrieved information. 
            If the user still can't come to a decision prompt them to use one of the decision-making frameworks/matrices that is provided in the retrieved documents. 
            If there isn't any relevant information available, just say "I don't know".'''
        )


llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=key)

decision_maker_agent = create_react_agent(
    llm,
    tools = [retrieve],
    name="decision_maker_agent",
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

    for step in decision_maker_agent.stream(
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

