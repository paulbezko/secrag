<template>
  <div class="flex-column width-100" style="padding-inline: 2rem; height: 100vh; align-items: center">
    <NavbarComp :authenticated=isAuthenticated :subscribed=isSubscribed />
    <div class="flex-column center gap-2 height-100">
      <div class="heading">Uh Oh, 404</div>
      <div class="text-3">Seems like this page does not exist.</div>
      <router-link class="button button-primary" to="/">Back to Safety</router-link>
    </div>
  </div>
</template>

<script>
import NavbarComp from '../components/NavbarComp.vue';
import { mapState } from 'vuex';

export default {
  components: {
    NavbarComp
  },
  data() {return {
    pageLoaded: false,
    subscription: ''
  }},
  computed: {
    ...mapState(['isAuthenticated', 'isSubscribed']),
  },
}
</script>