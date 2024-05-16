from fastapi import APIRouter, HTTPException
from app.models import Conversation
from app.utils import create_messages, extract_last_assistant_message
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain_community.llms import HuggingFaceHub
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langserve import add_routes
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

router = APIRouter()

CONNECTION_STRING = "postgresql+psycopg2://admin:admin@postgres:5432/vectordb"
COLLECTION_NAME="vectordb"

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

retriever = store.as_retriever()

prompt_template = """
As an HR Assistant, you have access to detailed curriculum vitae information of our employees. Using this information, please provide the most suitable response to the user's inquiries about our employees' professional profiles.

{context}

Please respond with relevant data about the employee as per the user's query and respond to all the questions in Catalan. If the information is not available in the provided context, respond with "No information available."

Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)

# Add routes using LangServe
add_routes(router, prompt, path="/llm_service")

@router.post("/llm_service_custom/{conversation_id}")
async def llm_service_custom(conversation_id: str, conversation: Conversation):
    query = conversation.conversation[-1].content
    docs = retriever.get_relevant_documents(query=query)
    
    # Check if any documents were found
    if not docs:
        return {"id": conversation_id, "reply": "No information available."}

    # Collect all unique document_ids from the retrieved docs
    document_ids = {doc.metadata["document_id"] for doc in docs}

    # Retrieve all chunks associated with the found document_ids
    all_docs = []
    for document_id in document_ids:
        docs_for_id = retriever.get_relevant_documents(query=document_id, filter_by_metadata={"document_id": document_id})
        all_docs.extend(docs_for_id)
    
    context = "\n".join([doc.metadata['source'] for doc in all_docs])
    prompt_text = system_message_prompt.format(context=context)
    messages = [prompt_text] + create_messages(conversation=conversation.conversation)
    result = chat(messages)
    last_response = extract_last_assistant_message(result.content)
    
    # Ensure the LLM response is constrained to the available context
    if "No information available." in last_response:
        return {"id": conversation_id, "reply": "No information available."}
    
    return {"id": conversation_id, "reply": last_response}
