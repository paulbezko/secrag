<template>
  <div v-if="pageLoaded" class="display display-flex-column center">
    <div class="display-margin display-flex-column center">
      <NavbarComp :authenticated="isAuthenticated()" :subscribed="this.subscription"/>
      <div class="display-flex-row stretch" style="gap: 4rem;">
        <div class="display-flex-column stretch center">
          <div class="display-flex-column show-on-large gap-2 align-left">
            <div class="display-flex-column">
              <div class="heading-1">SEC filings, embedded</div>
            </div>
            <div class="text-1">
              Take fundamental security analysis to another level through large language model integration.
            </div>
            <router-link class="button button-cta" to="/signup">Sign Up</router-link>
          </div>
          <div class="display-flex-column show-on-small gap-2 center text-center width-100">
            <img src="../assets/img_home.png" style="max-width: 28rem; width: 100%; aspect-ratio: 1; border-radius: 2rem;" alt="image of a skeleton playing a trombone">
            <div class="display-flex-column center width-100">
              <div class="heading-1">SEC filings, embedded</div>
            </div>
            <div class="text-1" style="max-width: 40rem">
              Take fundamental security analysis to another level through large language model integration.
            </div>
            <router-link class="button button-cta" to="/signup">Sign Up</router-link>
          </div>
        </div>
        <div class="display-flex-column stretch center show-on-large">
          <img src="../assets/img_home.png" style="width: 100%; aspect-ratio: 1; border-radius: 2rem;" alt="image of a skeleton playing a trombone">
        </div>
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
  data() { return {
    pageLoaded: false,
    subscription: '',
    test: 'ass'
  }},
  mounted() {
    this.pageLoaded = false
    getNavbarInfo().then(data => {this.subscription = data.subscription; this.pageLoaded = true;})
  },
  methods: {
    isAuthenticated() {return localStorage.getItem('_u') !== null}
  }
}
</script>
