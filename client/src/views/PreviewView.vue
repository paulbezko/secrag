<template>
  <div v-if="windowLoaded" class="flex-column width-100 center gap-1 padding-sidebar-dashboard height-100" style="height: 100svh; padding-bottom: 1rem; max-width: 140rem; overflow: hidden;">
  
    <!-- Component Section -->
    <div v-if="showProfile" class="backdrop z-17" @click="toggleProfile"></div>
    <div v-if="showConfirm" class="backdrop z-17" @click="toggleConfirm"></div>
    <div v-if="showConfirm && confirmLoading" class="card-component absolute z-20">
      <SpinnerCompInside :customClass="'text-2'"></SpinnerCompInside>
    </div>

    <div v-if="showConfirm && confirmAction === 'afterBilling'" class="card-component flex-column absolute z-20 gap-1 center text-center gap-2" style="max-width: 30rem">
      <div :class="isSmallScreen ? 'text-3' : 'text-4'">If you have submitted any adjustments, please note that it might take a few minutes for them to apply.</div>
      <div :class="isSmallScreen ? 'text-3' : 'text-4'">You will receive an email confirmation after the payment is processed.</div>
      <div :class="isSmallScreen ? 'text-3' : 'text-4'">Additionally, you can track the status of your payment on the Stripe billing portal.</div>
      <div :class="isSmallScreen ? 'text-3' : 'text-4'">In case the changes were not applied, feel free to contact support.</div>
      <div class="button button-secondary" @click="toggleConfirm()">OK</div>
    </div>

    <div v-if="showConfirm && confirmAction === 'insufficientTokens' && !confirmLoading" class="card-component flex-column center gap-1 absolute z-20" style="max-width: 32rem; padding: 2rem">
      <div class="text-1 text-bold text-center">Thank You for checking SECRAG out!</div>
      <div class="text-3 text-center">We would really value your feedback. Send it simply by clicking the button below.</div>
      <div class="button button-primary"><a href="mailto:secrag.info@gmail.com?subject=Feedback&body=Hi%20there%2C">Share Feedback</a></div>
    </div>
    <div v-if="sidebarShown && isSmallScreen" class="backdrop z-10" @click="toggleSidebar"></div>
    <div class="absolute" v-if="isSmallScreen" style="top: 0; right: 0; padding: 2rem;" @click="toggleSidebar"><div class="fa-solid fa-ellipsis-vertical text-1"></div></div>

    <!-- Sidebar Section -->
    <transition name="slide">
      <div class="sidebar flex-column gap-1 z-15 text-inter" v-if="sidebarShown" :style="isSmallScreen ? 'max-width: 18rem;' : 'max-width: 18rem;'">
        <div class="flex-column height-100">
          <div class="flex-column gap-05">
            <div class="flex-column gap-05" :class="isSmallScreen ? 'text-3' : 'text-4'">
              <router-link to="/" class="flex-row gap-05 sidebar-element menu" style="align-items: center;">
                <div class="fa-solid fa-house text-center sidebar-element-icon" style="min-width: 2rem;"></div>
                <div :class="isSmallScreen ? 'text-3' : 'text-4'">Homepage</div>
              </router-link>
              <div class="flex-row gap-05 sidebar-element menu" style="align-items: center;">
                <div class="fa-solid fa-coins text-center sidebar-element-icon" style="min-width: 2rem;"></div>
                <div :class="isSmallScreen ? 'text-3' : 'text-4'">Tokens: {{ subscriptionTokensLeft }}</div>
              </div>
              <div @click="toggleNewChat" class="flex-row gap-05 sidebar-element menu" style="align-items: center;" :class="{ active: newChat }">
                <div class="fa-solid fa-file-pen text-center sidebar-element-icon" style="min-width: 2rem;"></div>
                <div :class="isSmallScreen ? 'text-3' : 'text-4'">New Chat</div>
              </div>
            </div>
            <div class="width-100" style="padding-right: 0.5rem;"><hr class="width-100" style="border-top: 1px solid var(--color-grey);"></div>
            <div class="flex-column gap-1">
              <ul :style="{ height: chatHistoryHeight }" style="list-style-type: none; padding: 0" class="flex-column gap-05 chat-history">
                <li class="text-4 sidebar-element text-link" v-for="chat in chats" :key="chat" :class="{ active: currentChat === chat }" @click="selectChat(chat)" @mouseover="hoveredChat = chat" @mouseleave="hoveredChat = null">
                  <div class="flex-row space-between" :class="isSmallScreen ? 'text-3' : 'text-4'" style="align-items: center; white-space: nowrap; overflow: hidden; ">
                    <div style="max-width: 9rem; text-overflow: ellipsis;">{{ chat }}</div>
                    <div class="flex-row gap-05">
                      <div v-if="hoveredChat === chat" @click="resetChat()" class="fa-solid fa-rotate-right icon-link-active sidebar-element-icon"></div>
                      <div v-if="hoveredChat === chat" @click="deleteChat()" class="fa-solid fa-trash-can icon-link-active sidebar-element-icon"></div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
            <div class="width-100" style="padding-right: 0.5rem;"><hr class="width-100" style="border-top: 1px solid var(--color-grey);"></div>
            <div class="flex-row gap-05 sidebar-element menu" style="align-items: center;">
              <div class="fa-solid fa-file text-center sidebar-element-icon" style="min-width: 2rem;"></div>
              <a href="mailto:secrag.info@gmail.com?subject=Feedback&body=Hi%20there%2C" :class="isSmallScreen ? 'text-3' : 'text-4'">Share Feedback</a>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- New Chat Section -->
    <div class="absolute" v-if="newChatLoading">
      <div class="z-20 flex-column center gap-1 card relative">
        <div class="text-2 text-bold" style="box-sizing: border-box; white-space: nowrap;">Creating the Chat</div>
        <div class="flex-row center gap-1">
          <div class="text-3" style="box-sizing: border-box; white-space: nowrap;">{{ newChatLoadingMessage }}</div>
          <SpinnerCompInside :customClass="'text-3'"></SpinnerCompInside>
        </div>
      </div>
      <div class="backdrop z-10"></div>
    </div>
    <div v-if="newChat" class="flex-column center gap-2" style="padding: 2rem">
      <div class="subheading">Create a new Chat</div>
      <div class="text-3">Select a Ticker, Year of interest, and a Filing Type</div>
      <div class="flex-column switch-row-to-column gap-1 width-100">
        <div class="relative width-100">
          <input type="text" class="input width-100" v-model="tickerInput" @input="filterTickers" @focus="showSuggestions = true" @blur="handleBlur" placeholder="Ticker" :class="{ 'selected-option': selectedTicker !== '' }"/>
          <div v-if="showSuggestions && filteredTickers.length > 0" class="suggestions-container">
            <div v-for="ticker in filteredTickers.slice(0, 10)" :key="ticker" class="suggestion-item" @mousedown="selectTickerFromSuggestion(ticker)">
              {{ ticker }}
            </div>
          </div>
        </div>
        <select class="input" @change="selectYear($event.target.value)" v-model="selectedYear" :class="{ 'input-disabled': selectedTicker === '' , 'selected-option': selectedYear !== '' }" :disabled="selectedTicker === ''">
          <option value="" disabled hidden selected>Year</option>
          <option v-for="option in yearOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
        <select class="input" @change="selectFiling($event.target.value)" v-model="selectedFiling" :class="{ 'input-disabled': selectedYear === '', 'selected-option': selectedFiling !== '' }" :disabled="selectedYear === ''">
          <option value="" disabled hidden selected>Filing</option>
          <option v-for="option in filingOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
      </div>
      <div
        class="button button-primary flex-row gap-1 width-100" 
        :class="{ 'button-disabled': (!selectedTicker || !selectedYear || !selectedFiling)}" 
        @click="createChat()"
        :disabled="(!selectedTicker || !selectedYear || !selectedFiling)">
        Create Chat
      </div>
      <div v-if="error && selectedNewFiling === ''" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
    </div>

    <!-- Chat Section -->
    <div class="flex-row width-100 gap-1 height-100" style="justify-content: center; max-height: calc(100svh - 4rem);" :style="isSmallScreen ? '' : 'padding: 1rem 1rem 0rem 1rem;'" v-if="!newChat">
      <div class="flex-column width-100 gap-1 center" style="max-width: 75rem; background-color: transparent;">
        <div v-if="!filingShown || !isSmallScreen" class="chat-container text-inter height-100" id="chat-container">
          <SpinnerCompInside v-if="chatLoading" :customClass="'text-3'"></SpinnerCompInside>
          <div v-else class="chat-container-scroll" ref="chatContainer">
            <div v-for="(message, index) in currentMessages" :key="index" :class="{'text-chat': message.role === 'assistant', 'text-chat': message.role === 'user'}">
              <div v-if="message.role === 'assistant'" class="width-100 flex-row switch-row-to-column gap-1" style="margin-bottom: 1rem;">
                <div class="flex-row gap-1" :style="isSmallScreen ? 'align-items: center' : ''">
                  <!-- v-if needed to only show emoji in the last message -->
                  <img
                    v-if="index === currentMessages.length - 1" 
                    :src="newMessage !== '' 
                      ? require('@/assets/dashboard/face_with_monocle_3d.png')
                      : (assistantMessageIndex === index && assistantMessageLoading
                        ? require('@/assets/dashboard/thinking_face_3d.png')
                        : require('@/assets/dashboard/slightly_smiling_face_3d.png'))"
                    class="bot-image"
                  >
                  <img
                  v-if="index !== currentMessages.length - 1" 
                  :src="require('@/assets/dashboard/relieved_face_3d.png')" 
                  class="bot-image"
                  >
                  <div class="loading-dots" v-if="assistantMessageLoading && index === assistantMessageIndex">
                    <span class="loading-dot"></span>
                    <span class="loading-dot"></span>
                    <span class="loading-dot"></span>
                  </div>
                </div>
              <div style="text-wrap: break-word" class="text-chat chat-message-assistant" v-html="renderMarkdown(message.content)" v-if="!assistantMessageLoading || index !== assistantMessageIndex"></div>
              </div>
              <div v-else class="flex-row width-100" style="justify-content: flex-end;">
                <div class="chat-message-user text-chat">{{ message.content }}</div>
              </div>
            </div>
          </div>
        </div>
        <!-- Filing Container Small -->
        <div class="filing-container flex-column center" ref="filingContainer" v-if="filingShown && isSmallScreen" >
          <SpinnerCompInside v-if="filingLoading" :customClass="'text-3'"></SpinnerCompInside>
          <div class="filing-html" v-if="!filingLoading" style="padding: 2rem;" v-html="filingContent"></div>
        </div>
        <div class="flex-row width-100 gap-1" :style="isSmallScreen ? 'padding-inline: 1rem' : ''" style="max-width: 75rem;">
          <textarea 
            placeholder="Enter your message here"
            class="chat-input" 
            rows="1" 
            v-model="newMessage" 
            @keydown.enter.exact.prevent 
            @keyup.enter.exact="sendMessage('textarea')"
            @input="adjustTextareaHeight('textarea')" 
            style="resize: none;" 
            ref="textarea"
            >
          </textarea>
          <!-- Input Buttons Large -->
          <div v-if="!isSmallScreen && stopButtonShown" class="button-icon" @click="stopResponse()"><div class="fa-solid fa-stop" style="color: var(--color-grey-black)"></div></div>
          <div v-if="!isSmallScreen && !stopButtonShown" class="button-icon" @click="sendMessage('textarea')"><div class="fa-solid fa-arrow-up" style="color: var(--color-grey-black)"></div></div>
          
          <div class="button-icon" v-if="!isSmallScreen" @click="toggleFilingView"><div class="fa-solid fa-file-lines" style="color: var(--color-grey-black)"></div></div>
          <!-- Input Buttons Small -->
          <div class="button-icon show-on-small" style="min-width: 4.6rem !important; min-height: 4.6rem !important" v-if="newMessage == '' && isSmallScreen && !stopButtonShown" @click="toggleFilingView">
            <div class="fa-solid fa-file-lines text-1" style="color: var(--color-grey-black);"></div>
          </div>
          <div class="button-icon" v-if="newMessage == '' && isSmallScreen && stopButtonShown" style="min-width: 4.6rem !important; min-height: 4.6rem !important"  @click="stopResponse()"><div class="fa-solid fa-stop text-1" style="color: var(--color-grey-black)"></div></div>
          <div class="button-icon" v-if="!newMessage == '' && isSmallScreen && !stopButtonShown" style="min-width: 4.6rem !important; min-height: 4.6rem !important"  @click="sendMessage('textarea')"><div class="fa-solid fa-arrow-up text-1" style="color: var(--color-grey-black)"></div></div>
        </div>
      </div>
      <!-- Filing Container Large -->
      <div class="filing-container flex-column center" ref="filingContainer" v-if="filingShown && !isSmallScreen" >
        <SpinnerCompInside v-if="filingLoading" :customClass="'text-3'"></SpinnerCompInside>
        <div class="filing-html" v-if="!filingLoading" style="padding: 2rem;" v-html="filingContent"></div>
      </div>
    </div>

    <!-- Disclaimer Section -->
    <div class="text-4 text-center" style="box-sizing: border-box;" v-if="!newChat">SECRAG can make mistakes. Check important info.</div>
  </div>
