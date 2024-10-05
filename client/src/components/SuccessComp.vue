<template>
  <div class="card-component card-component-center z-40 flex-column gap-2 center width-100 card-size-success" style="max-width: 28rem;">
    <div class="subheading text-center">{{ messages[action].heading }}</div>
    <div v-for="(text, index) in messages[action].text" :key="index" class="text-3 text-center">{{ text }}</div>
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
        'text': ['Check your email for the setup link.']
      },
      'resetPasswordBefore': {
        'heading': 'Email Sent',
        'text': ['Check your email for the reset link.']
      },
      'resetPasswordAfter': {
        'heading': 'Reset Successful',
        'text': ['You can now use your new password to login.']
      },
      'changeName': {
        'heading': 'Success',
        'text': ['Your name has been successfully changed.']
      },
      'changeEmail': {
        'heading': 'Email Sent',
        'text': ['Check your email for the confirmation link.']
      },
      'changePassword': {
        'heading': 'Success',
        'text': ['Your password has been successfully changed.']
      },
      'emailSentContact': {
        'heading': 'Email Sent',
        'text': ['Thank you for your message.', ' We will be in touch with you shortly.']
      },
      'deleteAccount': {
        'heading': 'Account Deleted',
        'text': ['Thank you being with us.', ' Hope to see you again!']
      }
    }
  }},
  methods: {
    handleClickOutside() {this.$emit('close')}
  },
  mounted() {window.addEventListener('click', this.handleClickOutside);},
  beforeUnmount() {window.removeEventListener('click', this.handleClickOutside);}
}
</script>
