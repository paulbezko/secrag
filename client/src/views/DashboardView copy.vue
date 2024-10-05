<template>
  <div class="display display-full display-flex-column center gap-1">


      <Transition name="slide">
        <div v-if="sidebarShown" class="sidebar display-margin" style="position:absolute; left: 0; top: 0; z-index: 10;">
          <button @click="toggleSidebar" :class="sidebarShown ? 'fa-solid fa-square-caret-left text-1 text-link text-color-semilight' : ''" style="position:absolute; left: 0; top:0; margin: 2rem; padding: 0"></button>
          <button @click="toggleNewChat" :class="sidebarShown ? 'fa-solid fa-square-pen text-1 text-link text-color-semilight' : ''" style="position:absolute; right: 0; top:0; margin: 2rem; padding: 0"></button>
          <div class="text text-2 text-color-semilight">Chat History</div>
          <ul>
            <li class="text-link text-3" 
                v-for="topic in topics" 
                :key="topic" 
                @click="selectTopic(topic)">
              {{ topic }}
            </li>
          </ul>
        </div>
      </Transition>

      <button @click="toggleSidebar" :class="sidebarShown ? '' : 'fa-solid fa-square-caret-right text-1 text-link text-color-semilight'" style="position:absolute; left: 0; top: 0; margin: 2rem; padding: 0"></button>



    
    <div class="display-margin display-flex-column center gap-2">

      <div class="chat-container card">

        <div v-if="newChat">
          <div class="text text-3 text-color-semilight">Select a ticker of your interest</div>
          <select v-model="selectedTicker">
            <option v-for="option in tickerOptions" :key="option" :value="option">{{ option }}</option>
          </select>

          <div class="text text-3 text-color-semilight">Select a filing year</div>
          <select v-model="selectedYear">
            <option v-for="option in filingYearOptions" :key="option" :value="option">{{ option }}</option>
          </select>

          <button class="button button-cta" @click="createChat">Create</button>
        </div>

        <div class="chat-message" v-for="(message, index) in currentMessages" :key="index" :class="{'assistant-message text text-3': message.role === 'assistant', 'user-message text text-3': message.role === 'user'}">
          <div v-if="message.role === 'assistant'" class="message-content" style="display: flex; align-items: center;">
            <i class="fa-solid fa-face-smile text-1" style="margin-right: 1.5rem;"></i>
            <p>{{ message.content }}</p>
          </div>
          <div v-else class="message-content">
            <p>{{ message.content }}</p>
          </div>
        </div>
      </div>



    </div>

    <div class="display-flex-row gap-1" style="position: relative;">
      <input class="input flex-1" type="text" v-model="newMessage" @keyup.enter="sendMessage" style="padding-right: 40px; width: 40rem;" placeholder="Type your message here..."/>
      <button @click="sendMessage" class="fa-solid fa-arrow-right text-2 button-icon text-color-semilight" style="position: absolute; right: 0; top: 50%; transform: translateY(-50%); border: 0; background-color: transparent;"></button>
    </div>
    <div class="text-3 text-color-semilight">SecRag can make mistakes. Check important info.</div>

  </div>
</template>

<script>
import { config } from '@/config';
import { socket } from "@/socket";
import axios from 'axios';

export default {
  data() {
    return {
      topics: [],
      tickerOptions: ['AAPL', 'TSLA', 'AMZN'],
      filingYearOptions: ['2021', '2022', '2023'],
      selectedTicker: '', // Initialize selected ticker
      selectedYear: '', // Initialize selected year
      currentTopic: '',
      currentMessages: [],
      newMessage: '',
      sidebarShown: true,
      newChat: true,
      llmResponseBuffer: '', // Buffer for storing incoming words
      assistantMessageIndex: null, // Index of the assistant message to update
    };
  },
  mounted() {
    this.initializeSocket();
    this.loadTopics();
  },
  methods: {
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

    loadTopics() {
      axios.get(`${config.apiUrl}/api/get-topics`, {
        params: { token: localStorage.getItem('_u') }
      })
      .then(response => {
        this.topics = response.data.topics;
      })
      .catch(error => {
        console.error('Error getting topics:', error);
      });
    },

    selectTopic(topic) {
      this.newChat = false;
      this.currentTopic = topic;
      axios.get(`${config.apiUrl}/api/get-messages`, {
        params: { token: localStorage.getItem('_u'), topic: topic }
      })
      .then(response => {
        this.currentMessages = response.data.messages;
      })
      .catch(error => {
        console.error('Error getting messages:', error);
      });
    },

    async sendMessage() {
      if (this.newMessage.trim() !== '') {
        // Add user message to currentMessages
        this.currentMessages.push({ role: 'user', content: this.newMessage });
        let payloadMessage = this.newMessage;
        this.newMessage = '';

        this.assistantMessageIndex = this.currentMessages.length;
        this.currentMessages[this.assistantMessageIndex] = {role: 'assistant', content: null}

        try {
          let response = await axios.post(`${config.apiUrl}/api/new-message`, {
            token: localStorage.getItem('_u'),
            topic: this.currentTopic,
            message: payloadMessage
          });

          if (response.data.error) {
            alert(response.data.error);
            return;
          }

          this.llmResponseBuffer = ''

        } catch (error) {
          console.error('Error sending message:', error);
        }

        this.newChat = false;
      }
    },

    updateAssistantMessage() {
      // Update the existing assistant message
      
      if (this.assistantMessageIndex !== null) {
        if (this.llmResponseBuffer.trim()) {
          this.currentMessages[this.assistantMessageIndex].content = this.llmResponseBuffer;
        }
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
        alert('Please select both a ticker and a filing year.');
        return;
      }

      const newTopicName = `${this.selectedTicker}-${this.selectedYear}`;

      if (this.topics.includes(newTopicName)) {
        alert('This topic already exists.');
        return;
      }

      this.topics.push(newTopicName);

      try {
        let response = await axios.post(`${config.apiUrl}/api/new-chat`, {
          token: localStorage.getItem('_u'),
          topic: newTopicName
        });

        if (response.data.error) {
          alert(response.data.error);
          return;
        }

        this.selectTopic(newTopicName);
        this.newChat = false;
        this.selectedTicker = '';
        this.selectedYear = '';
      } catch (error) {
        console.error('Error creating chat:', error);
      }
    }
  }
};
</script>
<style scoped>

.sidebar {
  padding-block: 6rem;
  padding-inline: 2rem;
  width: 200px;
  background-color: #272727;
  border-right: 1px solid #ddd;
}

.sidebar ul {
  padding: 0;
  list-style: none;
}

.sidebar li {
  padding-block: 1rem;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
}

.chat-container {
  background: var(--color-grey-darker);
  margin-top: 2rem;
  width: 100%;
  max-width: 600px;
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-radius: 20px;
  overflow-y: scroll; /* Allows content to scroll */
}

.chat-container::-webkit-scrollbar {
  display: none;
}

.chat-message {
  padding-inline: 2rem;
  max-width: 75%;
  line-height: 2;
}

.assistant-message {
  background: #3b3b3b;
  border-radius: 1rem;
  align-self: flex-start;
}

.user-message {
  background: #212121;
  border-radius: 1rem;
  align-self: flex-end;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}

</style>