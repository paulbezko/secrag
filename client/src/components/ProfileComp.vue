<template>
  <div v-if="view === 'profile'" class="flex-column width-100 gap-1 center" style="padding-inline: 1rem">
    <div class="flex-row center gap-1 assistant-message single" style="height: 4rem; text-align: left;">
      <img
        :src="input !== '' 
          ? require('@/assets/dashboard/face_with_monocle_3d.png')
          : require('@/assets/dashboard/slightly_smiling_face_3d.png')"
        class="assistant-image"
      >
      <div v-if="userProfileUpdated === false" class="chat-text assistant-text" v-html="markdownify('This is what I know about you.<br>Feel free to adjust!')"></div>
      <div v-else class="chat-text assistant-text" v-html="markdownify('Thanks for correcting!<br>Your profile has been updated successfully.')"></div>
    </div>
    <div 
      ref="profileDiv"
      class="input-profile" 
      contenteditable="true" 
      :innerHTML="markdownify(userProfile)"
    ></div>
  </div>
</template>

<script>
import { messaging } from '@/utils/messaging.js';

export default {

  props: {
    view: String,
    input: String,
    userProfileUpdated: Boolean,
    userProfile: String,
  },

  methods: {
    markdownify(text) {
      return messaging.markdownify(text);
    }
  }
}
</script>