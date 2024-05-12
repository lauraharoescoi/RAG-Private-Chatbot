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
    this.conversation = [{ role: 'assistant', content: 'Hi, how can I help?' }]; 
  }

  generateConversationId(): string {
    const id = '_' + Math.random().toString(36).slice(2, 11);
    localStorage.setItem('conversationId', id);
    return id;
  }

  fetchConversation() {
    this.conversationService.getConversation(this.conversationId).subscribe((data: Conversation) => {
        if (data && data.conversation) {
            this.conversation = data.conversation;
        } else {
            console.log('No conversation data returned:', data);
            this.conversation = []; // Set to an empty array to avoid undefined errors
        }
    }, error => {
        console.error('Failed to fetch conversation:', error);
        this.conversation = []; // Set to an empty array to ensure the UI doesn't break
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

