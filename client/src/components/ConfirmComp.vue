<template>
  <div>
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div v-if="showComponent">
      <div v-if="action === 'resetPasswordBefore'" style="position: absolute" class="z-40">
        <div class="card card-helper position-fixed" ref="ConfirmCard">
          <div class="heading-3">Reset Password</div>
          <input class="input" placeholder="Email" v-model="email"/>
          <div v-if="error" class="text-3 text-error bold"> {{ error }}</div>
          <div class="button button-secondary" @click="submit($event)">Submit</div>
        </div>
      </div>
      <div v-if="action === 'changeEmail'" style="position: absolute" class="z-40">
        <div class="card card-helper position-fixed" ref="ConfirmCard">
          <div class="heading-3">Change Email</div>
          <input class="input" v-model="emailNew" type="text" placeholder="New Email">
          <div class="display-flex-row gap-1 width-100">
            <input class="input flex-1" type="password" placeholder="Current Password" v-model="password"/>
            <button @click="submit($event)" class="fa-solid fa-arrow-right text-2 button-icon"></button>
          </div>
          <div v-if="error" class="text-3 text-error bold"> {{ error }}</div>
        </div>
      </div>
      <div v-if="action === 'changePassword'" style="position: absolute" class="z-40">
        <div class="card card-helper position-fixed" ref="ConfirmCard">
          <div class="heading-3">Change Password</div>
          <input class="input" type="password" placeholder="Current Password" v-model="password"/>
          <input class="input" type="password" placeholder="New Password" v-model="passwordNew"/>
          <div class="display-flex-row gap-1 width-100">
            <input class="input flex-1" type="password" placeholder="Confirm New Password" v-model="passwordNewConfirm"/>
            <button @click="submit($event)" class="fa-solid fa-arrow-right text-2 button-icon"></button>
          </div>
          <div v-if="error" class="text-3 text-error bold"> {{ error }}</div>
        </div>
      </div>
      <div v-if="action === 'signOut'" style="position: absolute" class="z-40">
        <div class="card card-helper position-fixed" ref="ConfirmCard">
          <div class="heading-3">Sign Out?</div>
          <div class="button button-discouraged" @click="submit($event)">Confirm</div>
        </div>
      </div>
      <div v-if="action === 'deleteAccount'" style="position: absolute" class="z-40">
        <div class="card card-helper position-fixed" ref="ConfirmCard">
          <div class="heading-3">Delete Account?</div>
          <div class="text-3">This action is final and cannot be undone. Current subscription will be cancelled.</div>
          <input v-if="!oneStepDelete" v-model="password" class="input" type="password" placeholder="Current Password"/>
          <img v-if="oneStepDelete" :src="captchaImage" alt="CAPTCHA Image" style="object-fit: cover; width: 100%; border-radius: 1rem; border: solid 2px black; box-sizing: border-box;">
          <input v-if="oneStepDelete" class="input" placeholder="Captcha answer" v-model="captcha"/>
          <div v-if="error" class="text-3 text-error bold"> {{ error }}</div>
          <div class="display-flex-row gap-1 width-100">
            <div class="button button-cta flex-1" @click="closeCard()">Go Back</div>
            <div class="button button-discouraged flex-1" @click="submit($event)">Confirm</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { passwordStrength } from 'check-password-strength'
import SpinnerComp from './SpinnerComp.vue';
import { config } from '@/config';
import axios from 'axios';

export default {
  name: 'ConfirmComp',
  components: {SpinnerComp},
  props: {
    oneStepDelete: {type: Boolean, required: true},
    action: {type: String, required: true}
  },
  data() {return {
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
      finally {this.showSpinner = false}
      event.stopPropagation();
    }
  },

  beforeUnmount() {window.removeEventListener('click', this.handleClickOutside)}
}
</script>

