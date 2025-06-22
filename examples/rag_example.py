import bs4
import re
import logging
import os
from dotenv import load_dotenv
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

#### INDEXING ####

# Load Documents
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

# Split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# Embed
vectorstore = Chroma.from_documents(documents=splits, 
                                    embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever()

#### RETRIEVAL and GENERATION ####

# Prompt
prompt = hub.pull("rlm/rag-prompt")

# LLM
llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=key)

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Question
response = rag_chain.invoke("What is Task Decomposition?")
print(response)












####################################

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
from langchain.retrievers.multi_query import MultiQueryRetriever

# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

#### INDEXING ####

# Load Documents
loader = WebBaseLoader(web_paths=["https://pmc.ncbi.nlm.nih.gov/articles/PMC10741869/",
                                  "https://www.healthline.com/health/grounding-techniques#physical-techniques",
                                  "https://www.resiliencelab.us/thought-lab/grounding-techniques",
                                  "https://www.ncbi.nlm.nih.gov/books/NBK207188/box/part1_ch4.box5/?report=objectonly"],)
docs = {}
for doc in loader.lazy_load():
    docs['url'].append(doc)


# Split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
#print(splits)

# Embed
vectorstore = Chroma.from_documents(documents=splits, 
                                    embedding=OpenAIEmbeddings())

query = "What is the 4-7-8 breathing technique?"
retriever = vectorstore.as_retriever()
ans = retriever.get_relevant_documents(query)
#print("Retrieved Documents:")
#for doc in ans:
    #print(doc.page_content)


#### RETRIEVAL and GENERATION ####

llm = ChatOpenAI(model_name="gpt-4o", temperature=0,api_key=key)
retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever, llm=llm
)
retrieved_docs = retriever_from_llm.invoke("What is the 4-7-8 breathing technique?")





# Re-word some of the LangChain rag prompt to not restrict the 
# llm's output size and cater more to the stress and anxiety domain
prompt_template = '''
You are an initial stress responder agent for question-answering tasks. 
Your job is to help the user by providing them with information/practices to reduce anxiety and stress.
Use ONLY the following pieces of retrieved context to answer the question.
Give a quote from the retrieved context to support your answer. 
If you don't know the answer, just say "I don't know".
 
Question: {question} 
Context: {context} 
Answer:
'''
prompt = ChatPromptTemplate.from_template(prompt_template)

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Question
response = rag_chain.invoke("What is the 4-7-8 breathing technique?")



question = "I'm feeling anxious and stressed. I seem to be breathing quickly and shallowly. What are some breathing exercises I can do to help calm down?"







