// src/app/models.ts

export interface Message {
    role: string;
    content: string;
}
  
export interface Conversation {
    name: string;
    conversation: Message[];
}
  