import { marked } from 'marked';
import { config } from '@/config';
import axios from 'axios';

import { interfacing } from './interfacing.js';

export const messaging = {
  markdownify(text) {
    if (typeof text !== 'string') {return '';}
    return marked(text, { breaks: false });
  },

  async sendMessage(ctx, input) {
    if (input === '') return;
    if (ctx.responseIsProcessing) {await ctx.stopResponse()}
    const textarea = document.getElementById('textarea');
    if (textarea) textarea.blur();

    if (!localStorage.getItem('_u')) {
      await ctx.initializeAnonToken()
      await axios.post(`${config.apiUrl}/api/new-chat`, {token: localStorage.getItem('_u'), chat: 'general'});
    }

    ctx.chat.push({role: 'user', content: input});
    ctx.$nextTick(() => {interfacing.chatScrollToBottom(); interfacing.updateTextareaHeight(ctx)});
    ctx.input = '';

    await axios.post(`${config.apiUrl}/api/new-message`, {
      token: localStorage.getItem('_u'), 
      role: 'user', 
      input: input, 
      widgets: null,
      socketId: ctx.socketId
    });
  },

  processResponse(ctx, word) {
    const newMessageIndex = ctx.chat.length - 1;
    const currentMessage = ctx.chat[newMessageIndex];
    if (currentMessage && currentMessage.role === 'assistant') {
      currentMessage.content += word
    }

    ctx.$forceUpdate();
    ctx.$nextTick(() => {interfacing.chatScrollToBottom()});
  },

  async processWidget(ctx, data) {
    const lastMessage = ctx.chat[ctx.chat.length - 1];
    if (!Array.isArray(lastMessage.widgets)) {lastMessage.widgets = [];}
    const widgetData = typeof data.metadata === "string" ? JSON.parse(data.metadata) : data.metadata;
    lastMessage.widgets.push(widgetData);
  },

  processTool(ctx, data) {
    ctx.responseFlowstep = data.flowstep;
    if (data.name && data.name.startsWith('layout_')) {
      if (data.name === "layout_signup_email") {ctx.inputMode = 'signup_email'} 
      else if (data.name === "layout_login") {ctx.inputMode = 'login'} 
      else if (data.name === "layout_forgot_password") {ctx.inputMode = 'forgot_password'}
      else if (data.name === "layout_reset_password") {ctx.inputMode = 'reset_password'}
  
      else if (data.name === "layout_signed_in") {
        localStorage.setItem('_u', data.token)
        ctx.userIsAuthenticated = true
        if (data.subscription !== 'none') {ctx.userIsSubscribed = true}
        ctx.inputMode = 'default'
        const lastAssistantMessage = ctx.chat.slice().reverse().find((message) => message.role === 'assistant');
        ctx.chat = lastAssistantMessage ? [lastAssistantMessage] : [];
        ctx.getPremadeSuggestions();
      }

      if ((data.name === "tool_login" || data.name === "tool_signup_email") && ctx.isMobile === true) {ctx.premadeSuggestionsShown = false}
    }

    else {ctx.inputMode = 'default'}
    ctx.$nextTick(() => {interfacing.updateChatHeight(ctx)});
  },

  sendManualAssistantMessage(ctx, message) {
    const words = message.match(/\S+|\s+/g); 
    words.forEach((word, index) => {
      setTimeout(() => { 
        this.processResponse(ctx, word); 
      }, index * 20);
    });
  },

  async stopResponse(ctx, socket) {
    return new Promise((resolve) => {
      socket.emit("stop_llm_stream");
      setTimeout(() => {ctx.currentAssistantMessage = ''; resolve()}, 100);
    });
  },

  async saveAssitantResponse(ctx) {
    const lastMessage = ctx.chat[ctx.chat.length - 1];

    await axios.post(`${config.apiUrl}/api/new-message`, {
      token: localStorage.getItem('_u'), 
      role: 'assistant', 
      input: lastMessage.content, 
      widgets: lastMessage.widgets || null,
      socketId: ctx.socketId
    });
  },
}