<template>
  <div v-if="view === 'chat'" class="flex-column width-100 gap-2 no-scrollbar chat-container" id="chatContainer" style="overflow-y: auto;" :style="{ 'max-height': `${chatContainerHeight}px` }">
    <div v-for="(message, index) in chat" :key="index" class="flex-row center gap-1 width-100 chat-message">
      
      <!-- Assistant Message -->
      <div v-if="message.role === 'assistant'" :class="['flex-row', 'center', 'gap-1', 'row-to-column', chat.length === 1 ? 'assistant-message single' : 'assistant-message']">
        <img
          v-if="isLatestAssistantMessage(message)" 
          :src="input !== '' 
            ? require('@/assets/dashboard/face_with_monocle_3d.png'): (responseIsProcessing
              ? require('@/assets/dashboard/thinking_face_3d.png')
              : require('@/assets/dashboard/slightly_smiling_face_3d.png'))"
          class="assistant-image"
        />
        <img  v-if="!isLatestAssistantMessage(message)" :src="require('@/assets/dashboard/relieved_face_3d.png')"  class="assistant-image assistant-image-past"/>
        <div v-if="isLatestAssistantMessage(message) && responseFlowstep !== ''" class="chat-text assistant-text assistant-text-flowstep">{{ responseFlowstep }}</div>
        <div class="chat-text" :class="chat.length === 1 ? 'assistant-text single' : 'assistant-text'">
          <div v-for="(part, index) in processMessage(message)" :key="index">
            <div v-if="part.type === 'text'" v-html="part.content"></div>

            <!-- Widget generation -->
            <ApexChartsWidget v-else-if="part.type === 'treemap'" :theme="theme" :params="part.params" />
            <TradingViewWidget v-else-if="part.type === 'pricechart'" :theme="theme" :params="part.params" />
          </div>
        </div>
      </div>

      <!-- User Message -->
      <div v-else class="flex-row center gap-1 width-100 user-message">
        <div class="chat-text" v-html="markdownify(message.content)"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { messaging } from '@/utils/messaging.js';
import ApexChartsWidget from '@/widgets/ApexChartsWidget.vue';
import TradingViewWidget from '@/widgets/TradingViewWidget.vue';

export default {
  props: {
    chat: Array,
    view: String,
    input: String,
    responseIsProcessing: Boolean,
    responseFlowstep: String,
    theme: String,
    chatContainerHeight: Number,
  },
  components: {
    ApexChartsWidget,
    TradingViewWidget
  },
  methods: {

    isLatestAssistantMessage(message) {
      const assistantMessages = this.chat.filter(msg => msg.role === 'assistant');
      return assistantMessages.length > 0 && assistantMessages[assistantMessages.length - 1] === message;
    },
    
    processMessage(message) {
      const content = message.content;
      const widgets = message.widgets || [];
      const parts = [];
      let lastIndex = 0;

      if (widgets.length > 0) {
        widgets.forEach((widget) => {
          const placeholder = `[${widget.id}]`;
          const idx = content.indexOf(placeholder, lastIndex);
          if (idx > -1) {
            if (idx > lastIndex) {parts.push({ type: 'text', content: this.markdownify(content.substring(lastIndex, idx)) });}
            parts.push({ type: widget.type, params: widget.params });
            lastIndex = idx + placeholder.length;
          }
        });
      }

      if (lastIndex < content.length) {parts.push({ type: 'text', content: this.markdownify(content.substring(lastIndex)) });}
      return parts;
    },



    markdownify(text) {
      return messaging.markdownify(text);
    },

    chatScrollToBottom() {
      const chatContainer = document.getElementById('chatContainer');
      chatContainer.scrollTo({top: chatContainer.scrollHeight, behavior: 'smooth'});
    },
  }
};
</script>