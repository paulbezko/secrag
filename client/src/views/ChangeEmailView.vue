<template>
  <div v-if="showError"><ErrorComp :action="action" @close="handleCloseError"/></div>
</template>

<script>
import axios from 'axios';
import ErrorComp from '../components/ErrorComp.vue';
import { config } from '@/config';

export default {
  components: {
    ErrorComp,
  },
  data() {return {
    showError: false,
    action: '', 
    token: ''
  }},
  mounted() {
    this.token = new URLSearchParams(window.location.search).get('token') // Getting the token from the url
    if (this.token) {
      try {
        axios.get(`${config.apiUrl}/api/change-email?token=${this.token}`)
          .then(response => {
            if (response.data.error) {this.action = response.data.error; this.showError = true; return}
            if (response.data.critical) {this.$router.push('/'); localStorage.removeItem('_u'); return} // Logout the user if token is not correct
            localStorage.setItem('_u', response.data.token)
            this.$router.push('/dashboard')
          })
          .catch(error => {this.error = 'Error retrieving encrypted email:', error;});
      } catch (error) {this.error = 'Error retrieving encrypted email:', error;}
    }
  },
  methods: {
    handleCloseError() {this.showError = false},
  }
}
</script>
