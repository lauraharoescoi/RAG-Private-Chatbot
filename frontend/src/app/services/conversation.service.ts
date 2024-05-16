import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Conversation, Message } from '../models';
import { SERVER_URLS } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  constructor(private http: HttpClient) {}

  getConversation(conversationId: string): Observable<Conversation> {
    const url = SERVER_URLS.conversation.get_conversation.replace(':conversationId', conversationId);
    return this.http.get<Conversation>(url);
  }

  postConversation(conversationId: string, conversation: Message[]): Observable<Conversation> {
    const url = SERVER_URLS.conversation.post_conversation.replace(':conversationId', conversationId);
    return this.http.post<Conversation>(url, { conversation });
  }

  updateConversationName(conversationId: string, name: string): Observable<void> {
    const url = SERVER_URLS.conversation.update_conversation_name.replace(':conversationId', conversationId);
    return this.http.patch<void>(url, { name });
  }

  getConversations(): Observable<{ conversation_id: string, name: string }[]> {
    return this.http.get<{ conversation_id: string, name: string }[]>(SERVER_URLS.conversation.get_conversations);
  }
}
