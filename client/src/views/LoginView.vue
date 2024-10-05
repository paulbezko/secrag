<template>
  <div class="flex-column width-100 center" style="padding-inline: 4rem;">
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div v-if="showConfirm"><ConfirmComp :action="action" @close="handleCloseConfirm" @success="handleSuccess" /></div>
    <div v-if="showSuccess"><SuccessComp :action="action" @close="handleCloseSuccess" /></div>
    <div v-if="showConfirm || showSuccess || showError" class="backdrop z-30" @click="handleCloseConfirm"></div>
    <router-link to="/" class="fa-solid fa-xmark text-1 text-link" style="position: absolute; top: 2rem; left: 2rem;"></router-link>
    <div class="flex-column center width-100 gap-4" style="max-width: 50rem;">
      <div class="heading text-center">Login to {{ projectName }}</div>
      <div class="text-2 text-center">If you gained access to {{ projectName }}, you can enter your credentials or login with your Google account.</div>
      <div class="flex-column center gap-2 width-100">
        <div class="flex-column gap-1 width-100" style="max-width: 40rem;">
          <input class="input" v-model="email" type="email" placeholder="Email">
          <div class="flex-row gap-1">
            <input class="input" v-model="password" type="password" placeholder="Password">
            <div @click="loginPassword()" class="button-icon"><div class="fa-solid fa-arrow-right" style="color: var(--color-grey-black)"></div></div>
          </div>
          <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
        </div>
        <div class="text-4 text-link discouraged" @click="resetPassword($event)">Forgot Password?</div>
        <div class="text-3 text-bold flex-row gap-1 center text-link" @click="loginGoogle()"><div class="fa-brands fa-google text-3"></div>Sign In with Google</div>
      </div>
    </div>
    <div class="text-4 flex-row center absolute width-100 gap-05" style="bottom: 2rem; left: 50%; transform: translateX(-50%)">
      No account yet? <router-link class="text-4 text-link" to="/signup">Sign Up</router-link>
    </div>
  </div>
</template>

<script>
import webdata from '../webdata.json'
import axios from 'axios';
import {createClient} from '@supabase/supabase-js'
import ConfirmComp from '../components/ConfirmComp.vue';
import SuccessComp from '../components/SuccessComp.vue';
import SpinnerComp from '../components/SpinnerComp.vue';
import {config} from '@/config';

export default {
  components: {
    ConfirmComp,
    SuccessComp,
    SpinnerComp
  },
  data() {return {
    projectName: webdata.projectName,
    email: '', 
    password: '', 
    action: '', 
    error: '',
    showConfirm: false,
    showSuccess: false,
    showError: false,
    showSpinner: false
  }},
  methods: {

    async loginPassword() {
      this.showSpinner = true
      this.error = false
      this.errorPassword = false
      if (this.email === '') {this.error =  "Please provide your email address"; this.showSpinner = false; return}
      if (this.password === '') {this.error =  "Please provide your password"; this.showSpinner = false; return}
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {this.error =  "Please provide a valid email address"; this.showSpinner = false; return} // Regex test for a valid email address

      const response = await axios.post(`${config.apiUrl}/api/login`, {type: 'password', email: this.email, password: this.password})
      if (response.data.error) {
        if (response.data.error === 'userNotFound') {this.error = "User not found"}
        else if (response.data.error === 'authMethodIncorrect') {this.error = "Incorrect authentication method"}
        else if (response.data.error === 'invalidCredentials') {this.error = "Invalid credentials"}
        this.password = ''; this.showSpinner = false; return
      }
      
      const token = response.data.token
      localStorage.setItem('_u', token)
      this.$router.push('/dashboard')
    },
    async loginGoogle() {
      
      const SUPABASE_KEY = webdata.supabaseKey
      const SUPABASE_URL = webdata.supabaseURL
      const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
      await supabase.auth.signInWithOAuth({provider: 'google', "options": {"redirectTo": `${config.webUrl}/handle-supabase`}})
    },

    resetPassword(event) {this.action = 'resetPasswordBefore'; this.showConfirm = true; event.stopPropagation()},
    handleSuccess() {this.showConfirm = false; this.showSuccess = true;},
    handleCloseConfirm() {this.showConfirm = false},
    handleCloseSuccess() {this.showSuccess = false},
  }
}
</script>
