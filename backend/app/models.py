from pydantic import BaseModel
from typing import List

class Message(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    conversation: List[Message]
    name: str = "New conversation"  # Valor predeterminado para el nombre
