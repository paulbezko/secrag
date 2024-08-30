<template>
  <div>
    <div v-if="action==='linkExpired'" style="z-index: 40; position: absolute">
      <div class="card card-helper position-fixed" ref="successCard">
        <div class="heading-3">Link Expired</div>
        <div class="text-3">The email link has expired. Please retry with a new one.</div>
      </div>
    </div>
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
  methods: {
    closeCard() {this.$emit('close')},
    handleClickOutside(event) {if (!this.$refs.successCard.contains(event.target)) {this.closeCard(); this.$router.push('/')}
    }
  },
  mounted() {window.addEventListener('click', this.handleClickOutside);},
  beforeUnmount() {window.removeEventListener('click', this.handleClickOutside);}
}
</script>
