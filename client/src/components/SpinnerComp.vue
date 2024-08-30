<template>
  <div class="overlay">
    <div class="spinner">
      <div class="fa-solid fa-arrows-rotate heading-2"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SpinnerComp',
  mounted() {}
};
</script>

<style scoped>
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  backdrop-filter: blur(4px); /* Adjust the value as needed */
  /* background-color: rgba(0, 0, 0, 0.5); */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.spinner {
  position: relative;
}

.fa-arrows-rotate {
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  from {transform: rotate(0deg)}
  to {transform: rotate(360deg)}
}
</style>