<template>
  <div v-if="windowLoaded" class="flex-column width-100 center gap-1 padding-sidebar-dashboard height-100" style="height: 100vh; padding-bottom: 1rem; max-width: 140rem; overflow: hidden;">
  
    <!-- Component Section -->
    <component :is="profileComp"></component>
    <div v-if="showProfile" class="backdrop z-17" @click="toggleProfile"></div>
    <div v-if="showConfirm" class="backdrop z-17" @click="toggleConfirm"></div>
    <div v-if="showConfirm && confirmLoading" class="card-component absolute z-20">
      <SpinnerCompInside></SpinnerCompInside>
    </div>
    <div v-if="showConfirm && confirmSuccess" class="card-component absolute z-20 flex-row center text-2 gap-1">Chat Deleted
      <div class="fa-circle-check fa-solid text-1" style="color: var(--color-green)"></div>
    </div>
    <div v-if="showConfirm && confirmAction === 'deleteChat' && !confirmLoading" class="card-component flex-column center gap-1 absolute z-20">
      <div class="text-1 text-bold">Delete Chat?</div>
      <div class="button button-secondary" @click="deleteChat(currentChat)">Confirm</div>
    </div>
    <div v-if="showConfirm && confirmAction === 'insufficientTokens' && !confirmLoading" class="card-component flex-column center gap-1 absolute z-20" style="max-width: 32rem; padding: 2rem">
      <div class="text-1 text-bold text-center">Token Balance Low</div>
      <div class="text-3 text-center">Your account doesn't have enough tokens to proceed with this action.</div>
      <div class="button button-primary" @click="replenishTokens()">Add Tokens</div>
    </div>
    <div v-if="sidebarShown && isSmallScreen" class="backdrop z-10" @click="toggleSidebar"></div>
    <div class="absolute" v-if="isSmallScreen" style="top: 0; right: 0; padding: 2rem;" @click="toggleSidebar"><div class="fa-solid fa-ellipsis-vertical text-1"></div></div>

    <!-- Sidebar Section -->
    <transition name="slide">
      <div class="sidebar flex-column gap-1 z-15 text-inter" v-if="sidebarShown" :style="isSmallScreen ? 'max-width: 18rem;' : 'max-width: 18rem;'">
        <div class="flex-column space-between height-100">
          <div class="flex-column gap-05">
            <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
            <div class="flex-column gap-05" :class="isSmallScreen ? 'text-3' : 'text-4'">
              <div @click="toggleProfile" class="flex-row gap-05 sidebar-element menu" style="align-items: center;">
                <div class="fa-solid fa-user" style="min-width: 1.6rem;"></div>
                Profile
              </div>
              <div @click="toggleNewChat" class="flex-row gap-05 sidebar-element menu" style="align-items: center;" :class="{ active: newChat }">
                <div class="fa-solid fa-file-pen" style="min-width: 1.6rem;"></div>
                New Chat
              </div>
            </div>
            <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
            <div class="flex-column gap-1">
              <ul :style="{ height: chatHistoryHeight }" style="list-style-type: none; padding: 0" class="flex-column gap-05 chat-history">
                <li class="text-4 sidebar-element text-link" v-for="chat in chats" :key="chat" :class="{ active: currentChat === chat }" @click="selectChat(chat)" @mouseover="hoveredChat = chat" @mouseleave="hoveredChat = null">
                  <div class="flex-row space-between" :class="isSmallScreen ? 'text-3' : 'text-4'" style="align-items: center;">{{ chat }}<div v-if="hoveredChat === chat" @click="toggleConfirm('deleteChat')" class="fa-solid fa-trash-can icon-link-active"></div></div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- New Chat Section -->
    <SpinnerCompInside v-if="newChatLoading"></SpinnerCompInside>
    <div v-if="!newChatLoading && newChat" class="flex-column center gap-2" style="padding: 2rem">
      <div class="subheading">Create a new Chat</div>
      <div class="text-3" v-if="this.subscription === 'basic'">Select a Ticker and a Year of interest</div>
      <div class="text-3" v-if="this.subscription === 'premium'">Select a Ticker, Year of interest, and a Filing Type</div>
      <div class="flex-row switch-row-to-column gap-1 width-100">
        <select class="input" @change="selectTicker($event.target.value)" v-model="selectedTicker" :class="{ 'selected-option': selectedTicker !== '' }">
          <option value="" disabled hidden selected class="placeholder-option">Ticker</option>
          <option v-for="option in tickerOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
        <select class="input" @change="selectYear($event.target.value)" v-model="selectedYear" :class="{ 'input-disabled': selectedTicker === '' , 'selected-option': selectedYear !== '' }" :disabled="selectedTicker === ''">
          <option value="" disabled hidden selected>Year</option>
          <option v-for="option in yearOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
        <select class="input" @change="selectFiling($event.target.value)" v-model="selectedFiling" :class="{ 'input-disabled': selectedYear === '', 'selected-option': selectedFiling !== '' }" :disabled="selectedYear === ''" v-if="this.subscription === 'premium'">
          <option value="" disabled hidden selected>Filing</option>
          <option v-for="option in filingOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
      </div>
      <div
        class="button button-primary flex-row gap-1 width-100" 
        :class="{ 'button-disabled': (!selectedTicker || !selectedYear || (!selectedFiling && subscription !== 'basic'))}" 
        @click="createChat()"
        :disabled="(!selectedTicker || !selectedYear || (!selectedFiling && subscription !== 'basic'))">
        Create Chat
      </div>
      <div v-if="error && selectedNewFiling === ''" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
      <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
      <div class="text-3">Or choose one of the Recent Filings</div>
      <div class="flex-row gap-1">
        <select class="input" style="width: 24rem" @change="selectNewFiling($event.target.value)" v-model="selectedNewFiling" :class="{ 'selected-option': selectedNewFiling !== '' }">
          <option value="" disabled hidden selected>Select a Filing</option>
          <option v-for="option in newFilings" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
      </div>
      <div 
        class="button button-primary flex-row gap-1 width-100" 
        :class="{ 'button-disabled': !selectedNewFiling }"
        @click="createChat()"
        :disabled="!selectedNewFiling">
        Create Chat
      </div>
      <div v-if="error && selectedNewFiling !== ''" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
    </div>

    <!-- Chat Section -->
    <div class="flex-row width-100 gap-1 height-100" style="justify-content: center; max-height: calc(100vh - 4rem);" :style="isSmallScreen ? '' : 'padding: 1rem 1rem 0rem 1rem;'" v-if="!newChat">
      <div class="flex-column width-100 gap-1 center" style="max-width: 75rem; background-color: transparent;">
        <div v-if="!filingShown || !isSmallScreen" class="chat-container text-inter height-100" ref="chatContainer">
          <SpinnerCompInside v-if="chatLoading"></SpinnerCompInside>
          <div v-else>
            <div v-for="(message, index) in currentMessages" :key="index" :class="{'text-chat': message.role === 'assistant', 'text-chat': message.role === 'user'}">
              <div v-if="message.role === 'assistant'" class="width-100 flex-row gap-1">
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
                <div class="text-chat chat-message-assistant" v-html="renderMarkdown(message.content)" v-if="!assistantMessageLoading || index !== assistantMessageIndex"></div>
              </div>
              <div v-else class="flex-row width-100" style="justify-content: flex-end;">
                <div class="chat-message-user text-chat">{{ message.content }}</div>
              </div>
            </div>
          </div>
        </div>
        <!-- Filing Container Small -->
        <div class="filing-container flex-column center" ref="filingContainer" @scroll="handleScroll" v-if="filingShown && isSmallScreen" >
          <SpinnerCompInside v-if="filingLoading"></SpinnerCompInside>
          <div class="filing-html" v-if="!filingLoading" style="padding: 2rem;" v-html="filingContent"></div>
        </div>
        <div class="flex-row width-100 gap-1" :style="isSmallScreen ? 'padding-inline: 1rem' : ''" style="max-width: 75rem; align-items: end;">
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
          <div v-if="stopButtonShown"><div class="button-icon" v-if="!isSmallScreen" @click="stopResponse()"><div class="fa-solid fa-stop" style="color: var(--color-grey-black)"></div></div></div>
          <div v-else><div class="button-icon" v-if="!isSmallScreen" @click="sendMessage('textarea')"><div class="fa-solid fa-arrow-up" style="color: var(--color-grey-black)"></div></div></div>
          
          <div class="button-icon" v-if="!isSmallScreen" @click="toggleFilingView"><div class="fa-solid fa-file-lines" style="color: var(--color-grey-black)"></div></div>
          <!-- Input Buttons Small -->
          <div class="button-icon show-on-small" v-if="newMessage == '' && isSmallScreen" @click="toggleFilingView">
            <div class="fa-solid fa-file-lines" style="color: var(--color-grey-black)"></div>
          </div>
          <div v-if="stopButtonShown"><div class="button-icon" v-if="!newMessage == '' && isSmallScreen" @click="stopResponse()"><div class="fa-solid fa-stop" style="color: var(--color-grey-black)"></div></div></div>
          <div v-else><div class="button-icon" v-if="!newMessage == '' && isSmallScreen" @click="sendMessage('textarea')"><div class="fa-solid fa-arrow-up" style="color: var(--color-grey-black)"></div></div></div>
        </div>
      </div>
      <!-- Filing Container Large -->
      <div class="filing-container flex-column center" ref="filingContainer" @scroll="handleScroll" v-if="filingShown && !isSmallScreen" >
        <SpinnerCompInside v-if="filingLoading"></SpinnerCompInside>
        <div class="filing-html" v-if="!filingLoading" style="padding: 2rem;" v-html="filingContent"></div>
      </div>
    </div>

    <!-- Disclaimer Section -->
    <div class="text-4 text-center" style="box-sizing: border-box;" v-if="!newChat">SECRAG can make mistakes. Check important info.</div>
  </div>
