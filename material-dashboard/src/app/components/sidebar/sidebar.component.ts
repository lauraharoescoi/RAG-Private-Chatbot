import { Component, OnInit } from '@angular/core';
import { ConversationService } from '../../services/conversation.service';
import { ChatService } from '../../services/chat.service';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

declare const $: any;
declare interface RouteInfo {
    path: string;
    title: string;
    icon: string;
    class: string;
    dropdown: boolean;
}
export const ROUTES: RouteInfo[] = [
    { path: '/chat', title: 'Chat', icon: 'chat', class: '', dropdown: true },
    { path: '/upload', title: 'Upload', icon: 'upload', class: '', dropdown: false },
    { path: '/configuration', title: 'Configuration', icon: 'settings', class: '', dropdown: false }
];

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {
  menuItems: any[];
  conversationIds: string[] = [];
  selectedConversationId: string | null = null;
  isChatRoute: boolean = false;
  showConversations: boolean = false; // Inicializar correctamente

  constructor(private conversationService: ConversationService, private chatService: ChatService, private router: Router) { 
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      this.isChatRoute = event.urlAfterRedirects.startsWith('/chat');
      if (this.isChatRoute) {
        this.fetchConversationIds();
        this.selectedConversationId = localStorage.getItem('conversationId');
      }
    });
  }

  ngOnInit() {
    this.menuItems = ROUTES.filter(menuItem => menuItem);
  }

  clickSubBtn(evnt, classname, classname2) {
    $(evnt.currentTarget).next('.' + classname).slideToggle();
    $(evnt.currentTarget).find('.' + classname2).toggleClass('rotate');
  }
  

  fetchConversationIds() {
    this.conversationService.getConversationIds().subscribe(ids => {
      this.conversationIds = ids;
    });
  }

  toggleConversations() {
    this.showConversations = !this.showConversations;
  }

  createNewConversation() {
    localStorage.removeItem('conversationId');
    this.selectedConversationId = this.generateConversationId();
    localStorage.setItem('conversationId', this.selectedConversationId);
    window.location.reload();
  }

  generateConversationId(): string {
    return '_' + Math.random().toString(36).slice(2, 11);
  }

  selectConversation(id: string) {
    this.selectedConversationId = id;
    this.chatService.selectConversation(id);
    localStorage.setItem('conversationId', id);
  }

  isMobileMenu() {
    return $(window).width() <= 991;
  }
}
