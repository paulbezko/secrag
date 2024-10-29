<template>
  <div>
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div v-if="showComponent">
      <div v-if="showConfirm"><ConfirmComp :action="action" :oneStepDelete="limitSettings" @close="handleCloseConfirm" @success="handleSuccess" /></div>
      <div v-if="showSuccess"><SuccessComp :action="action" @close="handleCloseSuccess" /></div>
      <div v-if="showConfirm || showSuccess" class="backdrop z-30" @click="handleCloseConfirm"></div>
      <div class="card-component card-component-center z-20 absolute gap-1 flex-column width-100 card-size-profile text-inter">
        <div class="flex-column gap-1">
          <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold">Preferred Name</div>
          <div class="flex-row gap-1 width-100">
            <input class="input" type="text" placeholder="Name" v-model="name"/>
            <div @click="changeName" class="button-icon"><SpinnerCompButton v-if="showSpinnerButton"></SpinnerCompButton><div v-if="!showSpinnerButton" class="fa-solid fa-arrow-right" style="color: var(--color-grey-black)"></div></div>
          </div>
        </div>
        <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
        <div class="flex-column gap-1">
          <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold">Security</div>
          <div v-if="limitSettings" class="flex-row center gap-1 text-link encouraged" :style="isSmallScreen ? 'height: 3.0rem;' : 'height: 3.6rem;'">
            <div class="fa-solid fa-envelope text-1 text-center" style="min-width: 3rem;"></div>
            <div class="flex-column width-100">
              <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold">Email</div>
              <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-overflow" style="max-width: 19rem;">{{ email }}</div>
            </div>
          </div>
          <div v-if="!limitSettings" class="flex-row center gap-1 text-link encouraged" :style="isSmallScreen ? 'height: 3.0rem;' : 'height: 3.6rem;'" @click="changeEmail">
            <div class="fa-solid fa-envelope text-1 text-center" style="min-width: 3rem;"></div>
            <div class="flex-column width-100">
              <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold">Email</div>
              <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-overflow" style="max-width: 19rem; line-height: 1.5rem">{{ email }}</div>
            </div>
          </div>
          <div v-if="!limitSettings" class="flex-row center gap-1 text-link encouraged" :style="isSmallScreen ? 'height: 3.0rem;' : 'height: 3.6rem;'" @click="changePassword">
            <div class="fa-solid fa-key text-1 text-center" style="min-width: 3rem;"></div>
            <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold" style="flex: 1">Password</div>
          </div>
          <div class="flex-row center gap-1 text-link discouraged" :style="isSmallScreen ? 'height: 3.0rem;' : 'height: 3.6rem;'" @click="signOut">
            <div class="fa-solid fa-arrow-right-from-bracket text-1 text-center" style="min-width: 3rem;"></div>
            <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold text-link encouraged" style="flex: 1">Sign Out</div>
          </div>
        </div>
        <hr v-if="subscribed" class="width-100" style="border-top: 1px solid var(--color-grey)">
        <div v-if="subscribed" class="flex-column gap-2">
          <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold">Subscription</div>
          <div class="flex-row center gap-1 text-link encouraged" @click="manageSubscription" :style="isSmallScreen ? 'height: 3.0rem;' : 'height: 3.6rem;'">
            <div class="fa-solid fa-money-check-dollar text-1 text-center" style="min-width: 3rem;"></div>   
            <div style="flex: 1">
              <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold">Manage Subscription</div>
              <div :class="isSmallScreen ? 'text-3' : 'text-4'" :style="isSmallScreen ? 'line-height: 1.5rem' : ''">{{ subscription }}</div>
            </div>
          </div>
          <!-- tokensLeft -->
          <div class="flex-row center gap-1 text-link encouraged"  @click="replenishTokens" :style="isSmallScreen ? 'height: 3.0rem;' : 'height: 3.6rem;'">
            <div class="fa-solid fa-chart-simple text-1 text-center" style="min-width: 3rem;"></div>   
            <div style="flex: 1">
              <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold">Replenish Tokens</div>
              <div :class="isSmallScreen ? 'text-3' : 'text-4'" :style="isSmallScreen ? 'line-height: 1.5rem' : ''">{{ tokensLeft }} tokens left</div>
            </div>
          </div>
        </div>
        <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
        <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold">Danger Zone</div>
        <div class="flex-row center gap-1 text-link discouraged" @click="deleteAccount" :style="isSmallScreen ? 'height: 3.0rem;' : 'height: 3.6rem;'">
          <div class="fa-solid fa-triangle-exclamation text-1 text-center" style="min-width: 3rem;"></div>
          <div :class="isSmallScreen ? 'text-3' : 'text-4'" class="text-bold" style="flex: 1">Delete Account</div>
        </div>
        <hr v-if="error" class="width-100" style="border-top: 1px solid var(--color-grey)">
        <div v-if="error" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ConfirmComp from './ConfirmComp.vue';
