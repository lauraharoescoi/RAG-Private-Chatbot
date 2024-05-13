import { Component, OnInit } from '@angular/core';
import { ConversationService } from '../services/conversation.service';
import { Message, Conversation } from '../models';
import { RouterLink } from '@angular/router';

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

  constructor(private conversationService: ConversationService) {}

  ngOnInit() {
    this.conversationId = localStorage.getItem('conversationId') || this.generateConversationId();
    this.fetchConversation();
  }

  generateConversationId(): string {
    const id = '_' + Math.random().toString(36).slice(2, 11);
    localStorage.setItem('conversationId', id);
    return id;
  }

  fetchConversation() {
    this.conversationService.getConversation(this.conversationId).subscribe((data: Conversation) => {
      if (data && data.conversation) {
        this.conversation = data.conversation
          .filter(msg => msg.role === 'user' || msg.role === 'assistant')
          .map(msg => {
            console.log('msg', msg);
            if (msg.role === 'assistant') {
              msg.content = msg.content.substring(msg.content.indexOf('\n') + 1);
            }
            return msg;
          });
      } else {
        console.log('No conversation data returned:', data);
        this.conversation = [];
      }
    }, error => {
      console.error('Failed to fetch conversation:', error);
      this.conversation = [];
    });
  }

  handleNewSession() {
    localStorage.removeItem('conversationId');
    this.conversation = []; // Clear current conversation
    this.conversationId = this.generateConversationId();
    this.fetchConversation(); // Optional: Attempt to fetch a new conversation if needed
  }


  async handleSubmit() {
    console.log('converasation', this.conversation);
    this.isLoading = true;
    const newConversation = [...this.conversation, { role: 'user', content: this.userMessage }];
    
    this.conversationService.postConversation(this.conversationId, newConversation).subscribe((data: Conversation) => {
      this.conversation = data.conversation;
      this.userMessage = '';
      this.isLoading = false;
    }, error => {
      console.error('Error updating conversation:', error);
      this.isLoading = false;
    });
  }
  
}

