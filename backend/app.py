from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conexión a MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017/')
client = MongoClient(MONGO_URI)
db = client.chat_database
conversations_collection = db.conversations

# Crear índices para la colección
conversations_collection.create_index([('conversation_id', ASCENDING)], unique=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Base64File(BaseModel):
    pdf_file: str

class Message(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    conversation: List[Message]
    name: str = "New conversation"  # Valor predeterminado para el nombre

def convert_object_ids(document):
    if isinstance(document, dict):
        return {key: convert_object_ids(value) for key, value in document.items()}
    elif isinstance(document, list):
        return [convert_object_ids(element) for element in document]
    elif isinstance(document, ObjectId):
        return str(document)
    else:
        return document

@app.get("/backend/{conversation_id}")
async def get_conversation(conversation_id: str):
    logger.info(f"Retrieving conversation with ID {conversation_id}")
    conversation = conversations_collection.find_one({"conversation_id": conversation_id})
    if conversation:
        return convert_object_ids(conversation)
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.post("/backend/{conversation_id}")
async def backend(conversation_id: str, conversation: Conversation):
    logger.info(f"Sending Conversation with ID {conversation_id} to LLM service")
    existing_conversation = conversations_collection.find_one({"conversation_id": conversation_id})
    if not existing_conversation:
        # Incluir la primera pregunta del usuario en la nueva conversación
        user_message = conversation.dict()["conversation"][-1]
        existing_conversation = {
            "conversation_id": conversation_id,
            "conversation": [
                {"role": "system", "content": "You are a helpful assistant."},
                user_message
            ],
            "name": conversation.name if conversation.name else "New conversation"
        }
        conversations_collection.insert_one(existing_conversation)
    else:
        existing_conversation["conversation"].append(conversation.dict()["conversation"][-1])

    # Enviar la conversación al servicio LLM
    response = requests.post(f"http://llm_service:80/llm_service/{conversation_id}", json=convert_object_ids(existing_conversation))
    response.raise_for_status()
    assistant_message = response.json()["reply"]

    existing_conversation["conversation"].append({"role": "assistant", "content": assistant_message})
    conversations_collection.update_one({"conversation_id": conversation_id}, {"$set": {"conversation": existing_conversation["conversation"]}})

    return convert_object_ids(existing_conversation)

@app.patch("/name/{conversation_id}")
async def update_conversation_name(conversation_id: str, name: dict = Body(...)):
    logger.info(f"Updating name of conversation with ID {conversation_id} to {name['name']}")
    result = conversations_collection.update_one({"conversation_id": conversation_id}, {"$set": {"name": name['name']}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation name updated successfully"}

@app.post("/upload_files")
async def upload_files(file: UploadFile = File(...)):
    try:
        files = {'file': (file.filename, file.file, file.content_type)}
        response = requests.post("http://llm_service:80/process_file", files=files)
        response.raise_for_status()
        return {"message": "PDF processed successfully", "data": response.json()}
    except Exception as e:
        logger.error(f"File processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
async def get_conversations():
    try:
        conversations = conversations_collection.find().limit(10)
        conversation_list = [{"conversation_id": conv["conversation_id"], "name": conv.get("name", "New conversation")} for conv in conversations]
        return conversation_list
    except Exception as e:
        logger.error(f"Failed to retrieve conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
