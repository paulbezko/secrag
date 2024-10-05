<template>
  <div class="flex-column width-100 center gap-1 padding-sidebar-dashboard" style="height: 100vh; padding-bottom: 1rem; max-width: 140rem; overflow: hidden">
    <component :is="profileComp"></component>
    <div v-if="showProfile" class="backdrop z-17" @click="toggleProfile"></div>
    <div v-if="showConfirmDeleteChat" class="backdrop z-17" @click="toggleConfirmDeleteChat"></div>
    <div v-if="showConfirmDeleteChat" class="card flex-column center gap-1 absolute z-20">
      <div class="text-1 text-bold">Delete Chat?</div>
      <div class="button button-secondary" @click="deleteChat(currentChat)">Confirm</div>
    </div>
    <div v-if="sidebarShown && isSmallScreen" class="backdrop z-10" @click="toggleSidebar"></div>
    <div class="absolute" v-if="isSmallScreen" style="top: 0; right: 0; padding: 2rem;" @click="toggleSidebar"><div class="fa-solid fa-ellipsis-vertical text-1"></div></div>
    <div class="flex-column center gap-2" style="padding: 2rem" v-if="newChat">
      <div class="subheading">Create a new Chat</div>
      <div class="text-3" v-if="this.subscription === 'basic'">Select a Ticker and a Year of interest</div>
      <div class="text-3" v-if="this.subscription === 'premium'">Select a Ticker, Year of interest, and a Filing Type</div>
      <div class="flex-row switch-row-to-column gap-1 width-100">
        <select class="input" @change="selectTicker($event.target.value)" v-model="selectedTicker">
          <option value="" disabled hidden selected>Ticker</option>
          <option v-for="option in tickerOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
        <select class="input" @change="selectYear($event.target.value)" v-model="selectedYear" :disabled="selectedTicker === ''">
          <option value="" disabled hidden selected>Year</option>
          <option v-for="option in yearOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
        <select class="input" @change="selectFiling($event.target.value)" v-model="selectedFiling" :disabled="selectedYear === ''" v-if="this.subscription === 'premium'">
          <option value="" disabled hidden selected>Filing</option>
          <option v-for="option in filingOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
      </div>
      <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
      <div class="button button-primary" @click="createChat">Create Chat</div>
      <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
      <div class="text-3">Or choose one of the Popular Filings</div>
      <div class="flex-row gap-1">
        <div class="flex-row gap-2 width-100" v-for="(filing, index) in (popularFilings)" :key="index">
          <div class="card card-clickable flex-column center">
            <div class="text-2">{{ filing.split("_")[0] }}</div>
            <div class="flex-row gap-05">
              <div class="text-4">{{ filing.split("_")[2] }}</div>
              <div class="text-4">{{ filing.split("_")[1] }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="sidebar flex-column gap-1 z-15 text-inter" v-if="sidebarShown" :style="isSmallScreen ? 'max-width: 18rem;' : 'max-width: 18rem;'">
      <div class="flex-column space-between height-100">
        <div class="flex-column gap-1">
          <div class="flex-row gap-2" style="padding-inline: 1rem;">
            <div @click="toggleNewChat" class="text-link text-2"><div class="fa-solid fa-file-pen"></div></div>
            <div @click="toggleProfile" class="text-link text-2"><div class="fa-solid fa-user"></div></div>
          </div>
          <div class="flex-column gap-1">
            <div class="text-bold" :class="isSmallScreen ? 'text-2' : 'text-3'" style="padding-inline: 1rem;">Chat History</div>
            <ul :style="{ height: chatHistoryHeight }" style="list-style-type: none; padding: 0" class="flex-column gap-05 chat-history">
              <li class="text-link text-4 chat-history-element" v-for="chat in chats" :key="chat" :class="{ active: currentChat === chat }" @click="selectChat(chat)">
                <div class="flex-row space-between" :class="isSmallScreen ? 'text-3' : 'text-4'" style="align-items: center;">{{ chat }}<div v-if="currentChat === chat" @click="toggleConfirmDeleteChat()" class="fa-solid fa-trash-can" style="color: var(--color-grey-dark)"></div></div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="flex-row width-100 gap-1 height-100" style="justify-content: center;  max-height: calc(100vh - 4rem);" :style="isSmallScreen ? '' : 'padding: 1rem 1rem 0rem 1rem;'" v-if="!newChat">
      <div v-if="!filingShown || !isSmallScreen" class="flex-column width-100 gap-1 center" style="max-width: 75rem;">
        <div class="chat-container text-inter height-100" ref="chatContainer">
          <div v-for="(message, index) in currentMessages" :key="index" :class="{'text-chat': message.role === 'assistant', 'text-chat': message.role === 'user'}">
            <div v-if="message.role === 'assistant'" class="width-100 flex-row gap-1">
              <div class="fa-solid fa-face-smile text-1"></div>
              <div class="text-chat chat-message-assistant" v-html="renderMarkdown(message.content)"></div>
            </div>
            <div v-else class="flex-row width-100" style="justify-content: flex-end;">
              <div class="chat-message-user text-chat">{{ message.content }}</div>
            </div>
          </div>
        </div>
        <div class="flex-row width-100 gap-1 show-on-large" style="max-width: 75rem; align-items: end;">
          <textarea 
            class="chat-input" 
            rows="1" 
            v-model="newMessage" 
            @keydown.enter.exact.prevent 
            @keyup.enter.exact="sendMessage('textareaLarge')"
            @input="adjustTextareaHeight('textareaLarge')" 
            style="resize: none;" 
            ref="textareaLarge"
            ></textarea>
          <div class="button-icon" @click="sendMessage('textareaLarge')"><div class="fa-solid fa-arrow-up" style="color: var(--color-grey-black)"></div></div>
          <div class="button-icon" @click="toggleFilingView"><div class="fa-solid fa-file-lines" style="color: var(--color-grey-black)"></div></div>
        </div>
      </div>
      <div class="filing-container flex-column center" ref="filingContainer" @scroll="handleScroll" v-if="filingShown" >
        <SpinnerCompInside v-if="filingLoading"></SpinnerCompInside>
        <div class="filing-html" v-if="!filingLoading" style="padding: 2rem;" v-html="filingContent"></div>
      </div>
    </div>
    <div class="flex-row width-100 gap-1 show-on-small" v-if="!newChat" style="max-width: 75rem; align-items: end; padding-inline: 1rem;">
      <textarea 
        class="chat-input" 
        rows="1" 
        v-model="newMessage" 
        @keydown.enter.exact.prevent 
        @keyup.enter.exact="sendMessage('textareaSmall')" 
        @input="adjustTextareaHeight('textareaSmall')" 
        style="resize: none;" 
        ref="textareaSmall"
        ></textarea>
      <div class="button-icon show-on-small" v-if="newMessage == ''" @click="toggleFilingView">
        <div class="fa-solid fa-file-lines" style="color: var(--color-grey-black)"></div>
      </div>
      <div class="button-icon" v-else @click="sendMessage('textareaSmall')">
        <div class="fa-solid fa-arrow-up" style="color: var(--color-grey-black)"></div>
      </div>
    </div>
    <div class="text-4 text-center" style="box-sizing: border-box;" v-if="!newChat">SECRag can make mistakes. Check important info.</div>
  </div>
</template>

<script>
import ProfileComp from '../components/ProfileComp.vue';
import SpinnerCompInside from '../components/SpinnerCompInside.vue';
import { config } from '@/config';
import { marked } from 'marked';
import { socket } from "@/socket";
import { mapState } from 'vuex';
import { ref } from 'vue';
import axios from 'axios';

export default {
  components: {ProfileComp, SpinnerCompInside},
  computed: {
    profileComp() {return this.showProfile ? 'ProfileComp' : null},
    ...mapState(['subscription']),
  },
  data() {
    return {
      filingContent: '',
      filingLoading: false,
      showProfile: false,
      popularFilings: [],
      chats: [],
      availableFilings: {},
      tickerInfo: {},
      tickerOptions: [],
      yearOptions: [],
      filingOptions: [],
      selectedTicker: '', // Initialize selected ticker
      selectedYear: '', // Initialize selected year
      selectedFiling: '',
      currentChat: '',
      currentMessages: [],
      newChat: true,
      newMessage: '',
      message: '',
      showConfirmDeleteChat: false,
      sidebarShown: true,
      filingShown: false,
      chatHistoryHeight: '0px',
      isSmallScreen: window.innerWidth <= 800, // Initial check for screen size
      llmResponseBuffer: '', // Buffer for storing incoming words
      assistantMessageIndex: null, // Index of the assistant message to update
      error: null,
      chatContainer: ref(null),
      filingContainer: ref(null),
      chatScrollPosition: 0,  // To store chat scroll position
      filingScrollPosition: 0 // To store filing scroll position
    };
  },
  mounted() {
    this.initializeSocket();
    this.loadListTickers();
    this.loadChats();
    this.updateChatHistoryHeight();
    if (this.isSmallScreen) {this.filingShown = false; this.sidebarShown = false;}
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    handleResize() {
      this.checkScreenWidth(); // Check screen width for responsiveness
      this.updateChatHistoryHeight(); // Update chat history height
    },
    
    selectTicker(option) {
      this.selectedTicker = option; 
      axios.get(`${config.apiUrl}/api/get-info-by-ticker`, {
        params: { token: localStorage.getItem('_u'), ticker: option }
      })
      .then(response => {
        this.tickerInfo = response.data.info
        this.yearOptions = Object.keys(this.tickerInfo);
      })
      .catch(error => {
        console.error('Error getting ticker info:', error);
      });
    },
    selectYear(option) {this.selectedYear = option; this.filingOptions = this.tickerInfo[this.selectedYear];},
    selectFiling(option) {this.selectedFiling = option;},
    initializeSocket() {
      socket.connect();
      socket.on("connect", () => {console.log("Socket connected: ", socket.id)});
      socket.on("disconnect", () => {console.log("Socket disconnected")});
      socket.on("llm_response", (data) => {
        if (data && data.word) {
          this.llmResponseBuffer += data.word; // Append new word to buffer
          this.updateAssistantMessage();
        }
      });
    },
    toggleProfile() {this.showProfile = !this.showProfile;},

    updateChatHistoryHeight() {
      // Calculate available height based on window size and fixed element heights
      let heightAdjustment = 0
      const headerHeight = 95; // Adjust based on your actual header/footer heights
      if (this.isSmallScreen) {heightAdjustment = 5;}
      const availableHeight = window.innerHeight - headerHeight + heightAdjustment; // Subtracting other elements' heights
      this.chatHistoryHeight = `${availableHeight}px`;
    },
    toggleFilingView() {
      this.filingShown = !this.filingShown;
      if (this.isSmallScreen && !this.filingShown) {this.$nextTick(() => {this.scrollToBottomInstant()})}
      if (this.filingShown) {

        // Optional: Introduce a small delay to allow for padding to apply
        setTimeout(() => {
          const offset = this.isSmallScreen ? 25 : 0; // Adjust as necessary
          this.$refs.filingContainer.scrollTop = this.filingScrollPosition + offset;
        }, 50); // Adjust the delay as needed
      
      }
    },
    checkScreenWidth() {
      this.isSmallScreen = window.innerWidth <= 800;
    },
    handleScroll(event) {
      this.filingScrollPosition = event.target.scrollTop;
    },
    loadListTickers() {
      axios.get(`${config.apiUrl}/api/get-list-tickers`, {
        params: { token: localStorage.getItem('_u') }
      })
      .then(response => {
        this.popularFilings = response.data.popularFilings;
        this.tickerOptions = response.data.tickers;
        // this.availableFilings = response.data.availableFilings;
      })
      .catch(error => {
        console.error('Error getting filing selection data:', error);
      });
    },

    loadChats() {
      axios.get(`${config.apiUrl}/api/get-chats`, {
        params: { token: localStorage.getItem('_u') }
      })
      .then(response => {
        this.chats = response.data.chats;
      })
      .catch(error => {
        console.error('Error getting chats:', error);
      });
    },

    selectChat(chat) {
      this.newChat = false;
      this.currentChat = chat;

      axios.get(`${config.apiUrl}/api/get-messages`, {
        params: { token: localStorage.getItem('_u'), 'chat': chat }
      })
      .then(response => {
        this.currentMessages = response.data.messages;
        // Scroll to bottom after messages are loaded
        this.$nextTick(() => {this.scrollToBottomInstant()});
      })
      .catch(error => {
        console.error('Error getting messages:', error);
      });

      this.filingLoading = true
      axios.get(`${config.apiUrl}/api/get-filing`, {
        params: { token: localStorage.getItem('_u'), 'chat': chat }
      })
      .then(response => {
        this.filingContent = response.data.html;
        this.filingLoading = false
      })
      .catch(error => {
        console.error('Error getting filing:', error);
      });

      if (this.isSmallScreen) {this.toggleSidebar();}
    },

    scrollToBottom() {
      const chatContainer = this.$refs.chatContainer;
      if (chatContainer) {
        chatContainer.scrollTo({
          top: chatContainer.scrollHeight,
          behavior: 'smooth' // This enables smooth scrolling
        });
      }
    },

    scrollToBottomInstant() {
      const chatContainer = this.$refs.chatContainer;
      if (chatContainer) {
        chatContainer.scrollTo({
          top: chatContainer.scrollHeight,
          behavior: 'instant' // This enables smooth scrolling
        });
      }
    },

    async sendMessage(refName) {
      // Check if the Enter key was pressed without Shift (allow Shift+Enter for new lines)

      if (this.isSmallScreen && this.filingShown) {this.toggleFilingView();}

      const textarea = this.$refs[refName]
      textarea.style.height = '40px'

      if (this.newMessage.trim() !== '') {
        // Add user message to currentMessages
        this.currentMessages.push({ role: 'user', content: this.newMessage });
        
        this.$nextTick(() => {
          this.adjustTextareaHeight('textareaSmall'); // Adjust the height after message is sent
        });

        let payloadMessage = this.newMessage;
        this.newMessage = ''; // Clear the input message

        this.$nextTick(() => {
          this.scrollToBottom(); // Scroll to the bottom after the message is added
        });

        // Prepare assistant response handling
        this.assistantMessageIndex = this.currentMessages.length;
        this.llmResponseBuffer = '';
        this.currentMessages[this.assistantMessageIndex] = { role: 'assistant', content: null };

        try {
          let response = await axios.post(`${config.apiUrl}/api/new-message`, {
            token: localStorage.getItem('_u'),
            chat: this.currentChat,
            message: payloadMessage
          });

          if (response.data.error) {
            alert(response.data.error);
            return;
          }

        } catch (error) {
          console.error('Error sending message:', error);
        }

        this.newChat = false; // Mark that we're in an active chat
      }
    },
    renderMarkdown(content) {
      if (!content) {return '';}
      return marked(content);
    },
    updateAssistantMessage() {
      // Update the existing assistant message
      
      if (this.assistantMessageIndex !== null) {
        if (this.llmResponseBuffer.trim()) {
          this.currentMessages[this.assistantMessageIndex].content = marked(this.llmResponseBuffer);
          this.$nextTick(() => {this.scrollToBottomInstant()});
        }
      }
    },
    adjustTextareaHeight(refName) {
      const textarea = this.$refs[refName]; // Access the specific textarea by its ref
      
      if (textarea) {
        textarea.style.height = 'auto'; // Reset the height to auto to get the correct scrollHeight
        textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px'; // Limit max-height to 160px
      }
    },



    toggleSidebar() {
      this.sidebarShown = !this.sidebarShown;
    },

    toggleNewChat() {
      this.newChat = true;
      this.currentMessages = [];
    },

    async createChat() {
      if (!this.selectedTicker || !this.selectedYear) {
        this.error =  'Please select both a ticker and a filing year.'
        return;
      }

      let newChatName = '';
      if (this.subscription === 'basic') {newChatName = `${this.selectedTicker}-${this.selectedYear}-10K`;} 
      else {
        let selectedFiling
        if (this.selectedFiling.split(' ')[0] === '10-Q') {selectedFiling = this.selectedFiling.split(' ')[0].replace('-', '') + this.selectedFiling.split(' ')[1].split('-')[1]}
        else {selectedFiling = this.selectedFiling.split(' ')[0]}
        newChatName = `${this.selectedTicker}-${this.selectedYear}-${selectedFiling.replace('-', '')}`}

      if (this.chats.includes(newChatName)) {
        this.error = 'Chat already exists';
        return;
      }

      this.chats.unshift(newChatName);

      try {
        let response = await axios.post(`${config.apiUrl}/api/new-chat`, {
          token: localStorage.getItem('_u'),
          chat: newChatName,
          filingDate: this.selectedFiling.split(' ')[1]
        });

        if (response.data.error) {
          alert(response.data.error);
          return;
        }

        this.selectChat(newChatName);
        this.newChat = false;
        this.selectedTicker = '';
        this.selectedYear = '';
        this.selectedFiling = '';
      } catch (error) {
        console.error('Error creating chat:', error);
      }
    },
    async deleteChat(chat) {
      let response = await axios.post(`${config.apiUrl}/api/delete-chat`, {
          token: localStorage.getItem('_u'),
          chat: chat
        });

      if (response.data.error) {
        alert(response.data.error);
        return;
      }

      this.showConfirmDeleteChat = false
      this.loadChats()
      this.newChat = true
    },
    toggleConfirmDeleteChat() {
      this.showConfirmDeleteChat = !this.showConfirmDeleteChat
    }
  }
};

</script>
<style scoped>

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}</style>