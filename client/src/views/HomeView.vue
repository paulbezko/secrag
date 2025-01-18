<template>
  <div class="flex-column center width-100 height-100svh" id="dashboard">
    
    <div v-if="!pageLoaded" class="page-loading-message flex-row center width-100 gap-1">
      <img :src="require('@/assets/dashboard/relieved_face_3d.png')" class="assistant-image"/>
      <div class="assistant-text-flowstep">Loading...</div>
    </div>

    <div :class="{ 'hidden': !pageLoaded }" class="flex-column center space-between width-100 height-100svh" style="max-width: 80rem; ">
      
      <!-- Header -->
      <div style="min-height: 1rem;" class="width-100 header" id="header"></div>
      <div class="flex-column width-100 height-100 center">

        <!-- Chat container section -->
        <ChatComp
          ref="chatComp"

          :input="input"
          :chat="chat"
          :chatFullyLoaded="chatFullyLoaded"
          :view="view"
          :responseIsProcessing="responseIsProcessing"
          :responseFlowstep="responseFlowstep"
          :theme="theme"
          :chatContainerHeight="chatContainerHeight"

          @get-x-more-messages="getXMoreMessages"
        />

        <!-- Profile container section -->
        <ProfileComp
          ref="profileComp"

          :input="input"
          :view="view"
          :userProfileUpdated="userProfileUpdated"
          :userProfile="userProfile"
        />

      </div>

      <!-- Footer -->
      <div style="padding-block: 1rem;" class="width-100 footer" id="footer">

        <!-- Input section -->
        <div class="flex-column center gap-1 width-100" style="max-width: 80rem; padding-inline: 1rem;">

          <!-- Suggestion section -->
          <SuggestionsComp 
            ref="suggestionsComp"

            :isMobile="isMobile"
            :userStatus="userStatus"
            :inputMode="inputMode"
            :organicSuggestions="organicSuggestions"
            :premadeSuggestions="premadeSuggestions"
            :premadeSuggestionsShown="premadeSuggestionsShown"
            :responseIsProcessing="responseIsProcessing"

            @send-message="sendMessage"
            @switch-to-default-input="switchToDefaultInput"
            @toggle-premade-suggestions-visibility="togglePremadeSuggestionsVisibility"
          />

          <!-- Inputbox section -->
          <InputComp
            ref="inputComp"

            :view="view"
            :inputMode="inputMode"
            :chatContainerHeight="chatContainerHeight"
            :responseIsProcessing="responseIsProcessing"
            :responseFlowstep="responseFlowstep"
            :theme="theme"

            @update-textarea-height="updateTextareaHeight"
            @send-message="sendMessage"
            @stop-response="stopResponse"
            @signup-email="signupEmail"
            @signup-password="signupPassword"
            @login="login"
            @forgot-password="forgotPassword"
            @reset-password="resetPassword"
            @authenticate-with-google="authenticateWithGoogle"
          />

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { socket } from "@/socket";
import { config } from '@/config';
import axios from 'axios';
import TurndownService from 'turndown';

import { authenticating } from '@/utils/authenticating.js';
import { interfacing } from '@/utils/interfacing.js';
import { messaging } from '@/utils/messaging.js';
import { suggesting } from '@/utils/suggesting.js';

import ChatComp from '@/components/ChatComp.vue';
import ProfileComp from "@/components/ProfileComp.vue";
import InputComp from "@/components/InputComp.vue";
import SuggestionsComp from "@/components/SuggestionsComp.vue";

