<template>
  <div @mousemove="onMouseMove" @wheel="onScroll" class="page-container">
    <div ref="move" class="move fa-solid fa-skull text-2"></div>
  </div>
</template>

<script>
export default {
  name: 'MouseAttractedDiv',
  data() {
    return {
      scrollPosition: 0,
      lastScrollPosition: 0,
      hue: 0,
    };
  },
  methods: {
    onMouseMove(event) {
      const { clientX, clientY } = event;
      const moveElement = this.$refs.move;

      moveElement.style.left = `${clientX}px`;
      moveElement.style.top = `${clientY}px`;
    },
    onScroll(event) {
      // Update scroll positions
      this.lastScrollPosition = this.scrollPosition;
      this.scrollPosition = event.target.scrollTop;

      // Determine scroll direction
      const scrollDirection = this.scrollPosition > this.lastScrollPosition ? 'down' : 'up';

      // Adjust hue based on scroll direction
      if (scrollDirection === 'down') {
        this.hue += 5; // Increase hue value when scrolling down
      } else {
        this.hue -= 5; // Decrease hue value when scrolling up
      }

      // Ensure hue stays within 0-360 range
      if (this.hue >= 360) {
        this.hue -= 360;
      } else if (this.hue < 0) {
        this.hue += 360;
      }

      // Apply hue to the element
      const moveElement = this.$refs.move;
      moveElement.style.color = `hsl(${this.hue}, 70%, 50%)`;
    },
  },
};
</script>

<style scoped>
.page-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: auto; /* Enable scrolling */
}

.move {
  cursor: none;
  position: fixed;
  transform: translate(-50%, -50%);
  transition: color 0.3s ease; /* Smooth color transition */
}
</style>
