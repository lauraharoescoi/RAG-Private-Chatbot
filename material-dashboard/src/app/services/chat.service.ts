// chat.service.ts
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private conversationSelectedSubject = new Subject<string>();
  conversationSelected$ = this.conversationSelectedSubject.asObservable();

  selectConversation(conversationId: string) {
    this.conversationSelectedSubject.next(conversationId);
  }
}
