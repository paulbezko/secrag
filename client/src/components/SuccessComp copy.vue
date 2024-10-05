<template>
  <div>
    <div v-if="action==='emailSentSignUp'" class="absolute z-40 width-100 flex-row center" style="padding-inline: 4rem;">
      <div class="card-component card-component-center flex-column center gap-2" ref="successCard" style="max-width: 40rem;">
        <div class="subheading text-center">Email Sent</div>
        <div class="text-3 text-center">Check your email for the setup link.</div>
      </div>
    </div>
    <div v-if="action==='resetPasswordBefore'" style="z-index: 40;" class="absolute card-component-center">
      <div class="card-component card-component-center flex-column center gap-2" ref="successCard" style="max-width: 40rem;">
        <div class="heading-3">Email Sent</div>
        <div class="text-3 text-color-semilight">Check your email for the reset link.</div>
      </div>
    </div>
    <div v-if="action==='resetPasswordAfter'" style="z-index: 40;" class="absolute card-component-center">
      <div class="card-component card-component-center flex-column center gap-2" ref="successCard" style="max-width: 40rem;">
        <div class="heading-3">Reset Successful</div>
        <div class="text-3 text-color-semilight">You can now use your new password to login.</div>
      </div>
    </div>
    <div v-if="action==='changeName'" style="z-index: 40;" class="absolute card-component-center">
      <div class="card-component card-component-center flex-column center gap-2" ref="successCard" style="max-width: 40rem;">
        <div class="heading-3">Success</div>
        <div class="text-3 text-color-semilight">Your name has been successfully changed.</div>
      </div>
    </div>
    <div v-if="action==='changeEmail'" style="z-index: 40;" class="absolute card-component-center">
      <div class="card-component card-component-center flex-column center gap-2" ref="successCard" style="max-width: 40rem;">
        <div class="heading-3">Email Sent</div>
        <div class="text-3 text-color-semilight">Check your email for the confirmation link.</div>
      </div>
    </div>
    <div v-if="action==='changePassword'" style="z-index: 40;" class="absolute card-component-center">
      <div class="card-component card-component-center flex-column center gap-2" ref="successCard" style="max-width: 40rem;">
        <div class="heading-3">Success</div>
        <div class="text-3 text-color-semilight">Your password has been successfully changed.</div>
      </div>
    </div>
    <div v-if="action==='emailSentContact'" style="z-index: 40;" class="absolute card-component-center">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Email Sent</div>
        <div class="text-3 text-color-semilight">Thank you for your message.</div>
        <div class="text-3 text-color-semilight">We will be in touch with you shortly.</div>
      </div>
    </div>
    <div v-if="action==='deleteAccount'" style="z-index: 40;" class="absolute card-component-center">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Account Deleted</div>
        <div class="text-3 text-color-semilight">Thank you being with us.</div>
        <div class="text-3 text-color-semilight">Hope to see you again!</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SuccessComp',
  props: {
    action: {
      type: String,
      required: true
    }
  },
  data() {return {
    messages: {
      'emailSentSignUp': {
        'heading': 'Email Sent',
        'text': 'Check your email for the setup link.'
      },
      'resetPasswordBefore': {
        'heading': 'Email Sent',
        'text': 'Check your email for the reset link.'
      },
      'resetPasswordAfter': {
        'heading': 'Reset Successful',
        'text': 'You can now use your new password to login.'
      },
      'changeName': {
        'heading': 'Success',
        'text': 'Your name has been successfully changed.'
      },
      'changeEmail': {
        'heading': 'Email Sent',
        'text': 'Check your email for the confirmation link.'
      },
      'changePassword': {
        'heading': 'Success',
        'text': 'Your password has been successfully changed.'
      },
    }
  }},
  methods: {
    closeCard() {this.$emit('close')},
    handleClickOutside(event) {if (!this.$refs.successCard.contains(event.target)) {this.closeCard();}
    }
  },
  mounted() {window.addEventListener('click', this.handleClickOutside);},
  beforeUnmount() {window.removeEventListener('click', this.handleClickOutside);}
}
</script>
