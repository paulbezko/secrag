<template>
  <div @mousemove="onMouseMove" @wheel="onScroll" class="page-container">
    <div id="1" ref="move1" class="move heading-2">Sign In</div>
    <input id="2" ref="move2" class="move input" placeholder="Email">
    <input id="3" ref="move3" class="move input" placeholder="Password" type="password">
    <div id="4" ref="move4" class="move button button-cta">Submit</div>
  </div>
</template>

<script>
export default {
  name: 'MouseAttractedDiv',
  data() {
    return {
      currentElementIndex: 1, // Start with the first element being selected
      elements: ['move1', 'move2', 'move3', 'move4'], // List of ref names
    };
  },
  methods: {
    onMouseMove(event) {
      const { clientX, clientY } = event;
      const moveElement = this.$refs[this.elements[this.currentElementIndex]];

      moveElement.animate({
        left: `${clientX}px`,
        top: `${clientY}px`
      }, {
        duration: 500,
        fill: "forwards"
      });
    },
    onScroll(event) {
      if (event.deltaY > 0) { // Scrolled down
        this.currentElementIndex = (this.currentElementIndex + 1) % this.elements.length;
        this.onMouseMove(event)
      } else { // Scrolled up
        this.currentElementIndex = (this.currentElementIndex - 1 + this.elements.length) % this.elements.length;
        this.onMouseMove(event)
      }
    }
  },
  
};
</script>



<style scoped>
.page-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.move {
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  position: fixed;
}
</style>