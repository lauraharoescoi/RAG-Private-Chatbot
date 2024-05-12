// conversation.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Conversation, Message } from '../models';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  private apiUrl = 'http://localhost:5000/backend';

  constructor(private http: HttpClient) {}

  getConversation(conversationId: string): Observable<Conversation> {
    return this.http.get<Conversation>(`${this.apiUrl}/${conversationId}`);
  }

  postConversation(conversationId: string, conversation: Message[]): Observable<Conversation> {
    return this.http.post<Conversation>(`${this.apiUrl}/${conversationId}`, { conversation });
  }
}
