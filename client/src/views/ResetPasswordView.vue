<template>
  <div class="flex-column center width-100 gap-2" style="padding: 2rem">
    <div v-if="showSuccess"><SuccessComp :action="action" @close="handleCloseSuccess" /></div>
    <div v-if="showError"><ErrorComp :action="action" @close="handleCloseError"/></div>
    <div v-if="loaded && !showError" class="flex-column center width-100 gap-2">
      <div class="display display-flex-column center gap-1">
        <div class="heading">Reset Password</div>
        <div class="text-3" style="width: 25rem; text-align: center;">Enter a new password.</div>
        <div class="flex-column center gap-1 width-100" style="max-width: 40rem;">
          <input class="input" v-model="password" type="password" placeholder="Password">
          <div class="flex-row gap-1 width-100">
            <input class="input" v-model="passwordConfirm" type="password" placeholder="Confirm Password">
            <div @click="signupPassword('signUpAfter', $event)" class="button-icon"><SpinnerCompButton v-if="showSpinner"></SpinnerCompButton><div v-if="!showSpinner" class="fa-solid fa-arrow-right" style="color: var(--color-grey-black)"></div></div>
          </div>
          <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
        </div>
      </div>
    </div>
    <div v-if="showSuccess" class="backdrop z-30" @click="handleCloseConfirm"></div>
  </div>
</template>

<script>
import { passwordStrength } from 'check-password-strength'
import SuccessComp from '../components/SuccessComp.vue';
import ErrorComp from '../components/ErrorComp.vue';
import { config } from '@/config';
import axios from 'axios';

export default {
  components: {
    SuccessComp,
    ErrorComp,
  },
  data() {return {
    loaded: false,
    showError: false,
    action: '',
    error: '',
    token: '', 
    name: '', 
    password: '', 
    passwordConfirm: '', 
    showSuccess: false
  }},
  mounted() {
    this.token = new URLSearchParams(window.location.search).get('token') // Getting the token from the url

    if (this.token) {
      try {
        axios.get(`${config.apiUrl}/api/reset-password?token=${this.token}`)
          .then(response => {
            console.log(response.data.error)
            if (response.data.error) {this.action = response.data.error; this.showError = true; return}
            if (response.data.critical) {this.$router.push('/'); return} // Logout the user if token is not correct
            this.action = 'resetPasswordAfter'
          })
          .catch(error => {this.error = 'Error retrieving encrypted email:', error;});
      } catch (error) {this.error = 'Error retrieving encrypted email:', error;}
    }
    this.loaded = true
  },
  methods: {
    async submit() {

      if (this.password != this.passwordConfirm) {this.error = "Passwords do not match"; return}
      if (passwordStrength(this.password).id < 2) {this.error = "Password too weak"; return}

      const response = await axios.post(`${config.apiUrl}/api/reset-password`, {token: this.token, action: 'resetPasswordAfter', password: this.password})
      if (response.data.error) {this.error = response.data.error; return}
      this.action = 'resetPasswordAfter'
      this.showSuccess = true
    },
    handleCloseSuccess() {this.showSuccess = false; this.$router.push('/login')},
    handleCloseError() {this.showError = false},
  }
}
</script>