import SuccessComp from './SuccessComp.vue';
import SpinnerCompButton from './SpinnerCompButton.vue';
import SpinnerComp from './SpinnerComp.vue';
import { config } from '@/config';

export default {
  name: 'ProfileComp',
  components: {
    ConfirmComp,
    SuccessComp,
    SpinnerComp,
    SpinnerCompButton
  },
  data() {
    return {
      isSmallScreen: window.innerWidth <= 800, // Initial check for screen size
      showComponent: false,
      showSpinnerButton: false,
      showSpinner: false,
      name: '',
      email: '',
      showConfirm: false,
      showSuccess: false,
      action: '',
      subscription: '',
      tokensLeft: 0,
      subscribed: false,
      limitSettings: false,
      error: ''
    }
  },
  mounted() {
    this.showSpinner = true
    axios.get(`${config.apiUrl}/api/get-user-data`, {params: {token: localStorage.getItem('_u')}})
      .then(response => {
        if (response.data.auth_type !== 'password') {this.limitSettings = true}
        if (response.data.critical) {localStorage.removeItem('_u'); this.$router.push('/')}
        localStorage.setItem('_u', response.data.token)
        if (response.data.avatarUrl) {this.avatarUrl = response.data.avatarUrl}
        this.email = response.data.email;
        this.name = response.data.name;
        this.subscription = response.data.subscription;
        this.tokensLeft = response.data.subscription_tokens_left;
        if (this.subscription) {this.subscription = toTitleCase(response.data.subscription);}
        if (response.data.subscription !== 'none') {this.subscribed = true}
        this.showSpinner = false
        this.showComponent = true
      })
      .catch(error => {
        console.error('Error getting user data:', error);
      });
  },
  methods: {
    async manageSubscription() {
      this.showSpinner = true
      const response = await axios.post(`${config.apiUrl}/api/subscribe`, {
        token: localStorage.getItem('_u'),
        operation: 'manageSubscription',
      });
      window.location.href = response.data.sessionUrl;
    },
    async replenishTokens() {
      this.showSpinner = true
      const response = await axios.post(`${config.apiUrl}/api/subscribe`, {
        token: localStorage.getItem('_u'),
        operation: 'replenishTokens',
      });
      window.location.href = response.data.sessionUrl;
    },
    async changeName(event) {
      if (this.name === '') {this.error = "Please provide a name"; return}
      this.showSpinnerButton = true
      let response = await axios.post(`${config.apiUrl}/api/edit-user`, {action: 'changeName', token: localStorage.getItem('_u'), name: this.name});
      if (response.data.error) {this.error = response.data.error; return}
      localStorage.setItem('_u', response.data.token);
      this.action = 'changeName';
      this.showSpinnerButton = false
      this.showSuccess = true;
      event.stopPropagation();
    },
    changeEmail(event) {this.action = 'changeEmail'; this.showConfirm = true; event.stopPropagation()},
    changePassword(event) {this.action = 'changePassword'; this.showConfirm = true; event.stopPropagation()},
    signOut(event) {this.action = 'signOut'; this.showConfirm = true; event.stopPropagation()},
    deleteAccount(event) {this.action = 'deleteAccount'; this.showConfirm = true; event.stopPropagation()},
    handleCloseConfirm() {this.showConfirm = false;},
    handleCloseSuccess() {this.showSuccess = false; if (this.action === 'deleteAccount') {this.$router.push('/')}},
    handleSuccess() {
      if (this.action === 'changeEmail' || this.action === 'changePassword' || this.action === 'deleteAccount') {this.showConfirm = false; this.showSuccess = true;}
      else if (this.action === 'signOut') {localStorage.removeItem('_u'); this.$store.commit('resetUserState'); window.location.replace('/')}
    }
  }
}
function toTitleCase(str) {return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()}
</script>
<style scoped>
/* we will explain what these classes do next! */
.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>