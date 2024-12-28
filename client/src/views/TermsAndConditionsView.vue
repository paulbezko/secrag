<template>
  <div v-if="pageLoaded" class="flex-column width-100 height-100vh center" style="font-family: 'Inter', sans-serif; color: var(--black)">
    <div class="flex-column center gap-2 height-100 width-100" style="flex-grow: 1; padding: 2rem; ">
      <div class="text-3 policy" v-html="policy" @click="handleLinkClick" style="a {text-decoration: underline;}"></div>
    </div>
  </div>
</template>

<script>
import { config } from '@/config';
import { marked } from 'marked';
import axios from 'axios';

export default {
  data() {
    return {
      pageLoaded: false,
      policy: 'terms_and_conditions',
      subscription: ''
    };
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
    }
  }
};
</script>

<style scoped>
.shadow {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
</style>
