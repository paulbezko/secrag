<template>
  <div v-if="pageLoaded" class="display display-flex-column center">
    <div class="display-margin display-flex-column center">
      <NavbarComp :authenticated="isAuthenticated()" :subscribed="isSubscribed()"/>
      <div class="display-flex-column stretch center">
        <div class="heading-1">Frequently Asked Questions</div>
      </div>
    </div>
    <div class="text text-3 position-absolute width-100 text-center" style="bottom: 2rem; left: 50%; transform: translateX(-50%)">Still have a question? <router-link class="text text-3 text-link bold" to="/contact">Contact Us</router-link></div>
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