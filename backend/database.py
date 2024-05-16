from pymongo import MongoClient, ASCENDING
import os

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.chat_database
conversations_collection = db.conversations

# Crear índices para la colección
conversations_collection.create_index([('conversation_id', ASCENDING)], unique=True)
