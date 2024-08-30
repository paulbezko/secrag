<template>
  <div class="display-flex-row width-100" style="padding-block: 2rem;">
    <div class="display-flex-row width-100" style="justify-content: space-between;">
      <div class="display-flex-row gap-2">
        <router-link class="text text-2 text-link medium" to="/">SecRag</router-link>
        <div class="text text-2 text-link medium" style="color: transparent" v-if="authenticated && !subscribed">Dashboard</div>
        <router-link class="text text-2 text-link medium show-on-large" v-if="authenticated && subscribed" to="/dashboard">Dashboard</router-link>
      </div>
      <div class="display-flex-row gap-2 show-on-large">
        <router-link class="text text-2 text-link medium" to="/pricing">Pricing</router-link>
        <router-link class="text text-2 text-link medium" to="/about-us">About Us</router-link>
        <router-link class="text text-2 text-link medium" to="/faq">FAQ</router-link>
      </div>
      <div class="display-flex-row gap-2 show-on-large">
        <router-link class="text text-2 text-link medium" v-if="!authenticated" to="/login">Login</router-link>
        <router-link class="text text-2 text-link medium" v-if="authenticated && !subscribed" to="/subscribe">Subscribe</router-link>
        <div class="text text-2 text-link medium" style="color: transparent" v-if="authenticated && subscribed">Subscribe</div>
        <div class="text text-2 text-link medium" v-if="authenticated" @click="toggleProfile">Profile</div>
      </div>
      <div class="display-flex-row gap-2 show-on-small">
        <div class="fa-solid fa-bars text-1 text-link" @click="toggleDropdown()"></div>
      </div>
    </div>

    <component :is="profileComp"></component>

    <transition>
      <div v-if="showDropdown" class="card show-on-small z-30" style="position:absolute; top:1rem; right:1rem;">
        <router-link class="text text-2 text-link medium" v-if="authenticated && subscribed"  to="/dashboard">Dashboard</router-link>
        <div v-if="authenticated && subscribed" ></div>
        <router-link class="text text-2 text-link medium" to="/pricing">Pricing</router-link>
        <router-link class="text text-2 text-link medium" to="/about-us">About Us</router-link>
        <router-link class="text text-2 text-link medium" to="/faq">FAQ</router-link>
        <div></div>
        <router-link class="text text-2 text-link medium" v-if="!authenticated" to="/login">Login</router-link>
        <router-link class="text text-2 text-link medium" v-if="authenticated && !subscribed" to="/subscribe">Subscribe</router-link>
        <div class="text text-2 text-link medium" v-if="authenticated" @click="toggleProfile">Profile</div>
      </div>
    </transition>

      <!-- Modal Backdrop -->
      <div v-if="showProfile" class="backdrop z-10" @click="toggleProfile"></div>
      <div v-if="showDropdown" class="backdrop z-10" @click="toggleDropdown"></div>

  </div>
</template>

<script>
import ProfileComp from './ProfileComp.vue';

export default {
  components: {
    ProfileComp
  },
  props: {
    authenticated: Boolean, 
    subscribed: Boolean
  },
  data() {return {
    showProfile: false,
    showDropdown: false
  }},
  computed: {
    profileComp() {return this.showProfile ? 'ProfileComp' : null},
    dropdownComp() {return this.showDropdown ? 'DropdownComp' : null}
  },
  methods: {
    toggleProfile() {this.showProfile = !this.showProfile; this.showDropdown = false},
    toggleDropdown() {this.showDropdown = !this.showDropdown}
  }
}
</script>
<style scoped>
.v-enter-active,
.v-leave-active {
  transition: all .3s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}
</style>