from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PyPDF2 import PdfReader
import os
import logging
from dotenv import find_dotenv, load_dotenv

from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.chat_models.huggingface import ChatHuggingFace 
from langchain_community.llms import HuggingFaceHub

from huggingface_hub import login

from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.vectorstores.pgvector import PGVector

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
)

ROLE_CLASS_MAP = {
    "assistant": AIMessage,
    "user": HumanMessage,
    "system": SystemMessage
}

load_dotenv(find_dotenv())

CONNECTION_STRING = "postgresql+psycopg2://admin:admin@postgres:5432/vectordb"
COLLECTION_NAME="vectordb"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    conversation: List[Message]

login(token=os.environ["HUGGINGFACEHUB_API_TOKEN"])

logger.info("Loading embeddings")
embeddings = HuggingFaceInstructEmbeddings(
    model_name="hkunlp/instructor-xl",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

logger.info("Loading LLM")
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

logger.info("Chat loaded")

store = PGVector(
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
)

logger.info("Store loaded")
retriever = store.as_retriever()

prompt_template = """
As a HR Assistant, you have access to detailed curriculum vitae information of our employees. Using this information, please provide the most suitable response to the user's inquiries about our employees' professional profiles. 

{context}

Please respond with relevant data about the employee as per the user's query and respond all the questions in Catalan.
Answer:
"""

prompt = PromptTemplate(
    template=prompt_template, input_variables=["context"]
)
system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)

def create_messages(conversation):
    return [ROLE_CLASS_MAP[message.role](content=message.content) for message in conversation]


def format_docs(docs):
    formatted_docs = []
    for doc in docs:
        formatted_doc = "Source: " + doc.metadata['source']
        formatted_docs.append(formatted_doc)
    return '\n'.join(formatted_docs)

def extract_last_assistant_message(full_response):
    # Divide la respuesta en partes basada en el separador "</s>"
    messages = full_response.split('</s>')
    # Extrae el último mensaje no vacío
    for message in reversed(messages):
        return message.strip()
    return "No response found from the assistant."  # Respuesta predeterminada si no se encuentra nada

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("App loaded")

@app.post("/llm_service/{conversation_id}")
async def llm_service(conversation_id: str, conversation: Conversation):

    query = conversation.conversation[-1].content

    docs = retriever.get_relevant_documents(query=query)

    prompt = system_message_prompt.format(context=docs)
    messages = [prompt] + create_messages(conversation=conversation.conversation)

    result = chat(messages)

    last_response = extract_last_assistant_message(result.content)
    
    return {"id": conversation_id, "reply": last_response}


@app.post("/process_file")
async def process_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        logger.error("Invalid file type: " + file.content_type)
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        # Read and extract text from PDF
        pdf_reader = PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + " "

        # Split the text into manageable chunks
        text_chunks = get_text_chunks(text)

        # Generate embeddings for the text chunks
        embeddings_results = embeddings.embed_documents(text_chunks)

        # Store the text chunks and their embeddings using PGVector
        store.add_embeddings(texts=text_chunks, embeddings=embeddings_results)

        return {"status": "Embeddings stored successfully"}
    except Exception as e:
        logger.error(f"Failed to process the file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
