<template>
  <div v-if="pageLoaded" class="display display-flex-column center">
    <div class="display-margin display-flex-column center">
      <NavbarComp :authenticated="isAuthenticated()" :subscribed="isSubscribed()"/>
      <div class="display-flex-column stretch center gap-1">
        <div class="heading-1">Uh Oh, 404</div>
        <div class="text-3">Seems like this page does not exist.</div>
        <router-link class="button button-cta" to="/">Back to Safety</router-link>
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