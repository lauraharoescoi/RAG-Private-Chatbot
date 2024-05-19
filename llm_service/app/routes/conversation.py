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
from app.config import retriever, chat, store, embeddings, llm

load_dotenv(find_dotenv())

router = APIRouter()


prompt_template = """
As an HR Assistant, you have access to detailed curriculum vitae information of our employees. Using this information, please provide the most suitable response to the user's inquiries about our employees' professional profiles.

{context}

Please respond with relevant data about the employee as per the user's query and respond to all the questions in Catalan. If the information is not available in the provided context, respond with "No information available."

Answer:
"""

prompt = PromptTemplate(
    template=prompt_template, input_variables=["context"]
)
system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)

# Add routes using LangServe
add_routes(router, prompt, path="/llm_service")

@router.post("/llm_service/{conversation_id}")
async def llm_service_custom(conversation_id: str, conversation: Conversation):
    query = conversation.conversation[-1].content

    docs = retriever.get_relevant_documents(query=query)

    prompt = system_message_prompt.format(context=docs)
    messages = [prompt] + create_messages(conversation=conversation.conversation)

    result = chat(messages)

    last_response = extract_last_assistant_message(result.content)
    
    return {"id": conversation_id, "reply": last_response}
    
    # # Ensure the LLM response is constrained to the available context
    # if "No information available." in last_response:
    #     return {"id": conversation_id, "reply": "No information available."}
    
    # return {"id": conversation_id, "reply": last_response}
