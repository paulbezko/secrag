<template>
  <div>
    <div v-if="showComponent">
      <div class="z-40 width-100 flex-row center fixed card-component-center" style="padding-inline: 4rem;">
        <div class="card-component flex-column center gap-2 card-size-confirm" ref="ConfirmCard">
          <div class="text-1 text-bold text-center">{{ actions[action].heading }}</div>
          <div class="text-3 text-center">{{ actions[action].text }}</div>
          <div v-if="action === 'resetPasswordBefore'" class="flex-column gap-1 width-100">
            <div class="flex-row gap-1 width-100">
              <input class="input" placeholder="Email" v-model="email"/>
              <div @click.stop="submit($event)" class="button-icon"><SpinnerCompButton v-if="showSpinner"></SpinnerCompButton><div v-if="!showSpinner" class="fa-solid fa-arrow-right" style="color: var(--color-grey-black)"></div></div>
            </div>
            <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
          </div>
          <div v-if="action === 'changeEmail' || action === 'changePassword' || action === 'deleteAccount'" class="flex-column gap-1 center width-100">
            <input v-if="action === 'changeEmail' || action === 'changePassword' || action === 'deleteAccount'" class="input" type="password" placeholder="Current Password" v-model="password"/>
            <input v-if="action === 'changePassword'" class="input" type="password" placeholder="New Password" v-model="passwordNew"/>
            <div v-if="action === 'changePassword'" class="flex-column gap-1 width-100">
              <div class="flex-row gap-1 width-100">
                <input class="input" type="password" placeholder="Confirm New Password" v-model="passwordNewConfirm"/>
                <div @click.stop="submit($event)" class="button-icon"><SpinnerCompButton v-if="showSpinner"></SpinnerCompButton><div v-if="!showSpinner" class="fa-solid fa-arrow-right" style="color: var(--color-grey-black)"></div></div>
              </div>
              <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
            </div>
            <div v-if="action === 'changeEmail'" class="flex-column gap-1 width-100">
              <div class="flex-row gap-1 width-100">
                <input class="input" type="text" placeholder="New Email" v-model="emailNew"/>
                <div @click.stop="submit($event)" class="button-icon"><SpinnerCompButton v-if="showSpinner"></SpinnerCompButton><div v-if="!showSpinner" class="fa-solid fa-arrow-right" style="color: var(--color-grey-black)"></div></div>
              </div>
              <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
            </div>
          </div>
          <div v-if="action === 'signOut' || action === 'deleteAccount'" class="button button-secondary" @click="submit($event)">Confirm</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { passwordStrength } from 'check-password-strength'
import SpinnerCompButton from './SpinnerCompButton.vue';
import { config } from '@/config';
import axios from 'axios';

