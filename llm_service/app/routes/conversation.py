from fastapi import APIRouter, HTTPException
from app.models import Conversation
from app.utils import create_messages, extract_last_assistant_message
from app.config import embeddings, llm, chat, retriever
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langserve import add_routes

router = APIRouter()

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Prompt template con variables correctas
qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\

{context}"""


qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


# Definir la función para convertir roles en mensajes de chat
def convert_to_chat_message(role: str, content: str):
    if role == "system":
        return SystemMessage(content=content)
    elif role in ["user", "human"]:
        return HumanMessage(content=content)
    elif role in ["assistant", "AI"]:
        return AIMessage(content=content)
    else:
        raise ValueError(f"Unknown role: {role}")


# # Añadir rutas utilizando LangServe
# add_routes(router, qa_system_prompt , path="/llm_service")

@router.post("/conversation/{conversation_id}")
async def llm_service_custom(conversation_id: str, conversation: Conversation):
    query = conversation.conversation[-1].content
    print("Query: ", query)
    
    # Construir el historial de la conversación
    print("Conversation: ", conversation.conversation)
    chat_history = [convert_to_chat_message(message.role, message.content) for message in conversation.conversation]
    print("Chat history: ", chat_history)

    response = rag_chain.invoke({
        "input": query,
        "chat_history": chat_history
    })
    print("Response: ", response)

    # Extraer y limpiar la última respuesta del asistente
    last_response = extract_last_assistant_message(response["answer"])
    print("Last response: ", last_response)

    # Asegurar que la respuesta del LLM esté restringida al contexto disponible
    if "No information available." in last_response:
        return {"id": conversation_id, "reply": "No information available."}
    
    return {"id": conversation_id, "reply": last_response}
