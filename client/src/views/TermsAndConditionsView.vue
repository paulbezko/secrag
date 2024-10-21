<template>
<div v-if="pageLoaded" class="flex-column width-100" style="padding-inline: 2rem; height: 100vh; align-items: center">
  <NavbarComp :authenticated="isAuthenticated" :subscribed="isSubscribed" />
  <div class="flex-column center gap-2 height-100" style="flex-grow: 1; width: 100%; overflow-y: auto;">
    <div class="no-scrollbar" style="background-color: var(--color-grey-light); width: 100%; height: 100%; overflow-y: auto; padding: 2rem;">
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
  data() {return {
    pageLoaded: false,
    policy: 'terms_and_conditions',
    subscription: ''
  }},
  mounted() {
    this.pageLoaded = false
    axios.get(`${config.apiUrl}/api/get-policy`, {params: { 'policy': this.policy }})
      .then(response => {this.policy = marked(response.data); this.pageLoaded = true})
      .catch(error => {console.error('Error getting ticker info:', error);});
  },
  computed: {
    ...mapState(['isAuthenticated', 'isSubscribed']),
  },
  methods: {
    handleLinkClick(event) {
      const target = event.target;
      if (target.tagName === 'A') {
        event.preventDefault();
        const policyType = target.getAttribute('title');
        if (policyType) {this.fetchPolicy(policyType);}
      }
    },
    fetchPolicy(policyType) {
      axios.get(`${config.apiUrl}/api/get-policy`, {params: { 'policy': policyType }})
      .then(response => {this.policy = marked(response.data)})
      .catch(error => {console.error('Error getting ticker info:', error);});
    }
  }
}
</script>