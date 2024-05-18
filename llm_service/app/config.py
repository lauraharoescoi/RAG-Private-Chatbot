import os
from dotenv import load_dotenv, find_dotenv
from huggingface_hub import login
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.llms import HuggingFaceHub
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain.vectorstores.pgvector import PGVector
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv(find_dotenv())

login(token=os.environ["HUGGINGFACEHUB_API_TOKEN"])

CONNECTION_STRING = "postgresql+psycopg2://admin:admin@postgres:5432/vectordb"
COLLECTION_NAME = "vectordb"

# Load embeddings, LLM, and retriever
embeddings = HuggingFaceInstructEmbeddings(
    model_name="hkunlp/instructor-xl",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

llm = HuggingFaceHub(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    model_kwargs={
        "max_new_tokens": 512,
        "top_k": 30,
        "temperature": 0.1,
        "repetition_penalty": 1.03,
    },
)

chat = ChatHuggingFace(llm=llm)

store = PGVector(
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
)

# InMemoryStore for parent documents
byte_store = InMemoryStore()

# Text splitters for parent and child documents with larger chunk sizes
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Create ParentDocumentRetriever
loader = ParentDocumentRetriever(
    vectorstore=store,
    docstore=byte_store,
    parent_id_key="custom_id",
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

retriever = store.as_retriever()
