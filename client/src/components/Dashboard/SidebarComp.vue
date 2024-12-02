<template>
  <div class="sidebar flex-column gap-1 z-15 text-inter" v-if="sidebarShown" :style="isSmallScreen ? 'max-width: 18rem;' : 'max-width: 18rem;'">
    <div class="flex-column height-100">
      <div class="flex-column gap-05">
        <div class="flex-column gap-05" :class="isSmallScreen ? 'text-3' : 'text-4'">
          <router-link to="/" class="flex-row gap-05 sidebar-element menu" style="align-items: center;">
            <div class="fa-solid fa-house text-center sidebar-element-icon" style="min-width: 2rem;"></div>
            <div :class="isSmallScreen ? 'text-3' : 'text-4'">Homepage</div>
          </router-link>
          <div @click="toggleProfile" class="flex-row gap-05 sidebar-element menu" style="align-items: center;">
            <div class="fa-solid fa-user text-center sidebar-element-icon" style="min-width: 2rem; min-height: 2rem;"></div>
            <div :class="isSmallScreen ? 'text-3' : 'text-4'">Profile</div>
          </div>
          <div @click="toggleNewChat" class="flex-row gap-05 sidebar-element menu" style="align-items: center;" :class="{ active: newChat }">
            <div class="fa-solid fa-file-pen text-center sidebar-element-icon" style="min-width: 2rem;"></div>
            <div :class="isSmallScreen ? 'text-3' : 'text-4'">New Chat</div>
          </div>
        </div>
        <div class="width-100" style="padding-right: 0.5rem;"><hr class="width-100" style="border-top: 1px solid var(--color-grey);"></div>
        <div class="flex-column gap-1">
          <ul :style="{ height: chatHistoryHeight }" style="list-style-type: none; padding: 0" class="flex-column gap-05 chat-history">
            <li 
              class="text-4 sidebar-element text-link" 
              v-for="chat in chats" 
              :key="chat" 
              :class="{ active: currentChat === chat }" 
              @click="selectChat(chat)" 
              @mouseover="hoveredChat = chat" 
              @mouseleave="hoveredChat = null"
              >
              <div class="flex-row space-between" :class="isSmallScreen ? 'text-3' : 'text-4'" style="align-items: center; white-space: nowrap; overflow: hidden; ">
                <div style="max-width: 9rem; text-overflow: ellipsis;">{{ chat }}</div>
                <div class="flex-row gap-05">
                  <div v-if="hoveredChat === chat" @click="toggleConfirm('resetChat')" class="fa-solid fa-rotate-right icon-link-active sidebar-element-icon"></div>
                  <div v-if="hoveredChat === chat" @click="toggleConfirm('deleteChat')" class="fa-solid fa-trash-can icon-link-active sidebar-element-icon"></div>
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
</template>

<script>
export default {
  name: 'SidebarComp',

  props: {
    type: {
      type: String,
      required: true,
      validator(value) {
        return ['preview', 'full'].includes(value);
      },
    },
  },

  data() {
    return {
      sidebarShown: false,
      isSmallScreen: window.innerWidth <= 800,

      chats: [],
      newChat: true,
      chatHistoryHeight: '0px',
    };
  },

  mounted() {   
    if (!this.isSmallScreen) {this.sidebarShown = true;}
    this.updateChatHistoryHeight();
  },

  methods: {
    // Update Chat History Height
    updateChatHistoryHeight() {
      let heightAdjustment = 0
      const headerHeight = 155; 
      if (this.isSmallScreen) {heightAdjustment = -52;}
      const availableHeight = window.innerHeight - headerHeight + heightAdjustment;
      this.chatHistoryHeight = `${availableHeight}px`;
    },
  },
};
</script>