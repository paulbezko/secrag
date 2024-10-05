<template>
  <div>
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div  v-if="showComponent">
      <div v-if="showConfirm"><ConfirmComp :action="action" :oneStepDelete="limitSettings" @close="handleCloseConfirm" @success="handleSuccess" /></div>
      <div v-if="showSuccess"><SuccessComp :action="action" @close="handleCloseSuccess" /></div>
      <div v-if="showConfirm || showSuccess" class="backdrop z-30" @click="handleCloseConfirm"></div>
      <div class="card z-20 position-fixed card-profile">
        <div style="padding-bottom: 2rem;" class="display-flex-column gap-1">
          <div class="text-3 bold text-color-semilight">Profile</div>
          <div class="display-flex-column gap-1">
            <div class="text-3 bold text-color-semilight">Preferred Name</div>
            <div class="display-flex-row gap-1" style="position: relative">
              <input class="input flex-1" type="text" placeholder="Name" v-model="name">
              <button class="fa-solid fa-arrow-right text-2 button-icon text-color-semilight" @click="changeName" style="position: absolute; right: 0; top: 50%; transform: translateY(-50%); border: 0; background-color: transparent;"></button>
            </div>
          </div>
        </div>
        <div style="padding-bottom: 2rem;" class="display-flex-column gap-1">
          <div class="text-3 bold text-color-semilight">Security</div>
          <div v-if="limitSettings" class="display-flex-row center gap-1" style="height: 3rem;">
            <div class="fa-solid fa-envelope text-1"></div>
            <div style="flex: 1">
              <div class="text-3 light">Email</div>
              <div class="text-2 light">{{ email }}</div>
            </div>
          </div>
          <div v-if="!limitSettings" class="display-flex-row center gap-1 text-link" style="height: 3rem;" @click="changeEmail">
            <div class="fa-solid fa-envelope text-1"></div>
            <div style="flex: 1">
              <div class="text-3 light">Email</div>
              <div class="text-2 light">{{ email }}</div>
            </div>
          </div>
          <div v-if="!limitSettings" class="display-flex-row center gap-1 text-link" style="height: 3rem;" @click="changePassword">
            <div class="fa-solid fa-key text-1"></div>
            <div class="text-3 bold text-color-semilight" style="flex: 1">Password</div>
          </div>
          <div class="display-flex-row center gap-1 text-link-discouraged" style="height: 3rem;" @click="signOut">
            <div class="fa-solid fa-arrow-right-from-bracket text-1"></div>
            <div class="text-3 light" style="flex: 1">Sign Out</div>
          </div>
        </div>
        <div v-if="subscribed" class="display-flex-column gap-1" style="padding-bottom: 2rem;">
          <div class="text-3 bold">Subscription</div>
          <div class="display-flex-row center gap-1 text-link" @click="manageSubscription">
            <div class="fa-solid fa-money-check-dollar text-1"></div>   
            <div style="flex: 1">
              <div class="text-3 bold">Manage subscription</div>
              <div class="text-2">{{ subscription }}</div>
            </div>
          </div>
        </div>
        <div class="text-3 bold text-color-semilight">Danger Zone</div>
        <div class="display-flex-row center gap-1 text-link-discouraged" @click="deleteAccount">
          <div class="fa-solid fa-triangle-exclamation text-1"></div>
          <div class="text-3 light" style="flex: 1">Delete Account</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ConfirmComp from './ConfirmComp.vue';
import SuccessComp from './SuccessComp.vue';
import SpinnerComp from './SpinnerComp.vue';
import { config } from '@/config';

export default {
  name: 'ProfileComp',
  components: {
    ConfirmComp,
    SuccessComp,
    SpinnerComp
  },
  data() {
    return {
      showComponent: false,
      showSpinner: false,
      name: '',
      email: '',
      showConfirm: false,
      showSuccess: false,
      action: '',
      subscription: '',
      subscribed: false,
      limitSettings: false,
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
    async changeName(event) {
      this.showSpinner = true
      let response = await axios.post(`${config.apiUrl}/api/edit-user`, {action: 'changeName', token: localStorage.getItem('_u'), name: this.name});
      if (response.data.error) {alert(response.data.error); return}
      localStorage.setItem('_u', response.data.token);
      this.action = 'changeName';
      this.showSpinner = false
      this.showSuccess = true;
      event.stopPropagation();
    },
    changeEmail(event) {this.action = 'changeEmail'; this.showConfirm = true; event.stopPropagation()},
    changePassword(event) {this.action = 'changePassword'; this.showConfirm = true; event.stopPropagation()},
    signOut(event) {this.action = 'signOut'; this.showConfirm = true; event.stopPropagation()},
    deleteAccount(event) {this.action = 'deleteAccount'; this.showConfirm = true; event.stopPropagation()},
    handleCloseConfirm() {this.showConfirm = false},
    handleCloseSuccess() {this.showSuccess = false; if (this.action === 'deleteAccount') {this.$router.push('/')}},
    handleSuccess() {
      if (this.action === 'changeEmail' || this.action === 'changePassword' || this.action === 'deleteAccount') {this.showConfirm = false; this.showSuccess = true;}
      else if (this.action === 'signOut') {localStorage.removeItem('_u'); if (this.$route.path === '/') {window.location.reload()} else {this.$router.push('/')}}
    }
  }
}
function toTitleCase(str) {return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()}
</script>
