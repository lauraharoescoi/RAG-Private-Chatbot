from fastapi import APIRouter, HTTPException
from app.models import Conversation
from app.utils import create_messages, extract_last_assistant_message
from langchain.prompts import ChatPromptTemplate
from app.config import chat, retriever
from langserve import add_routes
from langchain.schema import HumanMessage, AIMessage, SystemMessage

router = APIRouter()

prompt_template = """
As an HR Assistant, you have access to detailed curriculum vitae information of our employees. Using this information, please provide the most suitable response to the user's inquiries about our employees' professional profiles.

{context}

Please respond with relevant data about the employee as per the user's query and respond to all the questions. If the information is not available in the provided context, respond with "No information available."

Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
print("Prompt:", prompt)  # Para depuración

# Add routes using LangServe
add_routes(router, prompt, path="/llm_service")

def convert_to_chat_message(role: str, content: str):
    if role == "system":
        return SystemMessage(content=content)
    elif role == "user":
        return HumanMessage(content=content)
    elif role == "assistant":
        return AIMessage(content=content)
    else:
        raise ValueError(f"Unknown role: {role}")

@router.post("/conversation/{conversation_id}")
async def llm_service_custom(conversation_id: str, conversation: Conversation):
    query = conversation.conversation[-1].content
    docs = retriever.get_relevant_documents(query=query)
    print("Initial docs retrieved:", docs)  # Para depuración

    # Check if any documents were found
    if not docs:
        return {"id": conversation_id, "reply": "No information available."}

    # Collect all unique custom_ids from the retrieved docs
    custom_ids = {doc.metadata.get("custom_id") for doc in docs if "custom_id" in doc.metadata}
    print("Custom IDs:", custom_ids)  # Para depuración

    # Check if any custom_ids were found
    if not custom_ids:
        return {"id": conversation_id, "reply": "No information available."}

    # Retrieve all chunks associated with the found custom_ids
    all_docs = []
    for custom_id in custom_ids:
        related_docs = retriever.get_relevant_documents(query="", search_kwargs={"filter": {"custom_id": custom_id}})
        print("Docs for custom_id", custom_id, ":", related_docs)  # Para depuración
        all_docs.extend(related_docs)
    
    context = "\n".join([doc.metadata.get('source', '') for doc in all_docs if 'source' in doc.metadata])
    print("Context:", context)  # Para depuración
    prompt_text = prompt.format(context=context)
    messages = [convert_to_chat_message("system", prompt_text)] + create_messages(conversation=conversation.conversation)
    result = chat(messages)
    last_response = extract_last_assistant_message(result.content)
    
    # Ensure the LLM response is constrained to the available context
    if "No information available." in last_response:
        return {"id": conversation_id, "reply": "No information available."}
    
    return {"id": conversation_id, "reply": last_response}