</template>

<script>
import ProfileComp from '../components/ProfileComp.vue';
import SpinnerCompInside from '../components/SpinnerCompInside.vue';
import SpinnerCompButton from '../components/SpinnerCompButton.vue';
import SpinnerComp from '@/components/SpinnerComp.vue';
import { config } from '@/config';
import { marked } from 'marked';
import { socket } from "@/socket";
import { mapState } from 'vuex';
import { ref } from 'vue';
import axios from 'axios';

export default {
  components: {ProfileComp, SpinnerCompInside, SpinnerCompButton, SpinnerComp},
  computed: {
    profileComp() {return this.showProfile ? 'ProfileComp' : null},
    ...mapState(['subscription', 'subscriptionTokensLeft']),
  },
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

      // Chat data
      chats: [],
      hoveredChat: null,
      currentChat: '',
      currentMessages: [],
      newChat: true,
      newMessage: '',
      assistantMessageIndex: null, // Index for assistant message
      assistantMessageLoading: false,
      llmResponseBuffer: '', // Buffer for LLM incoming words
      chatLoading: false,
      newChatLoading: false,
      lastXMessagesLength: 0, // Adjusted based on subscription
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
      tickerOptions: [],
      yearOptions: [],
      selectedTicker: '', // Initialize selected ticker
      selectedYear: '', // Initialize selected year
      selectedDate: '',
      selectedFiling: '',
      selectedFilingType: '',
      selectedNewFiling: '',

      // Socket
      socketId: '',

      // Miscellaneous
      error: null,
      chatContainer: ref(null),
      filingContainer: ref(null),
    };
  },
  
  mounted() {
    this.initializeSocket();
    this.loadFilingSelectionData();
    this.loadChats();
    this.windowLoaded = true;
    this.updateChatHistoryHeight();
    if (!this.isSmallScreen) {this.sidebarShown = true;}
    else (this.filingShown = false)
    window.addEventListener('resize', this.handleResize);
    if (this.subscription === 'basic') {this.lastXMessagesLength = 5}
    else {this.lastXMessagesLength = 10}
  },
  beforeUnmount() {window.removeEventListener('resize', this.handleResize);},

  methods: {

    // Initialize Socket
    initializeSocket() {
      socket.connect();
      socket.on("connect", () => {(this.socketId = socket.id)});
      socket.on("llm_response", (data) => {if (!this.responseStopped && data && data.word) {this.llmResponseBuffer += data.word; this.updateAssistantMessage()}});
      socket.on("llm_response_complete", () => {if (!this.responseStopped) {this.stopButtonShown = false, this.saveAssitantResponse()}});
    },

    // Load List Tickers
    loadFilingSelectionData() {
      axios.get(`${config.apiUrl}/api/get-filing-selection-data`, {params: { token: localStorage.getItem('_u') }})
      .then(response => {this.newFilings = response.data.newFilings; this.tickerOptions = response.data.tickers;})
      .catch(error => {console.error('Error getting filing selection data:', error)});
    },

    // Load Chats
    loadChats() {
      axios.get(`${config.apiUrl}/api/get-chats`, {params: { token: localStorage.getItem('_u') }})
      .then(response => {this.chats = response.data.chats;})
      .catch(error => {console.error('Error getting chats:', error);});
    },

    // Update Chat History Height
    updateChatHistoryHeight() {
      let heightAdjustment = 0
      const headerHeight = 110; 
      if (this.isSmallScreen) {heightAdjustment = 6;}
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
      axios.get(`${config.apiUrl}/api/get-info-by-ticker`, {params: { token: localStorage.getItem('_u'), ticker: option }})
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

      let selectedTicker, selectedYear, selectedDate, selectedFilingType

      if (this.selectedNewFiling) {
        [selectedTicker, selectedFilingType, selectedDate] = this.selectedNewFiling.split(" ");
        selectedFilingType = selectedFilingType.replace('-', '')
        selectedYear = selectedDate.split('-')[0]
      }

      else {
        selectedTicker = this.selectedTicker
        selectedYear = this.selectedYear
        selectedFilingType = this.selectedFiling.split(' ')[0].replace('-', '')
        selectedDate = this.selectedFiling.split(' ')[1]
      }

      let newChatName = `${selectedTicker}-${selectedYear}-${selectedFilingType}`
      if (this.chats.includes(newChatName)) {this.error = 'Chat already exists'; return}

      try {

        this.newChatLoading = true;
        let response = await axios.post(`${config.apiUrl}/api/new-chat`, {
          token: localStorage.getItem('_u'),
          chat: newChatName,
          filingDate: selectedDate,
          ticker: selectedTicker
        });

        if (response.data.error) {
          if (response.data.error === 'Insufficient Tokens') {this.confirmAction = 'insufficientTokens', this.showConfirm = true}
          else {console.log(response.data.error); this.newChatLoading = false}
          return;
        }

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
    selectChat(chat) {
      this.newChat = false;
      this.currentChat = chat;
      this.chatLoading = true;

      axios.get(`${config.apiUrl}/api/get-messages`, {params: { token: localStorage.getItem('_u'), 'chat': chat }})
      .then(response => {this.currentMessages = response.data.messages; this.filingDate = response.data.filing_date})
      .catch(error => {console.error('Error getting messages:', error);})
      .finally(() => {this.chatLoading = false; this.$nextTick(() => {this.scrollToBottom("instant")});});

      this.filingLoading = true

      axios.get(`${config.apiUrl}/api/get-filing`, {params: { token: localStorage.getItem('_u'), 'chat': chat }})
      .then(response => {this.filingContent = response.data.html; this.filingLoading = false})
      .catch(error => {console.error('Error getting filing:', error);});
      if (this.isSmallScreen) {this.toggleSidebar();}
    },

    // Delete Chat
    async deleteChat(chat) {
      this.confirmLoading = true
      let response = await axios.post(`${config.apiUrl}/api/delete-chat`, {
        token: localStorage.getItem('_u'),
        chat: chat
      });

      if (response.data.error) {console.log(response.data.error); return;}
      this.confirmAction = ''
      this.confirmLoading = false
      this.confirmSuccess = true
      this.loadChats()
      this.newChat = true
    },
  
    // Send Message
    async sendMessage() {

      if (this.isSmallScreen && this.filingShown) {this.toggleFilingView();}

      const textarea = this.$refs['textarea']
      textarea.style.height = '40px'

      if (this.newMessage.trim() !== '') {

        this.responseStopped = false
        this.stopButtonShown = true
        this.currentMessages.push({role: 'user', content: this.newMessage});
        this.assistantMessageIndex = this.currentMessages.length;
        this.assistantMessageLoading = true;
        this.llmResponseBuffer = '';
        this.currentMessages[this.assistantMessageIndex] = {role: 'assistant', content: null};
        let payloadMessage = this.newMessage
        this.newMessage = '';
        this.newChat = false;
        
        this.$nextTick(() => {this.adjustTextareaHeight('textarea'); this.scrollToBottom("smooth")});
        const lastXMessages = this.currentMessages.filter(msg => msg.role === 'user').slice(-this.lastXMessagesLength)

        try {
          let response = await axios.post(`${config.apiUrl}/api/new-message-user`, {
            token: localStorage.getItem('_u'),
            chat: this.currentChat,
            message: payloadMessage,
            lastXMessages: lastXMessages,
            socketId: this.socketId,
            filingDate: this.filingDate
          });

          if (response.data.error) {
            if (response.data.error === 'Insufficient Tokens') {this.confirmAction = 'insufficientTokens', this.showConfirm = true}
            else (console.log(response.data.error))
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
          this.currentMessages[this.assistantMessageIndex].content = marked(this.llmResponseBuffer);
          this.$nextTick(() => {this.scrollToBottom("instant")});
        }
      }
    },

    stopResponse() {this.stopButtonShown = false; this.responseStopped = true; this.saveAssitantResponse();},
    async saveAssitantResponse() {          
      try {
          let response = await axios.post(`${config.apiUrl}/api/new-message-assistant`, {
            token: localStorage.getItem('_u'),
            chat: this.currentChat,
            message: this.llmResponseBuffer,
          });
          if (response.data.error) {console.log(response.data.error); return;}
        } catch (error) {console.error('Error sending message:', error); return;}
    },

    // Render Markdown
    renderMarkdown(content) {if (!content) {return '';} return marked(content)},

    // Toggle Filing View
    toggleFilingView() {
      this.filingShown = !this.filingShown;
      if (this.isSmallScreen && !this.filingShown) {this.$nextTick(() => {this.scrollToBottom("instant")})}
      if (this.filingShown) {setTimeout(() => {const offset = this.isSmallScreen ? 25 : 0; this.$refs.filingContainer.scrollTop = this.filingScrollPosition + offset;}, 50)}
    },

    // Various UI Helpers
    adjustTextareaHeight(refName) {this.$refs[refName].style.height = 'auto'; this.$refs[refName].style.height = (Math.min(this.$refs[refName].scrollHeight, 160) + 2) + 'px';},
    checkScreenWidth() {this.isSmallScreen = window.innerWidth <= 800;},
    handleResize() {this.checkScreenWidth(); this.updateChatHistoryHeight()},
    handleScroll(event) {this.filingScrollPosition = event.target.scrollTop;},
    scrollToBottom(type) {this.$refs.chatContainer.scrollTo({top: this.$refs.chatContainer.scrollHeight, behavior: type})},

    // Toggle Sidebar, Profile, New Chat, Confirm
    toggleProfile() {this.showProfile = !this.showProfile; if (this.isSmallScreen) {this.sidebarShown = false}},
    toggleSidebar() {this.sidebarShown = !this.sidebarShown;},
    toggleNewChat() {this.currentChat='', this.newChat = true; this.currentMessages = []; if (this.isSmallScreen) {this.sidebarShown = false}},
    toggleConfirm(action) {this.confirmAction = action; this.confirmSuccess = false; this.showConfirm = !this.showConfirm},

    // Replenish Tokens
    async replenishTokens() {
      this.showSpinner = true
      const response = await axios.post(`${config.apiUrl}/api/subscribe`, {token: localStorage.getItem('_u'), operation: 'replenishTokens'});
      window.location.href = response.data.sessionUrl;
    },
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

