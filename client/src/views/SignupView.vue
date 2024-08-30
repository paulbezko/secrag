<template>
  <div class="display">
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div v-if="showSuccess"><SuccessComp :action="action" @close="handleCloseSuccess" /></div>
    <div class="display display-flex-column center" v-if="stage === 'signUpBefore'">
      <router-link to="/" class="fa-solid fa-xmark text text-1 text-link" style="position: absolute; top: 2rem; left: 2rem;"></router-link>
      <div class="display-flex-column center height-100">
        <div class="display-flex-column center gap-2" style="max-width: 24rem;">
          <div class="heading-2">Sign Up</div>
          <div class="text-3" style="width: 24rem; text-align: center;">Thank you for being an early adopter. To start enjoying the benefits, let's set up your account.</div>
          <div class="display-flex-column center gap-1 width-100">
            <div class="display-flex-row gap-1 width-100">
              <input class="input flex-1" v-model="email" type="email" placeholder="Email">
              <button @click="signupPassword('signUpBefore', $event)" class="fa-solid fa-arrow-right text-2 button-icon"></button>
            </div>
          </div>
          <div v-if="error" class="text-3 text-error">{{error}}</div>
          <div class="text-link text-3 display-flex-row bold gap-05 center" @click="signupGoogle()"><div class="fa-brands fa-google text-3"></div>Sign up with Google</div>
          <div class="text-3 text-center">By signing up you agree to our <router-link class="text text-3 text-link" to="/signup">Terms and Conditions.</router-link></div>
        </div>
      </div>
      <div class="text text-3 width-100 text-center" style="position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%)">Have an account already? <router-link class="text text-3 text-link bold" to="/login">Login</router-link></div>
      <div v-if="showSuccess" class="backdrop z-30" @click="handleCloseSuccess"></div>
    </div>
    <div v-if="stage === 'signUpAfter'">
      <div class="display display-flex-column center">
        <div class="display-flex-column center">
          <div style="display: flex; flex-direction: column; gap: 1rem; align-items: center; padding: 1rem;">
            <div class="heading-2">Sign Up</div>
            <div class="text-3" style="width: 24rem; text-align: center;">{{ signup_heading_1 }}</div>
            <div class="display-flex-column center gap-1 width-100">
              <input class="input" v-model="name" type="text" placeholder="Name">
              <input class="input" v-model="password" type="password" placeholder="Password">
              <div class="display-flex-row gap-1 width-100">
                <input class="input flex-1" v-model="passwordConfirm" type="password" placeholder="Confirm Password">
                <button @click="signupPassword('signUpAfter')" class="fa-solid fa-arrow-right text-2 button-icon"></button>
              </div>
            </div>
            <div v-if="error" class="text-3 text-error">{{error}}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import SuccessComp from '../components/SuccessComp.vue';
import SpinnerComp from '../components/SpinnerComp.vue';
import {createClient} from '@supabase/supabase-js'
import { passwordStrength } from 'check-password-strength'
import { config } from '@/config';

export default {
  components: {
    SuccessComp,
    SpinnerComp
  },
  data() {return {
    stage: '', 
    action: '',
    email: '',
    name: '', 
    password: '', 
    passwordConfirm: '',
    error: '', 
    showSuccess: false,
    showSpinner: false
  }},
  mounted() {
    const tokenUrl = new URLSearchParams(window.location.search).get('token') // Getting the token from the url
    const tokenLocalStorage = localStorage.getItem('_u')

    if (tokenUrl) {
      try {
        axios.get(`${config.apiUrl}/api/signup?token=${tokenUrl}`)
          .then(response => {

            if (response.data.critical) {this.$router.push('/'); return} // Logout the user if token is not correct
            if (response.data.error === 'linkExpired') {alert('Link expired'); this.$router.push('/'); return}
            
            localStorage.setItem('_u', response.data.token);
            this.stage = 'signUpAfter'
            this.$router.push('/signup')

          })
          .catch(error => {this.error = 'Error retrieving encrypted email:', error;});
      } catch (error) {this.error = 'Error retrieving encrypted email:', error;}
    }
    else if (tokenLocalStorage) {this.stage = 'signUpAfter'}
    else {this.stage = 'signUpBefore'}
  },

  methods: {
    async signupPassword(stage, event) {
      this.showSpinner = true
      
      if (stage === 'signUpBefore') {
        if (this.email === '') {this.error = "Please provide your email address"; this.showSpinner = false; return}
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {this.error = "Please provide a valid email address"; this.showSpinner = false; return} // Regex test for a valid email address

        const response = await axios.post(`${config.apiUrl}/api/signup`, {email: this.email})
        if (response.data.error) {this.email = ''; this.error = response.data.error; this.showSpinner = false; return}

        this.showSpinner = false;
        this.action = "emailSentSignUp"
        this.showSuccess = true; event.stopPropagation()
      }

      else if (stage === 'signUpAfter') {
        if (this.name === '') {this.error = "Please provide your name"; this.showSpinner = false; return}
        if (this.password === '') {this.error = "Please enter your password"; this.showSpinner = false; return}
        if (this.password != this.passwordConfirm) {this.error = "Passwords do not match"; this.showSpinner = false; return}
        if (passwordStrength(this.password).id < 2) {this.error = "Password too weak"; this.showSpinner = false; return}

        const response = await axios.post(`${config.apiUrl}/api/signup`, {token: localStorage.getItem('_u'), action: stage, name: this.name, password: this.password})
        if (response.data.error) {this.error = response.data.error; this.showSpinner = false; return} 
        localStorage.setItem('_u', response.data.token)
        this.$router.push('/subscribe')
      }
    },
    async signupGoogle() {
      const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpiemtzcWFrdG15bXJzcXJndmZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTg4MTkyNjQsImV4cCI6MjAzNDM5NTI2NH0.d2PgiDLfP5AVPBaJM_s--TgTfIAErZu0FmdHuPV-5Fs'
      const SUPABASE_URL = 'https://jbzksqaktmymrsqrgvfo.supabase.co'
      const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
      await supabase.auth.signInWithOAuth({provider: 'google', "options": {"redirectTo": `${config.webUrl}/handle-supabase`}})
    },
    handleCloseSuccess() {this.showSuccess = false; this.$router.push('/')},
  }
}
</script>
