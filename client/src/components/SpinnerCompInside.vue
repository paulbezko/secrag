<template>
  <div class="overlay">
    <div class="spinner">
      <div :class="['fa-solid', 'fa-arrows-rotate', customClass]"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SpinnerCompInside',
  props: {
    customClass: {
      type: String,
      default: '' // Default to an empty string if not provided
    }
  },
  mounted() {}
};
</script>

<style scoped>
.overlay {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  justify-content: center;
  align-items: center;
}

.spinner {
  position: relative;
}

.fa-arrows-rotate {
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>