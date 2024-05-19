from fastapi import APIRouter, HTTPException, Body
import logging
from pymongo import MongoClient
import requests
from bson import ObjectId
from app.models import Conversation
from app.database import conversations_collection
from app.utils import convert_object_ids

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    logger.info(f"Retrieving conversation with ID {conversation_id}")
    conversation = conversations_collection.find_one({"conversation_id": conversation_id})
    if conversation:
        return convert_object_ids(conversation)
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@router.post("/{conversation_id}")
async def post_conversation(conversation_id: str, conversation: Conversation):
    logger.info(f"Sending Conversation with ID {conversation_id} to LLM service")
    existing_conversation = conversations_collection.find_one({"conversation_id": conversation_id})
    if not existing_conversation:
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

    response = requests.post(f"http://llm_service:80/llm_service/{conversation_id}", json=convert_object_ids(existing_conversation))
    response.raise_for_status()
    assistant_message = response.json()["reply"]

    existing_conversation["conversation"].append({"role": "assistant", "content": assistant_message})
    conversations_collection.update_one({"conversation_id": conversation_id}, {"$set": {"conversation": existing_conversation["conversation"]}})

    return convert_object_ids(existing_conversation)

@router.patch("/name/{conversation_id}")
async def update_conversation_name(conversation_id: str, name: dict = Body(...)):
    logger.info(f"Updating name of conversation with ID {conversation_id} to {name['name']}")
    result = conversations_collection.update_one({"conversation_id": conversation_id}, {"$set": {"name": name['name']}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation name updated successfully"}

@router.get("/")
async def get_conversations():
    try:
        conversations = conversations_collection.find().limit(10)
        conversation_list = [{"conversation_id": conv["conversation_id"], "name": conv.get("name", "New conversation")} for conv in conversations]
        return conversation_list
    except Exception as e:
        logger.error(f"Failed to retrieve conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
