<template>
  <div v-if="pageLoaded" class="flex-column width-100" style="height: 100vh; align-items: center">
    <!-- NavbarComp with ref to target the component -->
    <NavbarComp ref="navbar" class="navbar" :authenticated="isAuthenticated" :subscribed="isSubscribed" />
    
    <!-- Scrollable container with @scroll event -->
    <div class="flex-column center gap-2 height-100" style="flex-grow: 1; width: 100%; overflow-y: auto; padding-inline: 2rem; ">
      <div class="no-scrollbar" @scroll="handleScroll" style="background-color: var(--color-grey-light); width: 100%; height: 100%; overflow-y: auto; padding: 2rem;">
        <div class="text-3 policy" v-html="policy" @click="handleLinkClick" style="a {text-decoration: underline;}"></div>
      </div>
    </div>
  </div>
</template>

<script>
import NavbarComp from '../components/NavbarComp.vue';
import { mapState } from 'vuex';
import { config } from '@/config';
import { marked } from 'marked';
import axios from 'axios';

export default {
  components: {
    NavbarComp
  },
  data() {
    return {
      pageLoaded: false,
      policy: 'terms_and_conditions',
      subscription: ''
    };
  },
  computed: {
    ...mapState(['isAuthenticated', 'isSubscribed']),
  },
  mounted() {
    // Fetch the policy on mount
    this.pageLoaded = false;
    axios
      .get(`${config.apiUrl}/api/get-policy`, { params: { policy: this.policy } })
      .then((response) => {
        this.policy = marked(response.data);
        this.pageLoaded = true;
      })
      .catch((error) => {
        console.error('Error getting ticker info:', error);
      });
  },
  methods: {
    handleLinkClick(event) {
      const target = event.target;
      if (target.tagName === 'A') {
        event.preventDefault();
        const policyType = target.getAttribute('title');
        if (policyType) {
          this.fetchPolicy(policyType);
        }
      }
    },
    fetchPolicy(policyType) {
      axios
        .get(`${config.apiUrl}/api/get-policy`, { params: { policy: policyType } })
        .then((response) => {
          this.policy = marked(response.data);
        })
        .catch((error) => {
          console.error('Error getting ticker info:', error);
        });
    },
    handleScroll(event) {
      // Get the container element that is scrolling
      const scrollContainer = event.target;
      // Get the navbar reference
      const navbar = this.$refs.navbar.$el; // Access the DOM element of the NavbarComp
      
      // Check if user has scrolled down
      if (scrollContainer.scrollTop > 0) {
        navbar.classList.add('shadow');
      } else {
        navbar.classList.remove('shadow');
      }
    }
  }
};
</script>

<style scoped>
.shadow {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
</style>
