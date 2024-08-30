<template>
  <div v-if="pageLoaded" class="display display-flex-column center">
    <div class="display-margin display-flex-column center">
      <NavbarComp :authenticated="isAuthenticated()" :subscribed="isSubscribed()"/>
      <div class="display-flex-column stretch center">
        <div class="heading-1">About Us</div>
      </div>
    </div>
  </div>
</template>

<script>
import getNavbarInfo from '../main.js'
import NavbarComp from '../components/NavbarComp.vue';

export default {
  components: {
    NavbarComp
  },
  data() {return {
    pageLoaded: false,
    subscription: ''
  }},

  mounted() {
    getNavbarInfo().then(data => {this.subscription = data.subscription; this.pageLoaded = true})},
  methods: { // Adjust navbar accordingly
    isAuthenticated() {return localStorage.getItem('_u') !== null},
    isSubscribed() {return this.subscription},
  }
}
</script>