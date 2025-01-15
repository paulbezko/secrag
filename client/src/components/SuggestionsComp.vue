<template>
  <div class="flex-row center gap-1 width-100" style="justify-content: space-between; padding-left: 1rem;" :class="{ 'input-suggestion-disabled': responseIsProcessing }">
    
    <!-- Organic suggestions -->
    <div v-if="premadeSuggestionsShown && isMobile"></div>
    <div class="flex-row center" v-if="!premadeSuggestionsShown && isMobile || !isMobile" :class="isMobile ? 'gap-1' : 'gap-15'">
      <div v-if="inputMode === 'default'" class="flex-row center" :class="isMobile ? 'gap-1' : 'gap-15'">
        <div v-for="(prompt, index) in organicSuggestions" :key="index" class="input-suggestion" @click="this.$emit('send-message', prompt)">{{ prompt }}</div>
      </div>
      <div class="input-suggestion" v-if="inputMode === 'login' || inputMode === 'signup_email'" @click="$emit('switch-to-default-input')">Go back</div>
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
        @click="$emit('toggle-premade-suggestions-visibility')"
        >
      </div>
      <div v-else style="width: 4rem;"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SuggestionsComp',
  props: {
    isMobile: Boolean,
    userStatus: String,
    inputMode: String,
    organicSuggestions: Array,
    premadeSuggestions: Array,
    premadeSuggestionsShown: Boolean,
    responseIsProcessing: Boolean,
  },
}
</script>