<template>
  <div class="display">
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div v-if="showConfirm"><ConfirmComp :action="action" @close="handleCloseConfirm" @success="handleSuccess" /></div>
    <div v-if="showSuccess"><SuccessComp :action="action" @close="handleCloseSuccess" /></div>
    <div v-if="showConfirm || showSuccess" class="backdrop z-30" @click="handleCloseConfirm"></div>
    <div class="display display-flex-column center gap-2">
      <router-link to="/" class="fa-solid fa-xmark text text-1 text-link" style="position: absolute; top: 2rem; left: 2rem;"></router-link>
      <div class="display-flex-column center">
        <div class="display-flex-column center gap-2" style="max-width: 24rem;">
          <div class="heading-2">Login</div>
          <div class="text-3 text-center">If you gained access to SkelTal, you can enter your credentials or login with your Google account.</div>
          <div class="display-flex-column gap-1 width-100">
            <input class="input" v-model="email" type="email" placeholder="Email">
            <div class="display-flex-row gap-1">
              <input class="input flex-1" v-model="password" type="password" placeholder="Password">
              <button @click="loginPassword()" class="fa-solid fa-arrow-right text-2 button-icon"></button>
            </div>
          </div>
          <div v-if="error" class="text-3 text-error">{{error}}</div>
          <div v-if="errorPassword" class="text-3 text-error">Invalid credentials</div>
          <div class="text-3 text-link bold" @click="resetPassword($event)">Forgot password?</div>

        </div>
      </div>
      <div class="text-link text-3 display-flex-row bold gap-05 center" @click="loginGoogle()"><div class="fa-brands fa-google text-3"></div>Sign in with Google</div>
      <div class="text text-3 position-absolute width-100 text-center" style="bottom: 2rem; left: 50%; transform: translateX(-50%)">No account yet? <router-link class="text text-3 text-link bold" to="/signup">Sign Up</router-link></div>
    </div>
  </div>
</template>

<script>
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
    email: '', 
    password: '', 
    action: '', 
    error: '',
    errorPassword: false,
    showConfirm: false,
    showSuccess: false,
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
    
      if (response.data.error === 'Invalid credentials') {this.errorPassword = true; this.password = ''; this.showSpinner = false; return}
      else if (response.data.error) {this.error =  response.data.error; this.password = ''; this.showSpinner = false; return}
      
      const token = response.data.token
      localStorage.setItem('_u', token)
      this.$router.push('/dashboard')
    },
    async loginGoogle() {
      
      const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpiemtzcWFrdG15bXJzcXJndmZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTg4MTkyNjQsImV4cCI6MjAzNDM5NTI2NH0.d2PgiDLfP5AVPBaJM_s--TgTfIAErZu0FmdHuPV-5Fs'
      const SUPABASE_URL = 'https://jbzksqaktmymrsqrgvfo.supabase.co'
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
