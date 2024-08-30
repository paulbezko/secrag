<template>
  <div>
    <div v-if="action==='emailSentSignUp'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Email Sent</div>
        <div class="text-3">Check your email for the setup link.</div>
      </div>
    </div>
    <div v-if="action==='resetPasswordBefore'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Email Sent</div>
        <div class="text-3">Check your email for the reset link.</div>
      </div>
    </div>
    <div v-if="action==='resetPasswordAfter'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Reset Successful</div>
        <div class="text-3">You can now use your new password to login.</div>
      </div>
    </div>
    <div v-if="action==='changeName'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Success</div>
        <div class="text-3">Your name has been successfully changed.</div>
      </div>
    </div>
    <div v-if="action==='changeEmail'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Email Sent</div>
        <div class="text-3">Check your email for the confirmation link.</div>
      </div>
    </div>
    <div v-if="action==='changePassword'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Success</div>
        <div class="text-3">Your password has been successfully changed.</div>
      </div>
    </div>
    <div v-if="action==='emailSentContact'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Email Sent</div>
        <div class="text-3">Thank you for your message.</div>
        <div class="text-3">We will be in touch with you shortly.</div>
      </div>
    </div>
    <div v-if="action==='deleteAccount'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Account Deleted</div>
        <div class="text-3">Thank you being with us.</div>
        <div class="text-3">Hope to see you again!</div>
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
  methods: {
    closeCard() {this.$emit('close')},
    handleClickOutside(event) {if (!this.$refs.successCard.contains(event.target)) {this.closeCard()}
    }
  },
  mounted() {window.addEventListener('click', this.handleClickOutside);},
  beforeUnmount() {window.removeEventListener('click', this.handleClickOutside);}
}
</script>
