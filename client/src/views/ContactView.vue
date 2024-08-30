<template>
  <div class="display display-flex-column center">
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div v-if="showSuccess"><SuccessComp :action="action" @close="handleCloseSuccess" /></div>
    <div v-if="showSuccess" class="backdrop z-30" @click="handleCloseSuccess"></div>
    <div class="display-margin display-flex-column center">
      <NavbarComp :authenticated="isAuthenticated()" :subscribed="isSubscribed()"/>
      <div class="display-flex-column stretch center gap-2">
        <div class="heading-1">Contact Us</div>
        <div class="display-flex-column width-100 center gap-1">
          <input class="input" v-model="name" style="max-width: 40rem" placeholder="Name">
          <input class="input" v-model="email" style="max-width: 40rem" placeholder="Email">
          <textarea class="input" v-model="message" style="max-width: 40rem; height: 24rem;" placeholder="Message"></textarea>
          <div class="button button-cta" @click="submit($event)" style="max-width: 40rem; width: 100%; box-sizing: border-box; text-align: center;">Submit</div>
          <div v-if="error" class="text-3 text-error">{{error}}</div>
          <div class="text-3">Or send us an email at skeleton@skeleton.com</div>
          <button style="display: none" type="submit"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import getNavbarInfo from '../main.js'
import NavbarComp from '../components/NavbarComp.vue';
import SuccessComp from '../components/SuccessComp.vue';
import SpinnerComp from '../components/SpinnerComp.vue';
import { config } from '@/config';

export default {
  components: {
    NavbarComp,
    SuccessComp,
    SpinnerComp
  },
  data() {return {
    pageLoaded: false,
    action: null,
    error: null,
    subscription: '',
    email: null,
    name: null,
    message: null,
    showSuccess: false,
    showSpinner: false
  }},

  mounted() {getNavbarInfo().then(data => {this.subscription = data.subscription; this.pageLoaded = true})},
  methods: { // Adjust navbar accordingly
    async submit(event) {
      
      this.action = 'emailSentContact'
      this.error = false
      if (this.name === '') {this.error =  "Please provide your name"; return}
      if (this.email === '') {this.error =  "Please provide your email address"; return}
      if (!this.message) {this.error =  "Please provide your message"; return}
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {this.error =  "Please provide a valid email address"; return} // Regex test for a valid email address
      this.showSpinner = true
      const response = await axios.post(`${config.apiUrl}/api/contact`, {name: this.name, email: this.email, message: this.message})
      if (response.data.error) {this.error = response.data.error; return}
      this.showSuccess = true
      this.showSpinner = false
      event.stopPropagation()
    },
    isAuthenticated() {return localStorage.getItem('_u') !== null},
    isSubscribed() {return this.subscription},
    handleCloseSuccess() {this.showSuccess = false, this.$router.push('/faq')},
  }
}
</script>