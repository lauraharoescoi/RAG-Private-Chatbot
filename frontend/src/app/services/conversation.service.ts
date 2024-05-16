// conversation.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Conversation, Message } from '../models';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  private apiUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  getConversation(conversationId: string): Observable<Conversation> {
    return this.http.get<Conversation>(`${this.apiUrl}/backend/${conversationId}`);
  }

  postConversation(conversationId: string, conversation: Message[]): Observable<Conversation> {
    return this.http.post<Conversation>(`${this.apiUrl}/backend/${conversationId}`, { conversation });
  }

  updateConversationName(conversationId: string, name: string): Observable<void> {
    return this.http.patch<void>(`${this.apiUrl}/name/${conversationId}`, { name });
  }

  getConversations(): Observable<{conversation_id: string, name: string}[]> {
    return this.http.get<{conversation_id: string, name: string}[]>(`${this.apiUrl}/conversations`);
  }

  uploadFile(file: File): Observable<HttpEvent<any>> {
    const formData: FormData = new FormData();
    formData.append('file', file, file.name); 

    const req = new HttpRequest('POST', `${this.apiUrl}/upload_files`, formData, {
      reportProgress: true,
      responseType: 'json'
    });

    return this.http.request(req);
  }
}