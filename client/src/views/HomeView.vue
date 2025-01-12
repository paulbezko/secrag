<template>
  <div class="flex-column center width-100 height-100svh" id="dashboard">
    <div class="flex-column center space-between width-100 height-100svh" style="max-width: 80rem; ">

      <!-- Header -->
      <div style="min-height: 1rem;" class="width-100 header" id="header"></div>

      <div class="flex-column width-100 height-100 center">

        <!-- Chat container section -->
        <div v-if="view === 'chat'" class="flex-column width-100 gap-2 no-scrollbar chat-container" id="chatContainer" style="overflow-y: auto;" :style="{ 'max-height': `${chatContainerHeight}px` }">
          <div v-for="(message, index) in chat" :key="index" class="flex-row center gap-1 width-100 chat-message">

            <!-- Assistant message -->
            <div v-if="message.role === 'assistant'" class="flex-row center gap-1 row-to-column" :class="chat.length === 1 ? 'assistant-message single' : 'assistant-message'">
              <img
                v-if="isLatestAssistantMessage(message)" 
                :src="input !== '' 
                  ? require('@/assets/dashboard/face_with_monocle_3d.png')
                  : (responseIsProcessing
                    ? require('@/assets/dashboard/thinking_face_3d.png')
                    : require('@/assets/dashboard/slightly_smiling_face_3d.png'))"
                class="assistant-image"
              >
              <img v-if="!isLatestAssistantMessage(message)" :src="require('@/assets/dashboard/relieved_face_3d.png')" class="assistant-image assistant-image-past">
              <div v-if="isLatestAssistantMessage(message) && responseFlowstep !== ''" class="chat-text assistant-text assistant-text-flowstep">{{ responseFlowstep }}</div>
              <div class="chat-text" :class="chat.length === 1 ? 'assistant-text single' : 'assistant-text'" v-html="markdownify(message.content)"></div>
            </div>

            <div v-else-if="message.role === 'widget'" class="widget-container">
              <div v-if="message.content.type === 'treemap'">
                <ApexChartsWidget :params="message.content.params" :theme="theme" />
              </div>
              <div v-else-if="message.content.type === 'tradingview'">
                <TradingViewWidget :ticker="message.content.ticker" :theme="theme" />
              </div>
            </div>

            <!-- User message -->
            <div v-else class="flex-row center gap-1 width-100 user-message">
              <div class="chat-text" v-html="markdownify(message.content)"></div>
            </div>

          </div>
        </div>

        <!-- Profile container section -->
        <div v-if="view === 'profile'" class="flex-column width-100 gap-1 center" style="padding-inline: 1rem">
          <div class="flex-row center gap-1 assistant-message single" style="height: 4rem">
            <img
              :src="input !== '' 
                ? require('@/assets/dashboard/face_with_monocle_3d.png')
                : require('@/assets/dashboard/slightly_smiling_face_3d.png')"
              class="assistant-image"
            >
            <div v-if="userProfileUpdated === false" class="chat-text assistant-text single" v-html="markdownify('This is what I know about you.<br>Feel free to adjust!')"></div>
            <div v-else class="chat-text assistant-text single" v-html="markdownify('Thanks for correcting!<br>Your profile has been updated successfully.')"></div>
          </div>
          <div 
            ref="profileDiv"
            class="input-profile" 
            contenteditable="true" 
            :innerHTML="markdownify(userProfile)"
          ></div>
        </div>

      </div>

      <!-- Footer -->
      <div style="padding-block: 1rem;" class="width-100 footer" id="footer">

        <!-- Input section -->
        <div class="flex-column center gap-1 width-100" style="max-width: 80rem; padding-inline: 1rem;">

          <!-- Suggestion section -->
          <div class="flex-row center gap-1 width-100" style="justify-content: space-between; padding-left: 1rem;" :class="{ 'input-suggestion-disabled': responseIsProcessing }">
            
            <!-- Organic suggestions -->
            <div v-if="premadeSuggestionsShown && isMobile"></div>
            <div class="flex-row center" v-if="!premadeSuggestionsShown && isMobile || !isMobile" :class="isMobile ? 'gap-1' : 'gap-15'">
              <div v-for="(prompt, index) in organicSuggestions" :key="index" class="input-suggestion" @click="sendMessage(prompt)">{{ prompt }}</div>
              <div class="input-suggestion" v-if="inputMode === 'login' || inputMode === 'signup_email'" @click="switchToDefaultInput()">Go back</div>
            </div>

            <!-- Premade suggestions -->
            <div class="flex-row gap-2" style="justify-content: right;">
              <div class="flex-row center" v-if="premadeSuggestionsShown" :class="isMobile ? 'gap-1' : 'gap-15'">
                <div class="input-suggestion" v-for="(suggestion, index) in premadeSuggestions" :key="index" @click="suggestion.action">
                  {{ suggestion.label }}
                </div>
              </div>
              <div 
                v-if="isMobile && userStatus !== 'verified' && inputMode !== 'reset_password'" 
                class="icon fa-solid fa-ellipsis" 
                style="width: 4rem; text-align: center; font-size: 1.6rem; cursor: pointer;" 
                @click="togglePremadeSuggestionsVisibility()"
                >
              </div>
              <div v-else style="width: 4rem;"></div>
            </div>
          </div>

          <!-- Inputbox section -->
          <div class="flex-row center gap-1 width-100">

            <!-- Default input -->
            <div class="flex-row center gap-1 width-100" v-if="inputMode === 'default'" style="align-items: end;">
              <textarea
                class="input-chat" 
                :class="{ 'input-chat-disabled': responseIsProcessing || view !== 'chat' }"
                v-model="input" 
                type="text" 
                rows="1"
                id="textarea"
                placeholder="Ask me anything"
                @keydown.enter.exact.prevent 
                @keyup.enter.exact="sendMessage(input)"
                @input="updateTextareaHeight()"
              ></textarea>
              <div class="button-send" :class="{ 'button-send-disabled': view !== 'chat' }" v-if="!responseIsProcessing" @click="sendMessage(input)">
                <div class="icon fa-solid fa-arrow-up"></div>
              </div>
              <div class="button-send" v-else @click="stopResponse()">
                <div class="icon fa-solid fa-square"></div>
              </div>
            </div>

            <!-- Signup Email input -->
            <div class="flex-row center gap-1 width-100" v-if="inputMode === 'signup_email'">
              <input 
                class="input-chat input-chat-highlighted" 
                :class="{ 'input-chat-disabled': responseIsProcessing }"
                v-model="inputEmail" 
                type="email" 
                placeholder="Email"
                @keydown.enter.exact.prevent 
                @keyup.enter.exact="signupEmail(inputEmail)"
              >
              <div class="flex-row center gap-1">
                <div class="button-send" :class="{ 'input-chat-disabled': responseIsProcessing }" @click="authenticateWithGoogle()">
                  <div class="icon fa-brands fa-google"></div>
                </div>
                <div class="button-send" v-if="!responseIsProcessing" @click="signupEmail(inputEmail)">
                  <div class="icon fa-solid fa-arrow-up"></div>
                </div>
                <div class="button-send" v-else @click="stopResponse()">
                  <div class="icon fa-solid fa-square"></div>
                </div>
              </div>
            </div>

            <!-- Signup Password input -->
            <div class="flex-row gap-1 width-100" style="align-items: end;" v-if="inputMode === 'signup_password'">
              <div class="flex-row row-to-column center gap-1 width-100">
                <input 
                  class="input-chat input-chat-highlighted"
                  :class="{ 'input-chat-disabled': responseIsProcessing }"
                  v-model="inputPassword" 
                  type="password"
                  placeholder="Password"
                  @keydown.enter.exact.prevent 
                >
                <input 
                  class="input-chat input-chat-highlighted"
                  :class="{ 'input-chat-disabled': responseIsProcessing }"
                  v-model="inputPasswordConfirm" 
                  type="password" 
                  placeholder="Confirm Password"
                  @keydown.enter.exact.prevent 
                  @keyup.enter.exact="signupPassword(inputPassword, inputPasswordConfirm)"
                >
              </div>
              <div class="flex-row row-to-column center gap-1">
                <div class="button-send" v-if="!responseIsProcessing" @click="signupPassword(inputPassword, inputPasswordConfirm)">
                  <div class="icon fa-solid fa-arrow-up"></div>
                </div>
                <div class="button-send" v-else @click="stopResponse()">
                  <div class="icon fa-solid fa-square"></div>
                </div>
              </div>
            </div>

            <!-- Sign in input -->
            <div class="flex-row gap-1 width-100" style="align-items: end;" v-if="inputMode === 'login'">
              <div class="flex-row row-to-column center gap-1 width-100">
                <input 
                  class="input-chat input-chat-highlighted"
                  :class="{ 'input-chat-disabled': responseIsProcessing }"
                  v-model="inputEmail" 
                  type="email" 
                  placeholder="Your Email"
                  @keydown.enter.exact.prevent
                >
                <input 
                  class="input-chat input-chat-highlighted"
                  :class="{ 'input-chat-disabled': responseIsProcessing }"
                  v-model="inputPassword" 
                  type="password" 
                  placeholder="Your Password"
                  @keydown.enter.exact.prevent 
                  @keyup.enter.exact="login(inputEmail, inputPassword)"
                >
              </div>
              <div class="flex-row row-to-column center gap-1">
                <div class="button-send" :class="{ 'input-chat-disabled': responseIsProcessing }" @click="authenticateWithGoogle()">
                  <div class="icon fa-brands fa-google"></div>
                </div>
                <div class="button-send" v-if="!responseIsProcessing" @click="login(inputEmail, inputPassword)">
                  <div class="icon fa-solid fa-arrow-up"></div>
                </div>
                <div class="button-send" v-else @click="stopResponse()">
                  <div class="icon fa-solid fa-square"></div>
                </div>
              </div>
            </div>

            <!-- Forgot password input -->
            <div class="flex-row gap-1 width-100" style="align-items: end;" v-if="inputMode === 'forgot_password'">
              <div class="flex-row row-to-column center gap-1 width-100">
                <input 
                  class="input-chat input-chat-highlighted"
                  :class="{ 'input-chat-disabled': responseIsProcessing }"
                  v-model="inputEmail" 
                  type="email" 
                  placeholder="Your Email"
                  @keydown.enter.exact.prevent 
                  @keyup.enter.exact="forgotPassword(inputEmail)"
                >
              </div>
              <div class="button-send" v-if="!responseIsProcessing" @click="forgotPassword(inputEmail)">
                <div class="icon fa-solid fa-arrow-up"></div>
              </div>
              <div class="button-send" v-else @click="stopResponse()">
                <div class="icon fa-solid fa-square"></div>
              </div>
            </div>

            <!-- Reset password input -->
            <div class="flex-row gap-1 width-100" style="align-items: end;" v-if="inputMode === 'reset_password'">
              <div class="flex-row row-to-column center gap-1 width-100">
                <input 
                  class="input-chat input-chat-highlighted"
                  :class="{ 'input-chat-disabled': responseIsProcessing }"
                  v-model="inputPassword" 
                  type="password"
                  placeholder="Password"
                  @keydown.enter.exact.prevent 
                >
                <input 
                  class="input-chat input-chat-highlighted"
                  :class="{ 'input-chat-disabled': responseIsProcessing }"
                  v-model="inputPasswordConfirm" 
                  type="password" 
                  placeholder="Confirm Password"
                  @keydown.enter.exact.prevent 
                  @keyup.enter.exact="signupPassword(inputPassword, inputPasswordConfirm)"
                >
              </div>
              <div class="button-send" v-if="!responseIsProcessing" @click="resetPassword(inputPassword, inputPasswordConfirm)">
                <div class="icon fa-solid fa-arrow-up"></div>
              </div>
              <div class="button-send" v-else @click="stopResponse()">
                <div class="icon fa-solid fa-square"></div>
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { createClient } from '@supabase/supabase-js'
import { marked } from 'marked';
import { socket } from "@/socket";
import { config } from '@/config';
import webdata from '../webdata.json'
import axios from 'axios';
import TurndownService from 'turndown';