</template>

<script>
import SpinnerCompInside from '../components/SpinnerCompInside.vue';
import { config } from '@/config';
import { marked } from 'marked';
import { socket } from "@/socket";
import { ref } from 'vue';
import axios from 'axios';
const katex = require('katex');

export default {
  components: {SpinnerCompInside},
  data() {
    return {
      // UI states
      windowLoaded: false,
      showProfile: false,
      sidebarShown: false,
      filingShown: false,
      showConfirm: false,
      confirmAction: '',
      confirmLoading: false,
      confirmSuccess: false,
      isSmallScreen: window.innerWidth <= 800, // Initial check for screen size
      createButtonDisabled: true,
      newChatLoadingMessage: '',
      scrollTimeout: null,
      lastScrollTime: 0,
      userHasScrolled: false,

      subscriptionTokensLeft: 100,

      // Chat data
      chats: [],
      hoveredChat: null,
      currentChat: null,
      activeChat: null,
      currentMessages: [],
      newChat: true,
      newMessage: '',
      assistantMessageIndex: null, // Index for assistant message
      assistantMessageLoading: false,
      assistantMessageBeingRendered: false,
      llmResponseBuffer: '', // Buffer for LLM incoming words
      chatLoading: false,
      newChatLoading: false,
      lastXMessagesLength: 0,
      chatScrollPosition: 0, // To store chat scroll position
      chatHistoryHeight: '0px', // Adjusted dynamically based on screen size
      stopButtonShown: false,
      responseStopped: false,

      // Filing data
      filingContent: '',
      filingLoading: false,
      newFilings: [],
      availableFilings: {},
      filingOptions: [],
      filingDate: '',
      filingScrollPosition: 0, // To store filing scroll position

      // Ticker selection
      tickerInfo: {},
      tickerOptions: ["AAPL | Apple Inc.", "TSLA | Tesla, Inc.", "NVDA | NVIDIA CORP", "MSFT | MICROSOFT CORP"],
      yearOptions: [],
      selectedTicker: '', // Initialize selected ticker
      selectedYear: '', // Initialize selected year
      selectedDate: '',
      selectedFiling: '',
      selectedFilingType: '',
      selectedNewFiling: '',

      tickerInput: '',
      filteredTickers: [],
      showSuggestions: false,

      // Socket
      socketId: '',

      // Miscellaneous
      error: null,
      chatContainer: ref(null),
      filingContainer: ref(null),
    };
  },
  
  mounted() {
    const afterBilling = new URLSearchParams(window.location.search).get('after-billing');
    if (afterBilling === 'true') {this.confirmAction = 'afterBilling'; this.showConfirm = true;}
    this.initializeSocket();
    this.windowLoaded = true;
    this.updateChatHistoryHeight();
    if (!this.isSmallScreen) {this.sidebarShown = true;}
    else (this.filingShown = false)
    window.addEventListener('resize', this.handleResize);
    this.lastXMessagesLength = 16
  },
  unmounted() {
    window.removeEventListener('resize', this.handleResize);
    socket.off("llm_response_complete");
    socket.off("llm_response");
    socket.disconnect();
    if (this.$refs.chatContainer) {
      this.$refs.chatContainer.removeEventListener('wheel', this.handleUserScroll);
      this.$refs.chatContainer.removeEventListener('touchmove', this.handleUserScroll);
    }
  },

  methods: {

    // Initialize Socket
    initializeSocket() {
      socket.connect();
      socket.on("connect", () => {(this.socketId = socket.id)}); // console.log("Connected to socket", socket.id);
      socket.on("new_chat_started", () => {this.newChatLoadingMessage = 'Creating chat';});
      socket.on("new_chat_initialized", () => {this.newChatLoadingMessage = 'Downloading the filing';});
      socket.on("new_chat_downloaded", () => {this.newChatLoadingMessage = 'Vectorizing the filing';});
      socket.on("new_chat_vectorized", () => {this.newChatLoadingMessage = 'Finishing up';});
      socket.on("llm_response", (data) => {if (!this.responseStopped && data && data.word) {this.llmResponseBuffer += data.word; this.updateAssistantMessage()}});
      socket.on("llm_response_complete", () => {this.saveAssitantResponse(); this.$nextTick(() => {this.scrollToBottom("smooth")})});
    },

    // Update Chat History Height
    updateChatHistoryHeight() {
      let heightAdjustment = 0
      const headerHeight = 175; 
      if (this.isSmallScreen) {heightAdjustment = -52;}
      const availableHeight = window.innerHeight - headerHeight + heightAdjustment;
      this.chatHistoryHeight = `${availableHeight}px`;
    },

    // Select Ticker
    selectTicker(option) {
      this.error = null; 
      this.selectedTicker = option; 
      this.selectedYear = '';
      this.selectedFiling = '';
      this.selectedNewFiling = '';
      axios.get(`${config.apiUrl}/api/get-info-by-ticker-preview`, {params: { ticker: option }})
      .then(response => {this.tickerInfo = response.data.info; this.yearOptions = Object.keys(this.tickerInfo)})
      .catch(error => {console.error('Error getting ticker info:', error)});
    },

    // Select Year and Filing
    selectYear(option) {this.error = null; this.selectedYear = option; this.selectedFiling = ''; this.filingOptions = this.tickerInfo[this.selectedYear];},
    selectFiling(option) {this.error = null; this.selectedFiling = option;},
    selectNewFiling(option) {this.error = null; this.selectedNewFiling = option; this.selectedTicker = ''; this.selectedYear = ''; this.selectedFiling = '';},

    // Create chat
    async createChat() {

      if ((!this.selectedTicker || !this.selectedYear || !this.selectedFiling) && !this.selectedNewFiling) {return}
      if (this.chats.length === 1) {this.error = 'You can only have one chat in preview mode.'; return}

      let selectedTicker, selectedYear, selectedDate, selectedFilingType

      if (this.selectedNewFiling) {
        [selectedTicker, selectedFilingType, selectedDate] = this.selectedNewFiling.split(" ");
        selectedFilingType = selectedFilingType.replace('-', '')
        selectedYear = selectedDate.split('-')[0]
      }

      else {
        selectedTicker = this.selectedTicker.split(" | ")[0]
        selectedYear = this.selectedYear
        selectedFilingType = this.selectedFiling.split(' ')[0].replace('-', '')
        selectedDate = this.selectedFiling.split(' ')[1]
        this.filingDate = selectedDate
      }

      let newChatName = `${selectedTicker}-${selectedYear}-${selectedFilingType}`
      if (this.chats.includes(newChatName)) {this.error = 'Chat already exists'; return}

      try {

        this.newChatLoading = true;
        this.tickerInput = '';
        this.selectedTicker = '';
        this.selectedYear = '';
        this.selectedFiling = '';
        this.selectedNewFiling = '';
        let response = await axios.post(`${config.apiUrl}/api/new-chat-preview`, {
          chat: newChatName,
          filingDate: selectedDate,
          ticker: selectedTicker,
          socketId: this.socketId
        });

        if (response.data.error) {
          if (response.data.error === 'Insufficient Tokens') {this.confirmAction = 'insufficientTokens', this.showConfirm = true}
          else {console.log(response.data.error); this.newChatLoading = false}
          return;
        }

        this.subscriptionTokensLeft += -20
        this.chats.unshift(newChatName);
        this.selectChat(newChatName);
        if (this.isSmallScreen) {this.sidebarShown = false;}
        this.newChat = false;
        this.selectedTicker = '';
        this.selectedYear = '';
        this.selectedFiling = '';
        this.newChatLoading = false;
      } 
      catch (error) {console.error('Error creating chat:', error);}
    },

    // Select Chat
    async selectChat(chat) {
      
      if (this.llmResponseBuffer !== '') {this.stopResponse()}
      
      this.newChat = false;
      this.currentChat = chat;
      this.currentMessages = [{role: 'assistant', content: 'Hello! How can I help you today?'}]

      try {this.scrollToBottom('instant')} 
      catch (error) {console.warning('Error in scrollToBottom:', error)}
      this.filingLoading = true

      await axios.get(`${config.apiUrl}/api/get-filing-preview`, {params: { 'filingDate': this.filingDate, 'chat': chat }})
      .then(response => {this.filingContent = response.data.html; this.filingLoading = false})
      .catch(error => {console.error('Error getting filing:', error);});

      if (this.$refs.chatContainer) {
        this.$refs.chatContainer.addEventListener('wheel', this.handleUserScroll);
        this.$refs.chatContainer.addEventListener('touchmove', this.handleUserScroll);
      }
    },

    // Reset Chat
    async resetChat() {
      this.currentMessages = [{role: 'assistant', content: 'Hello! How can I help you today?'}]
    },

    // Delete Chat
    async deleteChat() {
      this.chats = []
      this.newChat = true
    },
  
    // Send Message
    async sendMessage() {
      if (this.subscriptionTokensLeft < 4) {this.confirmAction = 'insufficientTokens', this.showConfirm = true; return}

      this.subscriptionTokensLeft += -4
      this.userHasScrolled = false;
      this.stopButtonShown = true
      // If there's an ongoing response, stop it and save it first
      if (this.llmResponseBuffer !== '') {
        await this.stopResponse();
      }

      if (this.isSmallScreen && this.filingShown) {
        this.toggleFilingView();
      }

      const textarea = this.$refs['textarea'];
      textarea.style.height = '40px';

      if (this.newMessage.trim() !== '') {

        this.responseStopped = false
        this.currentMessages.push({role: 'user', content: this.newMessage});
        this.assistantMessageIndex = this.currentMessages.length;
        this.assistantMessageLoading = true;
        this.llmResponseBuffer = '';
        this.currentMessages[this.assistantMessageIndex] = {role: 'assistant', content: null};
        let payloadMessage = this.newMessage
        this.newMessage = '';
        this.newChat = false;
        this.activeChat = this.currentChat;
        
        this.$nextTick(() => {this.adjustTextareaHeight('textarea'); this.scrollToBottom("smooth")});
        const lastXMessages = this.currentMessages.slice(-this.lastXMessagesLength)

        try {
          let response = await axios.post(`${config.apiUrl}/api/new-message-user-preview`, {
            chat: this.activeChat,
            message: payloadMessage,
            lastXMessages: lastXMessages,
            socketId: this.socketId,
            filingDate: this.filingDate
          });

          if (response.data.error) {
            console.log(response.data.error)
            return;
          }
        } catch (error) {console.error('Error sending message:', error); return;}
      }
    },
    
    // Update Assistant Message
    updateAssistantMessage() {
      if (this.assistantMessageIndex !== null) {
        if (this.llmResponseBuffer.trim()) {
          this.assistantMessageLoading = false;
          this.assistantMessageBeingRendered = true;
          this.currentMessages[this.assistantMessageIndex].content = this.renderMarkdown(this.llmResponseBuffer);
          
          // Only auto-scroll if user hasn't manually scrolled
          if (!this.userHasScrolled) {
            const currentTime = Date.now();
            if (currentTime - this.lastScrollTime >= 1000) {
              this.lastScrollTime = currentTime;
              try {this.$nextTick(() => {this.scrollToBottom("smooth")})} 
              catch (error) {console.log(error)}
            }
          }
        }
      }
    },

    async stopResponse() {
      return new Promise((resolve) => {
        socket.emit("stop_llm_stream");
        this.responseStopped = true; 
        this.assistantMessageLoading = false;
        setTimeout(() => {resolve()}, 100);
      });
    },

    async saveAssitantResponse() {
      try {
        this.assistantMessageLoading = false;
        this.assistantMessageBeingRendered = false;
        this.userHasScrolled = false;
        this.stopButtonShown = false;
        this.llmResponseBuffer = '';
      } catch (error) {
        console.error('Error sending message:', error);
      }
    },

    renderMarkdown(content) {
      if (!content) {return '';}
      
      // Format numbers before converting to markdown
      const numberFormatted = content.replace(/\b(\d{1,3}(,\d{3})*)\b/g, (match) => {
        const num = match.replace(/,/g, '');
        if (/000000$/.test(num)) {return (parseInt(num) / 1000000) + 'M'}
        else if (/000$/.test(num)) {return (parseInt(num) / 1000) + 'K'}
        return match;
      });

      // Convert the latex expressions
      const latexConverted = numberFormatted
        .replace(/\\\[(.*?)\\\]/gs, (_, latex) => {return katex.renderToString(latex, { displayMode: true })})
        .replace(/\\\((.*?)\\\)/gs, (_, latex) => {return katex.renderToString(latex, { displayMode: false })})
        
      return marked(latexConverted);
    },

    // Toggle Filing View
    toggleFilingView() {
      this.filingShown = !this.filingShown;
      if (this.isSmallScreen && !this.filingShown) {this.$nextTick(() => {this.scrollToBottom("instant")})}
      if (this.filingShown) {setTimeout(() => {const offset = this.isSmallScreen ? 25 : 0; this.$refs.filingContainer.scrollTop = this.filingScrollPosition + offset;}, 50)}
    },

    // Various UI Helpers
    adjustTextareaHeight(refName) {
      this.$refs[refName].style.height = 'auto';
      let adjustment = 0
      if (this.isSmallScreen) {adjustment = 1}
      this.$refs[refName].style.height = (Math.min(this.$refs[refName].scrollHeight, 160) + 1 + adjustment) + 'px';
    },
    checkScreenWidth() {this.isSmallScreen = window.innerWidth <= 800;},
    handleResize() {this.checkScreenWidth(); this.updateChatHistoryHeight()},
    scrollToBottom(type) {
      try {
        if (this.$refs.chatContainer) {
          this.$refs.chatContainer.scrollTo({
            top: this.$refs.chatContainer.scrollHeight,
            behavior: type,
          });
        } else {
          console.warn('chatContainer is not yet available');
        }
      } catch (error) {
        console.error('Error in scrollToBottom:', error);
      }
    },

    // Toggle Sidebar, Profile, New Chat, Confirm
    toggleProfile() {this.showProfile = !this.showProfile; if (this.isSmallScreen) {this.sidebarShown = false}},
    toggleSidebar() {this.sidebarShown = !this.sidebarShown;},
    toggleNewChat() {this.currentChat='', this.newChat = true; this.currentMessages = []; if (this.isSmallScreen) {this.sidebarShown = false}},
    toggleConfirm(action) {
        // Clear URL parameters by updating the URL
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);

        // Toggle the confirmation state as per your original function
        this.confirmAction = action;
        this.confirmSuccess = false;
        this.showConfirm = !this.showConfirm;
    },

    filterTickers() {
    this.selectedTicker = '';
    this.showSuggestions = true;
    if (this.tickerInput) {
      this.filteredTickers = this.tickerOptions.filter(ticker =>
        ticker.toLowerCase().includes(this.tickerInput.toLowerCase())
      );
    } else {
      this.filteredTickers = [];
    }
  },

  selectTickerFromSuggestion(ticker) {
    this.tickerInput = ticker;
    this.selectedTicker = ticker;
    this.showSuggestions = false;
    this.selectTicker(ticker);
  },

  handleBlur() {
    // Delay hiding suggestions to allow for mousedown event on suggestion
    setTimeout(() => {
      this.showSuggestions = false;
      // If input doesn't match any valid ticker, clear it
      if (!this.tickerOptions.includes(this.tickerInput)) {
        this.tickerInput = '';
        this.selectedTicker = '';
      }
    }, 200);
  },
  handleUserScroll() {if (this.assistantMessageBeingRendered) {this.userHasScrolled = true}},
  }
};

</script>
<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-enter-to {
  transform: translateX(0);
}

.slide-leave-from {
  transform: translateX(0);
}

.slide-leave-to {
  transform: translateX(100%);
}


.loading-dots {
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem; /* Slightly increased gap for better scaling */
}

.loading-dot {
  animation: dot ease-in-out 1.5s infinite;
  background-color: var(--color-yellow-dark);
  display: inline-block;
  height: 0.5rem; /* Increase the size slightly to avoid pixelation */
  width: 0.5rem;
  border-radius: 50%;
  will-change: transform; /* Optimize for transformations */
}

.loading-dot:nth-of-type(2) {
  animation-delay: 0.5s;
}

.loading-dot:nth-of-type(3) {
  animation-delay: 1s;
}

@keyframes dot {
  0% { background-color: var(--color-yellow-dark);}
  50% { background-color: var(--color-yellow);}
  100% { background-color: var(--color-yellow-dark);}
}


</style>