export default {
  components: {
    ChatComp,
    ProfileComp,
    InputComp,
    SuggestionsComp
  },

  data() {
    return {
      pageLoaded: false,
      isMobile: window.innerWidth <= 796,
      theme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
      view: 'chat',

      socketId: null,
      userStatus: null,
      userProfile: '',
      userProfileUpdated: false,
      
      chatContainerHeight: null,
      chat: [],
      chatChunksLoaded: 0,
      chatFullyLoaded: false,

      organicSuggestions: [],
      premadeSuggestions: [],
      premadeSuggestionsShown: false,
      premadeSuggsetionsTopic: '',

      responseIsProcessing: false,
      responseFlowstep: '',

      input: '',
      inputMode: 'default',
    };
  },

  mounted() {
    const promises = [];
    this.initializeSocket();

    const urlToken = new URLSearchParams(window.location.search).get("token");
    if (urlToken) {promises.push(this.processUrlToken(urlToken))}

    const hashParams = new URLSearchParams(window.location.hash.slice(1));
    const urlSupabaseAccessToken = hashParams.get('access_token');
    const urlSupabaseRefreshToken = hashParams.get('refresh_token');
    if (urlSupabaseAccessToken && urlSupabaseRefreshToken) {promises.push(this.HandleSupabaseAuth(urlSupabaseAccessToken, urlSupabaseRefreshToken))} 
    
    else if (localStorage.getItem('_q')) {
      this.chat = [{ role: 'assistant', content: '' }];
      messaging.sendManualAssistantMessage(this, localStorage.getItem('_q'));
      localStorage.removeItem('_q');
    } 

    else if (localStorage.getItem('_u')) {
      const token = localStorage.getItem('_u');
      promises.push(
        this.getXMoreMessages(),
        this.getUserData(token).then(() => {
          if (this.userStatus === 'anonymous') {
            // messaging.sendManualAssistantMessage(this, "Welcome back!");
            // this.organicSuggestions = ['Tell me more'];
          } else if (this.userStatus === 'verified') {
            messaging.sendManualAssistantMessage(this, "Your email has been confirmed!<br>Let's set up your password now.");
            this.inputMode = 'signup_password';
            this.premadeSuggestionsShown = true;
          } else if (this.userStatus === 'registered') {
            messaging.sendManualAssistantMessage(this, "Welcome back!");
            this.organicSuggestions = ['Tell me more'];
          }
        })
      )
    } 
    
    else {
      this.chat = [{ role: 'assistant', content: '' }];
      messaging.sendManualAssistantMessage(this, 'Welcome to **SECRAG**.<br>We make security analysis easier.');
      this.organicSuggestions = ['How exactly?', 'Show me an example'];
    }

    Promise.all(promises).finally(() => {
      suggesting.getPremadeSuggestions(this);
      interfacing.observeSize(this);
      interfacing.chatScrollToBottom();
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
      socket.on("connect", () => {this.socketId = socket.id});

      socket.on("response_started", () => {console.log('response started')});

      socket.on("response_token", (data) => {
        messaging.processResponse(this, data.word), 
        this.responseFlowstep = ''
      });

      socket.on("response_complete", () => {
        this.responseIsProcessing = false;
        messaging.saveAssitantResponse(this);
        this.responseIsSaved = true; 
        const textarea = document.getElementById('textarea');
        if (textarea) textarea.focus();
      });

      socket.on("suggestions", (data) => {this.organicSuggestions = data.suggestions;});
      socket.on("flowstep", (data) => {console.log('flowstep received', data.flowstep), this.responseFlowstep = data.flowstep});
      socket.on("widget", (data) => {console.log(data), messaging.processWidget(this, data)});
      socket.on("tool", (data) => {messaging.processTool(this, data)});
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
      if (result.data.error) {localStorage.setItem('_q', result.data.error); window.location.href = '/'}
      else {
        if (result.data.action === 'confirm_email') {
          window.location.href = '/'
          this.inputMode = 'signup_password'
          messaging.sendManualAssistantMessage(this, "Your email has been confirmed!<br>Let's set up your password now.")
        }
        if (result.data.action === 'reset_password') {
          messaging.sendManualAssistantMessage(this, 'You can now enter your new password.')
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

    async getXMoreMessages() {
      const messageCount = 20;

      const chatContainer = document.getElementById("chatContainer");
      const scrollHeightBefore = chatContainer.scrollHeight;
      const scrollTopBefore = chatContainer.scrollTop;

      const result = await axios.get(
        `${config.apiUrl}/api/get-x-more-messages?token=` +
          localStorage.getItem('_u') +
          `&count=` + messageCount +
          `&skip=` + this.chatChunksLoaded
      );

      if (result.data.x_more_messages.length < messageCount) {this.chatFullyLoaded = true;}

      this.chat = [...result.data.x_more_messages, ...this.chat];
      this.chatChunksLoaded += 1;

      requestAnimationFrame(() => {
        const scrollHeightAfter = chatContainer.scrollHeight;
        const heightDifference = scrollHeightAfter - scrollHeightBefore;
        chatContainer.scrollTop = scrollTopBefore + heightDifference;
      });
    },

    async getUserProfile(token) {
      const result = await axios.get(`${config.apiUrl}/api/get-user-profile?token=` + token);
      this.userProfile = result.data.profile
    },

    async updateUserProfile() {
      const userProfileHTML = this.$refs.profileComp.$refs.profileDiv.innerHTML;
      const turndownService = new TurndownService();
      const userProfileMarkdown = turndownService.turndown(userProfileHTML);
      
      const result = await axios.post(`${config.apiUrl}/api/update-user-profile`, {token: localStorage.getItem('_u'), profile: userProfileMarkdown, socketId: this.socketId});
      if (result.data.error) {console.log(result.data.error)}
      else {this.userProfileUpdated = true; this.userProfile = userProfileMarkdown}
    },

    // INTERFACING
    updateTextareaHeight() {interfacing.updateTextareaHeight(this);},

    // SUGGESTING
    switchToDefaultInput() {this.inputMode = 'default';},
    getPremadeSuggestions() {suggesting.getPremadeSuggestions(this);},
    togglePremadeSuggestionsVisibility() {this.premadeSuggestionsShown = !this.premadeSuggestionsShown},

    // MESSAGING
    async sendMessage(input) {await messaging.sendMessage(this, input)},
    async stopResponse() {messaging.stopResponse(this, socket)},
    sendManualAssistantMessage(ctx, message) {messaging.sendManualAssistantMessage(ctx, message)},

    // AUTHENTICATING
    async signupEmail(email) {await authenticating.signupEmail(this, email);},
    async signupPassword(password, passwordConfirm) {await authenticating.signupPassword(this, password, passwordConfirm);},
    async login(email, password) {console.log(email, password); await authenticating.login(this, email, password);},
    async authenticateWithGoogle() {await authenticating.authenticateWithGoogle(this);},
    async HandleSupabaseAuth(urlSupabaseAccessToken, urlSupabaseRefreshToken) {await authenticating.HandleSupabaseAuth(this, urlSupabaseAccessToken, urlSupabaseRefreshToken);},
    async forgotPassword(email) {await authenticating.forgotPassword(this, email);},
    async resetPassword(password, passwordConfirm) {await authenticating.resetPassword(this, password, passwordConfirm);},
    signOut() {authenticating.signOut(this);},

  }
};
</script>
