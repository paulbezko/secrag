<template>
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
        @input="$emit('update-textarea-height')"
      ></textarea>
      <div class="button-send" :class="{ 'button-send-disabled': view !== 'chat' }" v-if="!responseIsProcessing" @click="sendMessage(input)">
        <div class="icon fa-solid fa-arrow-up"></div>
      </div>
      <div class="button-send" v-else @click="$emit('stop-response')">
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
        @keyup.enter.exact="$emit('signup-email',inputEmail)"
      >
      <div class="flex-row center gap-1">
        <div class="button-send" :class="{ 'input-chat-disabled': responseIsProcessing }" @click="$emit('authenticate-with-google')">
          <div class="icon fa-brands fa-google"></div>
        </div>
        <div class="button-send" @click="$emit('signup-email',inputEmail)">
          <div class="icon fa-solid fa-arrow-up"></div>
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
          @keyup.enter.exact="$emit('signup-password', inputPassword, inputPasswordConfirm)"
        >
      </div>
      <div class="flex-row row-to-column center gap-1">
        <div class="button-send" @click="$emit('signup-password', inputPassword, inputPasswordConfirm)">
          <div class="icon fa-solid fa-arrow-up"></div>
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
          @keyup.enter.exact="$emit('login', inputEmail, inputPassword)"
        >
      </div>
      <div class="flex-row row-to-column center gap-1">
        <div class="button-send" :class="{ 'input-chat-disabled': responseIsProcessing }" @click="$emit('authenticate-with-google')">
          <div class="icon fa-brands fa-google"></div>
        </div>
        <div class="button-send" @click="$emit('login', inputEmail, inputPassword)">
          <div class="icon fa-solid fa-arrow-up"></div>
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
          @keyup.enter.exact="$emit('forgot-password', inputEmail)"
        >
      </div>
      <div class="button-send" @click="$emit('forgot-password', inputEmail)">
        <div class="icon fa-solid fa-arrow-up"></div>
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
          @keyup.enter.exact="$emit('reset-password', inputPassword, inputPasswordConfirm)"
        >
      </div>
      <div class="button-send" v-if="!responseIsProcessing" @click="$emit('reset-password', inputPassword, inputPasswordConfirm)">
        <div class="icon fa-solid fa-arrow-up"></div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'InputComp',
  props: {
    // input: String,
    view: String,
    inputMode: String,
    responseIsProcessing: Boolean,
  },
  data() {
    return {
      input: '',
      inputEmail: '',
      inputPassword: '',
      inputPasswordConfirm: ''
    }
  },
  methods: {
    sendMessage(input) {
      this.input = '';
      this.$emit('send-message', input);
    },
    stopResponse() {
      this.$emit('stop-response');
    }
  }
}
</script>