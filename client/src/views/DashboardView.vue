<template>
  <div class="display display-full display-flex-column">
    <NavbarComp :authenticated="true" :subscribed="true"/>
    
    <div class="display-flex-column center stretch" style="overflow: hidden;">
      <img src="../assets/img_dashboard.jpg" style="max-height: 80rem; max-width: 100%; display: block; border-radius: 2rem;" alt="image of a skeleton">
    </div>
  </div>
</template>

<script>
import NavbarComp from '../components/NavbarComp.vue';

export default {
  components: {NavbarComp},
}
</script>
