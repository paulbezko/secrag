<template>
  <div class="overlay">
    <div class="spinner">
      <div class="fa-solid fa-arrows-rotate text-3"></div>
    </div>
  </div>
</template>

<script>
export default {name: 'SpinnerCompButton', mounted() {}};
</script>

<style scoped>
.overlay {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.spinner {position: relative;}
.fa-arrows-rotate {animation: spin 1s ease-in-out infinite;}

@keyframes spin {
  from {transform: rotate(0deg)}
  to {transform: rotate(360deg)}
}
</style>