import TradingViewWidget from '@/components/TradingViewWidget.vue'
import ApexChartsWidget from '@/components/ApexChartsWidget.vue';

export default {
  components: {
    TradingViewWidget,
    ApexChartsWidget
  },
  data() {
    return {
      isMobile: window.innerWidth <= 796,
      socketId: null,
      theme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
      userStatus: null,
      userProfile: '',
      userProfileUpdated: false,
      view: 'chat',
      input: '',
      inputMode: 'default',
      inputEmail: '',
      inputPassword: '',
      inputPasswordConfirm: '',
      chatContainerHeight: null,
      chat: [],
      organicSuggestions: [],
      premadeSuggestions: [],
      premadeSuggestionsShown: false,
      premadeSuggsetionsTopic: '',
      responseIsProcessing: false,
      responseIsSaved: true,
      responseFlowstep: '',
      currentAssistantMessage: '',
    };
  },
  mounted() {
    const promises = [];
    this.initializeSocket();
    if (!this.isMobile) {this.premadeSuggestionsShown = true;}

    const urlToken = new URLSearchParams(window.location.search).get("token");
    if (urlToken) {promises.push(this.processUrlToken(urlToken))}

    const hashParams = new URLSearchParams(window.location.hash.slice(1));
    const urlSupabaseAccessToken = hashParams.get('access_token');
    const urlSupabaseRefreshToken = hashParams.get('refresh_token');
    if (urlSupabaseAccessToken && urlSupabaseRefreshToken) {promises.push(this.HandleSupabaseAuth(urlSupabaseAccessToken, urlSupabaseRefreshToken))} 
    
    else if (localStorage.getItem('_q')) {
      this.chat = [{ role: 'assistant', content: '' }];
      this.sendManualAssistantMessage(localStorage.getItem('_q'));
      localStorage.removeItem('_q');
    } 

    else if (localStorage.getItem('_u')) {
      const token = localStorage.getItem('_u');
      promises.push(
        this.getChatHistory(token),
        this.getUserData(token).then(() => {
          if (this.userStatus === 'anonymous') {
            this.sendManualAssistantMessage("Welcome back!");
            this.organicSuggestions = ['Tell me more'];
          } else if (this.userStatus === 'verified') {
            this.chat = [{ role: 'assistant', content: '' }];
            this.sendManualAssistantMessage("Your email has been confirmed!<br>Let's set up your password now.");
            this.inputMode = 'signup_password';
            this.premadeSuggestionsShown = true;
          } else if (this.userStatus === 'registered') {
            this.chat = [{ role: 'assistant', content: '' }];
            this.sendManualAssistantMessage("Welcome back!");
            this.organicSuggestions = ['Tell me more'];
          }
        })
      )
    } 
    
    else {
      this.chat = [{ role: 'assistant', content: '' }];
      this.sendManualAssistantMessage('Welcome to **SECRAG**.<br>We make security analysis easier.');
      this.organicSuggestions = ['How exactly?', 'Show me an example'];
    }

    Promise.all(promises).finally(() => {
      this.chatScrollToBottom();
      this.updateChatHeight();
      this.updateTextareaHeight();
      this.observeSize();
      this.getPremadeSuggestions();
    });
  },

  beforeUnmount() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
  },

  methods: {

    // SOCKET HANDLING
    initializeSocket() {
      socket.connect();
      socket.on("connect", () => {
        (this.socketId = socket.id)
      });
      socket.on("response_started", () => {
        this.responseIsProcessing = true; 
        this.responseIsSaved = false; 
        this.responseFlowstep = 'Thinking...'; 
        this.chat.push({ role: "assistant", content: "" })
      });
      socket.on("response_token", (data) => {
        this.processResponse(data.word), 
        this.responseFlowstep = ''
      });
      socket.on("response_complete", () => {
        this.responseIsProcessing = false;
        this.saveAssitantResponse();
        this.responseIsSaved = true; 
        const textarea = document.getElementById('textarea');
        if (textarea) textarea.focus();
      });
      socket.on("tool", (data) => {
        this.processTool(data)
      });
      socket.on("flowstep", (data) => {
        this.responseFlowstep = data.flowstep
      });
      socket.on("widget", (data) => {
        this.processWidget(data)
      });
      socket.on("suggestions", (data) => {
        this.processOrganicSuggestions(data.suggestions)
      });
    },

    // SESSION HANDLING
    async initializeAnonToken() {
      const result = await axios.get(`${config.apiUrl}/api/init-anon-user`);
      localStorage.setItem('_u', result.data.token);
      this.userStatus = 0
    },

    async processUrlToken(token) {

      this.chat = [{ role: 'assistant', content: '' }]
      const result = await axios.get(`${config.apiUrl}/api/process-url-token?token=` + token);
      if (result.data.error) {
        localStorage.setItem('_q', result.data.error);
        window.location.href = '/'
      }
      else {
        if (result.data.action === 'confirm_email') {
          window.location.href = '/'
          this.inputMode = 'signup_password'
          this.sendManualAssistantMessage("Your email has been confirmed!<br>Let's set up your password now.")
        }
        if (result.data.action === 'reset_password') {
          this.sendManualAssistantMessage('You can now enter your new password.')
        }
        this.inputMode = result.data.input_mode;
      }
    },

    async getUserData(token) {
      const response = await axios.get(`${config.apiUrl}/api/get-user-data?token=` + token);
      if (response.data.critical) {
        localStorage.removeItem('_u');
        window.location.reload()
      }
      else (this.userStatus = response.data.user_status)
    },

    async getChatHistory(token) {
      const result = await axios.get(`${config.apiUrl}/api/get-chat-history?token=` + token);
      this.chat = result.data.chat.messages;
    },

    async getUserProfile(token) {
      const result = await axios.get(`${config.apiUrl}/api/get-user-profile?token=` + token);
      this.userProfile = result.data.profile
    },

    async updateUserProfile() {
      const userProfileHTML = this.$refs.profileDiv.innerHTML;
      const turndownService = new TurndownService();
      const userProfileMarkdown = turndownService.turndown(userProfileHTML);
      
      const result = await axios.post(`${config.apiUrl}/api/update-user-profile`, {token: localStorage.getItem('_u'), profile: userProfileMarkdown, socketId: this.socketId});
      if (result.data.error) {console.log(result.data.error)}
      else {this.userProfileUpdated = true; this.userProfile = userProfileMarkdown}
    },

    // UI HELPERS
    observeSize() {
      this.resizeObserver = new ResizeObserver(() => {
        requestAnimationFrame(() => {
          this.updateChatHeight();
          this.checkScreenWidth();
        });
      });
      const dashboard = document.getElementById('dashboard');
      this.resizeObserver.observe(dashboard);
    },

    markdownify(text) {
      if (typeof text !== 'string') {return '';}
      return marked(text, { breaks: false });
    },

    togglePremadeSuggestionsVisibility() {
      this.premadeSuggestionsShown = !this.premadeSuggestionsShown;
    },

    updateChatHeight() {
      const headerHeight = document.getElementById('header').offsetHeight;
      const footerHeight = document.getElementById('footer').offsetHeight;
      this.chatContainerHeight = window.innerHeight - footerHeight - headerHeight;
    },

    checkScreenWidth() {
      if (window.innerWidth <= 796) {this.isMobile = true; this.premadeSuggestionsShown = false} 
      else {this.isMobile = false; this.premadeSuggestionsShown = true}
    },

    chatScrollToBottom() {
      const chatContainer = document.getElementById('chatContainer');
      chatContainer.scrollTo({top: chatContainer.scrollHeight, behavior: 'smooth'});
    },

    updateTextareaHeight() {
      const textarea = document.getElementById('textarea');
      if (!textarea) return;
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
      this.updateChatHeight();
    },

    isLatestAssistantMessage(message) {
      const assistantMessages = this.chat.filter(msg => msg.role === 'assistant');
      return assistantMessages.length > 0 && assistantMessages[assistantMessages.length - 1] === message;
    },

    // CHAT INTERACTION
    getPremadeSuggestions() {
      if (this.view === 'profile') {
        this.inputMode = 'default';
        this.userProfileUpdated = false;
        this.organicSuggestions = [];
        this.premadeSuggestionsShown = true;
        this.premadeSuggestions = [
          { label: 'Save changes', action: () => (this.updateUserProfile()) },
          { label: 'Back', action: () => (this.view = 'chat', this.getPremadeSuggestions(), this.$nextTick(() => {setTimeout(() => {this.chatScrollToBottom();}, 100)})) },
        ];
      }
      
      else if (this.premadeSuggsetionsTopic === 'profile') {
        this.premadeSuggestions =  [
        ...(!this.userIsSubscribed ? [] : [{ label: 'Manage Subscription', action: () => console.log('Redirect to stripe here') }]),
          { label: 'Sign Out', action: this.signOut },
          { label: 'More', action: () => (this.premadeSuggsetionsTopic = 'more_authenticated', this.getPremadeSuggestions()) },
          { label: 'Back', action: () => (this.premadeSuggsetionsTopic = '', this.getPremadeSuggestions()) },
        ]
      }

      else if (this.premadeSuggsetionsTopic === 'more_authenticated') {
        this.premadeSuggestions =  [
          { label: 'Delete Account', action: () => console.log('DELETE ACCOUNT') },
          { label: 'Back', action: () => (this.premadeSuggsetionsTopic = 'profile', this.getPremadeSuggestions()) },
        ];
      }

      else if (this.premadeSuggsetionsTopic === 'more_anonymous') {
        this.premadeSuggestions =  [
        { label: 'Pricing', action: () => this.sendMessage("I'd like to know more about the pricing") },
        { label: 'Contact', action: () => this.sendMessage("I'd like to contact you") },
        { label: 'T&C', action: () => this.$router.push('/terms-and-conditions') },
        { label: 'Back', action: () => (this.premadeSuggsetionsTopic = '', this.getPremadeSuggestions()) },
        ];
      }

      else if (this.userStatus === 'anonymous' || this.userStatus === null) {
        this.premadeSuggestions =  [
          { label: 'Profile', action: async () => (await this.getUserProfile(localStorage.getItem('_u')), this.view = 'profile', this.getPremadeSuggestions()) },
          { label: 'Sign Up', action: () => this.sendMessage("I'd like to sign up") },
          { label: 'Sign In', action: () => this.sendMessage("I'd like to sign in") },
          { label: 'More', action: () => (this.premadeSuggsetionsTopic = 'more_anonymous', this.getPremadeSuggestions()) },
        ];
      }

      else if (this.userStatus === 'verified') {
        this.premadeSuggestions =  [];
      }

      else if (this.userStatus === 'registered') {
        this.premadeSuggestions =  [
          { label: 'Subscribe', action: () => console.log('Redirect to stripe here') },
          // { label: 'Profile', action: () => (this.premadeSuggsetionsTopic = 'profile', this.getPremadeSuggestions()) },
          { label: 'Profile', action: async () => (await this.getUserProfile(localStorage.getItem('_u')), this.view = 'profile', this.getPremadeSuggestions()) },
        ];
      }

      else {
        this.premadeSuggestions =  [
        ];
      }
    },

    async sendMessage(input) {
      if (input === '') return;
      if (this.responseIsProcessing) {await this.stopResponse()}
      const textarea = document.getElementById('textarea');
      if (textarea) textarea.blur();

      if (!localStorage.getItem('_u')) {
        await this.initializeAnonToken()
        await axios.post(`${config.apiUrl}/api/new-chat`, {token: localStorage.getItem('_u'), chat: 'general'});
      }

      this.chat.push({role: 'user', content: input});
      this.$nextTick(() => {this.chatScrollToBottom(); this.updateTextareaHeight()});
      this.input = '';

      await axios.post(`${config.apiUrl}/api/new-message`, {token: localStorage.getItem('_u'), role: 'user', input: input, socketId: this.socketId});
    },

    processTool(data) {
      this.responseFlowstep = data.flowstep;
      if (data.name === "tool_signup_email") {this.inputMode = 'signup_email'} 
      else if (data.name === "tool_login") {this.inputMode = 'login'} 
      else if (data.name === "tool_forgot_password") {this.inputMode = 'forgot_password'}
      else if (data.name === "tool_reset_password") {this.inputMode = 'reset_password'}

      else if (data.name === "tool_signed_in") {
        localStorage.setItem('_u', data.token)
        this.userIsAuthenticated = true
        if (data.subscription !== 'none') {this.userIsSubscribed = true}
        this.inputMode = 'default'
        const lastAssistantMessage = this.chat.slice().reverse().find((message) => message.role === 'assistant');
        this.chat = lastAssistantMessage ? [lastAssistantMessage] : [];
        this.getPremadeSuggestions();
      }

      else {this.inputMode = 'default'}

      if ((data.name === "tool_login" || data.name === "tool_signup_email") && this.isMobile === true) {this.premadeSuggestionsShown = false}
      this.$nextTick(() => {this.updateChatHeight()});
    },

    async processWidget(data) {
      console.log(data);
      let widgetMetadata = data.metadata;
      if (typeof data.metadata === 'string') {
        widgetMetadata = JSON.parse(data.metadata);
      }

      const processAfterResponse = async () => {
        this.chat.push({ role: 'widget', content: widgetMetadata });

        this.$nextTick(() => {
          setTimeout(() => {
            this.chatScrollToBottom();
          }, 100);
        });

        if (this.responseIsSaved) {
          try {
            await axios.post(`${config.apiUrl}/api/new-message`, {
              token: localStorage.getItem('_u'),
              role: 'widget',
              input: widgetMetadata,
              socketId: this.socketId,
            });
          } catch (error) {
            console.error("Error sending message:", error);
          }
        }
      };

      if (this.responseIsProcessing) {
        const checkResponseComplete = () => {
          if (!this.responseIsProcessing) {
            processAfterResponse();
          } else {
            setTimeout(checkResponseComplete, 50);
          }
        };
        checkResponseComplete();
      } else {
        processAfterResponse();
      }
    },


    switchToDefaultInput() {
      this.inputMode = 'default';
      this.organicSuggestions = ['Tell me more'];
      this.$nextTick(() => {this.updateChatHeight()});
    },

    processOrganicSuggestions(organicSuggestions) {
      this.organicSuggestions = organicSuggestions;
    },

    processResponse(word) {
      const newMessageIndex = this.chat.length - 1;
      const currentMessage = this.chat[newMessageIndex];
      if (currentMessage && currentMessage.role === 'assistant') {
        currentMessage.content += word
      }

      this.$forceUpdate();
      this.$nextTick(() => {this.chatScrollToBottom()});
    },

    async stopResponse() {
      return new Promise((resolve) => {
        socket.emit("stop_llm_stream");
        setTimeout(() => {this.currentAssistantMessage = ''; resolve()}, 100);
      });
    },

    sendManualAssistantMessage(message) {
      const words = message.match(/\S+|\s+/g); 
      words.forEach((part, index) => {
        setTimeout(() => { 
          this.processResponse(part); 
        }, index * 20);
      });
    },

    async saveAssitantResponse() {
      await axios.post(`${config.apiUrl}/api/new-message`, {token: localStorage.getItem('_u'), role: 'assistant', input: this.chat[this.chat.length - 1].content, socketId: this.socketId});
    },

    // AUTHENTICATION
    async signupEmail(email) {
      this.responseIsProcessing = true;

      if (email === '') {this.sendManualAssistantMessage("<br>Please provide your email address.")}
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {this.sendManualAssistantMessage("<br>Please provide a valid email address.")}
      else {
        const response = await axios.post(`${config.apiUrl}/api/signup-email`, {token: localStorage.getItem('_u'), email: email, socketId: this.socketId});
        if (response.data.error) {this.sendManualAssistantMessage('<br>' + response.data.error)}
        else {this.sendManualAssistantMessage('<br><b>Success!</b> An email has been sent.'); this.inputMode = 'default'}
      }
      this.inputEmail = '';
      this.responseIsProcessing = false;
    },

    async signupPassword(password, passwordConfirm) {
      this.responseIsProcessing = true;

      const passwordStrengthRegex = /^(?=.*\d)(?=.*[!@#$%^&*:;_\-.])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
      if (password === '' || passwordConfirm === '') {this.sendManualAssistantMessage("<br>Please provide your password.")}
      else if (password !== passwordConfirm) {this.sendManualAssistantMessage("<br>Passwords do not match.")}
      else if (!passwordStrengthRegex.test(password)) {this.sendManualAssistantMessage("<br>This password is not strong enough. Try a different one.")}
      else {
        const response = await axios.post(`${config.apiUrl}/api/signup-password`, {token: localStorage.getItem('_u'), password: password, socketId: this.socketId});
        if (response.data.error) {this.sendManualAssistantMessage('<br>' + response.data.error)}
        else {
          this.chat = [{ role: 'assistant', content: '' }];
          this.sendManualAssistantMessage('Success! Now you can login anytime you want.'); 
          this.userStatus = 'registered'; 
          this.inputMode = 'default'
          this.getPremadeSuggestions()
        }
      }

      this.inputPassword = '';
      this.inputPasswordConfirm = '';
      this.responseIsProcessing = false;
    },

    async login(email, password) {
      this.inputEmail = '';
      this.inputPassword = '';
      const response = await axios.post(`${config.apiUrl}/api/login`, {token: localStorage.getItem('_u'), email: email, password: password});
      if (response.data.error) {this.sendManualAssistantMessage(response.data.error)}
      else {
        this.userStatus = response.data.user_status; 
        this.inputMode = 'default';
        this.getPremadeSuggestions()
        this.organicSuggestions = ['Tell me more']
        this.chat = [{ role: 'assistant', content: '' }];
        this.sendManualAssistantMessage('Welcome back!');
        localStorage.setItem('_u', response.data.token);
      }
    },

    async authenticateWithGoogle() {
      const SUPABASE_KEY = webdata.supabaseKey
      const SUPABASE_URL = webdata.supabaseURL
      const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
      await supabase.auth.signInWithOAuth({provider: 'google', "options": {"redirectTo": `${config.webUrl}/`}})
    },

    async HandleSupabaseAuth(urlSupabaseAccessToken, urlSupabaseRefreshToken) {
      const SUPABASE_KEY = webdata.supabaseKey
      const SUPABASE_URL = webdata.supabaseURL
      const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
      await supabase.auth.setSession({access_token: urlSupabaseAccessToken, refresh_token: urlSupabaseRefreshToken,})
      const { data } = await supabase.auth.getSession()
      const response = await axios.post(`${config.apiUrl}/api/authenticate-with-supabase`, {
        token: localStorage.getItem('_u'),
        supabase_user_id: data.session.user.id,
        email: data.session.user.email, 
        name: data.session.user.user_metadata.full_name, 
        auth_type: data.session.user.app_metadata.provider
      })
      if (response.data.error) {
        this.chat=[{ role: 'assistant', content: '' }];
        this.sendManualAssistantMessage(response.data.error);
      }
      else {
        this.userStatus = response.data.user_status; 
        this.inputMode = 'default';
        this.getPremadeSuggestions()
        this.organicSuggestions = ['Tell me more']
        this.chat = [{ role: 'assistant', content: '' }];
        this.sendManualAssistantMessage('Welcome back!');
        localStorage.setItem('_u', response.data.token);
      }
    },

    async forgotPassword(email) {
      this.responseIsProcessing = true;
      const response = await axios.post(`${config.apiUrl}/api/forgot-password`, {email: email, socketId: this.socketId});
      if (response.data.error) {this.sendManualAssistantMessage(response.data.error)}
      else {
        this.inputMode = 'default';
        this.sendManualAssistantMessage('<br>Success! An email with a password reset link has been sent.');
      }
      this.inputEmail = '';
      this.responseIsProcessing = false;
    },

    async resetPassword(password, passwordConfirm) {
      this.responseIsProcessing = true;

      const passwordStrengthRegex = /^(?=.*\d)(?=.*[!@#$%^&*:;_\-.])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
      if (password === '' || passwordConfirm === '') {this.sendManualAssistantMessage("<br>Please provide your new password.")}
      else if (password !== passwordConfirm) {this.sendManualAssistantMessage("<br>Passwords do not match.")}
      else if (!passwordStrengthRegex.test(password)) {this.sendManualAssistantMessage("<br>This password is not strong enough. Try a different one.")}
      else {
        const urlToken = new URLSearchParams(window.location.search).get("token");
        const response = await axios.post(`${config.apiUrl}/api/reset-password`, {token: urlToken, password: password});
        if (response.data.error) {this.sendManualAssistantMessage(response.data.error)}
        else {
          localStorage.setItem('_q', 'Success! You can now login with your new password.');
          localStorage.removeItem('_u');
          window.location.href = '/'
        }
      }
      this.inputPassword = '';
      this.inputPasswordConfirm = '';
      this.responseIsProcessing = false;
    },

    signOut() {
      localStorage.removeItem('_u');
      window.location.reload()
    },

  }
};
</script>