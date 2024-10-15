<template>
  
  <div class="flex-column flex-1 width-100 center" style="padding-inline: 4rem;">
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div v-if="showSuccess"><SuccessComp :action="action" @close="handleCloseSuccess"/></div>
    <div v-if="showSuccess" class="backdrop z-30" @click="handleCloseConfirm"></div>
    <div v-if="stage === 'signUpBefore'" class="flex-column width-100 flex-1 space-between gap-2">
      <div></div>
      <div class="flex-column center">
        <router-link to="/" class="fa-solid fa-xmark text-1" style="position: absolute; top: 2rem; left: 2rem;"></router-link>
        <div class="flex-column center width-100 gap-2" style="max-width: 50rem;">
          <div class="heading text-center">Welcome to {{ projectName }}</div>
          <div class="text-2 text-center">Thank you for being an early adopter. To start enjoying the benefits, let's set up your account.</div>
          <div class="flex-column center gap-2 width-100" style="max-width: 40rem;">
            <div class="flex-row gap-1 width-100">
              <input class="input" v-model="email" type="email" placeholder="Email">
              <div @click="signupPassword('signUpBefore', $event)" class="button-icon"><div class="fa-solid fa-arrow-right" style="color: var(--color-grey-black)"></div></div>
            </div>
            <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
          </div>
          <div class="text-3 text-bold flex-row gap-1 center text-link" @click="signupGoogle()"><div class="fa-brands fa-google text-3"></div>Sign In with Google</div>
        </div>
      </div>
      <div class="text-4 flex-column center width-100 gap-05" style="padding-bottom: 1rem">
        <div class="flex-row center gap-05">Have an account already? <router-link class="text-4 text-link" to="/login">Login</router-link></div>
        <div class="text-4 text-center">By signing up you agree to our <router-link to="/terms-and-conditions" class="text-4">Terms and Conditions</router-link></div>
      </div>
    </div>
    <div v-if="stage === 'signUpAfter'" class="display display-flex-column center">
      <div class="flex-column center width-100 gap-2" style="max-width: 50rem;">
        <div class="heading text-center">Welcome to {{ projectName }}</div>
        <div class="text-2 text-center">Thank you for being an early adopter. To start enjoying the benefits, let's set up your account.</div>
        <div class="flex-column center gap-1 width-100" style="max-width: 40rem;">
          <input class="input" v-model="name" type="text" placeholder="Name">
          <input class="input" v-model="password" type="password" placeholder="Password">
          <div class="flex-row gap-1 width-100">
            <input class="input" v-model="passwordConfirm" type="password" placeholder="Confirm Password">
            <div @click="signupPassword('signUpAfter', $event)" class="button-icon"><div class="fa-solid fa-arrow-right" style="color: var(--color-grey-black)"></div></div>
          </div>
          <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import webdata from '../webdata.json'
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
    projectName: webdata.projectName,
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
      const SUPABASE_KEY = webdata.supabaseKey
      const SUPABASE_URL = webdata.supabaseURL
      const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
      await supabase.auth.signInWithOAuth({provider: 'google', "options": {"redirectTo": `${config.webUrl}/handle-supabase`}})
    },
    handleCloseSuccess() {this.showSuccess = false; this.$router.push('/')},
  }
}
</script>
