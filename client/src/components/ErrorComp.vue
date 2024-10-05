<template>
  <div class="card-component card-component-center z-40 flex-column gap-2 center card-size-error" style="max-width: 40rem;" ref="errorCard">
    <div class="flex-row center gap-1">
      <div class="text-3 fa-solid fa-triangle-exclamation" style="color: var(--color-red)"></div>
      <div class="text-3 text-bold text-center" style="color: var(--color-red)">{{ actions[action].heading }}</div>
    </div>
    <div class="text-3 text-center">{{ actions[action].text }}</div>
  </div>
</template>

<script>
export default {
  name: 'ErrorComp',
  props: {
    action: {
      type: String,
      required: true
    }
  },
  data() {return {
    actions: {
      'linkExpired': {
        'heading': 'Link Expired',
        'text': 'This email link has expired. Please retry with a new one.'
      },
      'authMethodIncorrect': {
        'heading': 'Incorrect Authentication Method',
        'text': 'The account was created using a different authentication method. Please retry with another one.'
      }
    }
  }},
  methods: {
    closeCard() {this.$emit('close')},
    handleClickOutside(event) {
      if (!this.$refs.errorCard.contains(event.target)) {
        if (this.action === 'linkExpired' || this.action === 'authMethodIncorrect') {this.closeCard(); this.$router.push('/')}
        else {this.closeCard()}
      }
    }
  },
  mounted() {window.addEventListener('click', this.handleClickOutside)},
  beforeUnmount() {window.removeEventListener('click', this.handleClickOutside);}
}
</script>
