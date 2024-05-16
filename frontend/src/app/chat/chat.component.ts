import { Component, OnInit } from '@angular/core';
import { ConversationService } from '../services/conversation.service';
import { ChatService } from '../services/chat.service';
import { Message, Conversation } from '../models';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit {
  conversation: Message[] = [];
  userMessage: string = '';
  isLoading: boolean = false;
  conversationId: string = '';
  conversationName: string = 'New chat';
  isEditingName: boolean = false;

  constructor(private conversationService: ConversationService, private chatService: ChatService) {}

  ngOnInit() {
    this.conversationId = localStorage.getItem('conversationId') || this.generateConversationId();
    this.fetchConversation();
    this.chatService.conversationSelected$.subscribe(id => {
      this.loadConversation(id);
    });
  }

  generateConversationId(): string {
    const id = '_' + Math.random().toString(36).slice(2, 11);
    localStorage.setItem('conversationId', id);
    return id;
  }

  fetchConversation() {
    this.conversationService.getConversation(this.conversationId).subscribe((data: Conversation) => {
      if (data && data.conversation) {
        this.conversationName = data.name || 'New chat';
        this.conversation = data.conversation
          .filter(msg => msg.role === 'user' || msg.role === 'assistant')
          .map(msg => {
            if (msg.role === 'assistant') {
              msg.content = msg.content.substring(msg.content.indexOf('\n') + 1);
            }
            return msg;
          });
      } else {
        this.conversation = [];
      }
    }, error => {
      this.conversation = [];
    });
  }

  handleNewSession() {
    localStorage.removeItem('conversationId');
    this.conversation = [];
    this.conversationId = this.generateConversationId();
    this.conversationName = 'New chat';
    this.fetchConversation();
  }

  async handleSubmit() {
    if (!this.userMessage.trim()) return;
    
    this.isLoading = true;
    const newMessage = { role: 'user', content: this.userMessage };
    const newConversation = [...this.conversation, newMessage];

    this.conversationService.postConversation(this.conversationId, newConversation).subscribe((data: Conversation) => {
      this.conversation = data.conversation;
      this.userMessage = '';
      this.isLoading = false;
    }, error => {
      this.isLoading = false;
    });
  }

  loadConversation(id: string) {
    this.conversationId = id;
    localStorage.setItem('conversationId', id);
    this.fetchConversation();
  }

  editName() {
    this.isEditingName = true;
  }

  saveName() {
    this.isEditingName = false;
    this.conversationService.updateConversationName(this.conversationId, this.conversationName).subscribe();
  }
}