export default {
  name: 'ConfirmComp',
  components: {SpinnerCompButton},
  props: {
    oneStepDelete: {type: Boolean, required: true},
    action: {type: String, required: true}
  },
  data() {return {
    actions: {
      'resetPasswordBefore': {
        'heading': 'Reset Password',
        'text': 'We will send you an email with a link to reset your password.'
      },
      'changeEmail': {
        'heading': 'Change Email',
        'text': 'We will send you an email with a link to confirm your new email address.'
      },
      'changePassword': {
        'heading': 'Change Password',
        'text': 'Please enter your current password and a new password.'
      },
      'signOut': {
        'heading': 'Sign Out',
        'text': 'Are you sure you want to sign out?'
      },
      'deleteAccount': {
        'heading': 'Delete Account',
        'text': 'This action is final and cannot be undone. Current subscription will be cancelled.'
      },
    },
    showComponent: false,
    showSpinner: false,
    email: '', 
    password: '',
    captcha: '',
    emailNew: '', 
    passwordNew: '', 
    passwordNewConfirm: '', 
    error: '',
    captchaImage: null,
  }},
  mounted() {
    this.showSpinner = true; // Show spinner while loading CAPTCHA
    window.addEventListener('click', this.handleClickOutside);
    window.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        this.submit(event);
      }
    });
    if (this.oneStepDelete && this.action === 'deleteAccount') {
      axios.get(`${config.apiUrl}/api/get-captcha`, {params: {token: localStorage.getItem('_u')}})
        .then(response => {
          this.captchaImage = response.data.captcha_image;
          localStorage.setItem('_u', response.data.token);
          this.showSpinner = false; // Hide spinner after CAPTCHA is loaded
          this.showComponent = true; // Show component after CAPTCHA is loaded
        })
        .catch(error => {
          console.error('Error getting captcha:', error);
          this.showSpinner = false; // Hide spinner if there's an error
          this.showComponent = false; // Optionally hide component or show an error message
        });
    } else {
      this.showSpinner = false; // Hide spinner if no CAPTCHA is needed
      this.showComponent = true; // Show component if no CAPTCHA is needed
    }
  },
  methods: {
    closeCard() {this.$emit('close')},
    handleClickOutside(event) {if (!this.$refs.ConfirmCard.contains(event.target)) {this.closeCard()}
    },
    async submit(event) {
      this.error = false
      this.showSpinner = true
      try {
        if (this.action === 'resetPasswordBefore') {
          if (this.email === '') {this.error = "Please provide your email address"; return}
          if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {this.error = "Please provide a valid email address"; return} // Regex test for a valid email address

          const response = await axios.post(`${config.apiUrl}/api/reset-password`, {action: 'resetPasswordBefore', email: this.email})
          if (response.data.error) {this.error = response.data.error; return}
          this.$emit('success');
        }
        else if (this.action === 'changeEmail') {
          if (this.password === '') {this.error = "Please provide your current password"; return}
          if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.emailNew)) {this.error = "Please provide a valid email address"; return} // Regex test for a valid email address

          const response = await axios.post(`${config.apiUrl}/api/edit-user`, {action: 'changeEmail', token: localStorage.getItem('_u'), password: this.password, emailNew: this.emailNew})
          if (response.data.error) {this.error = response.data.error; return}
          this.$emit('success');
        }
        else if (this.action === 'changePassword') {
          if (this.password === '') {this.error = "Please provide your current password"; return}
          if (this.passwordNew != this.passwordNewConfirm) {this.error = "Passwords do not match"; return}
          if (passwordStrength(this.passwordNew).id < 2) {this.error = "Password too weak"; return}

          const response = await axios.post(`${config.apiUrl}/api/edit-user`, {action: 'changePassword', token: localStorage.getItem('_u'), password: this.password, passwordNew: this.passwordNew})
          if (response.data.error) {this.error = response.data.error; return}
          this.$emit('success');
          
        }
        else if (this.action === 'signOut') {
          this.$emit('success');
        }
        else if (this.action === 'deleteAccount') {

          if (!this.oneStepDelete) {if (this.password === '') {this.error = "Please provide your current password"; return}}
          if (this.oneStepDelete) {if (this.captcha === '') {this.error = "Please provide the captcha answer"; return}}
          
          const response = await axios.post(`${config.apiUrl}/api/edit-user`, {action: 'deleteAccount', password: this.password, captcha: this.captcha, token: localStorage.getItem('_u')})
          if (response.data.error) {this.error = response.data.error; 
            
            if (this.oneStepDelete && this.action === 'deleteAccount') {
              axios.get(`${config.apiUrl}/api/get-captcha`, {params: {token: localStorage.getItem('_u')}})
                .then(response => {
                  this.captchaImage = response.data.captcha_image;
                  localStorage.setItem('_u', response.data.token);
                  this.captcha = ''
                  this.showSpinner = false; // Hide spinner after CAPTCHA is loaded
                  this.showComponent = true; // Show component after CAPTCHA is loaded
                })
                .catch(error => {
                  console.error('Error getting captcha:', error);
                  this.showSpinner = false; // Hide spinner if there's an error
                  this.showComponent = false; // Optionally hide component or show an error message
                });
            } else {
              this.showSpinner = false; // Hide spinner if no CAPTCHA is needed
              this.showComponent = true; // Show component if no CAPTCHA is needed
            }
            
            return}
          
          localStorage.removeItem('_u')
          this.$emit('success');
          event.stopPropagation();
        }
      }
      catch (error) {console.log(error)}
      finally {this.showSpinner = false; event.stopPropagation()}
    }
  },

  beforeUnmount() {window.removeEventListener('click', this.handleClickOutside)}
}
</script>

