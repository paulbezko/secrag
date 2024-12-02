<template>
  <div class="navbar flex-row width-100 center">
    <div class="flex-row width-100" style="padding-block: 2rem; max-width: 116rem; padding-inline: 2rem;">
      <div class="flex-row width-100" style="justify-content: space-between;">
        <div class="flex-row center gap-2">
          <router-link class="text-3 text-bold text-link" to="/">{{projectName}}</router-link>
          <router-link class="text-3 show-on-large text-link text-bold text-link-accent" v-if="!authenticated" to="/preview">Try for Free</router-link>
        </div>
        <div class="flex-row center gap-2 show-on-large">
          <router-link class="text-3 text-link" to="/#about">About</router-link>
          <router-link class="text-3 text-link" to="/#faq">FAQ</router-link>
          <router-link class="text-3 text-link" to="/#contact">Contact</router-link>
          <a class="text-3 text-link" href="https://open.spotify.com/show/69BXlAfewT4Pdeja7YDYdz">Podcast</a>
        </div>
        <div class="flex-row gap-2 show-on-large">
          <router-link class="button button-navbar button-secondary" v-if="!authenticated" to="/signup">Sign Up</router-link>
          <router-link class="text-3 text-link text-link-accent" v-if="authenticated && !subscribed" to="/subscribe">Subscribe</router-link>
          <router-link class="text-3 show-on-large text-link text-link-accent" v-if="authenticated && subscribed" to="/dashboard">Dashboard</router-link>
          <div class="text-3 text-link" v-if="authenticated" @click="toggleProfile">Profile</div>
        </div>
        <div class="flex-row gap-2 show-on-small">
          <div class="fa-solid fa-ellipsis-vertical text-1 text-link" @click="toggleDropdown()"></div>
        </div>
      </div>
      
    <component :is="profileComp"></component>

    <transition>
      <div v-if="showDropdown" class="card-component card-component-navbar flex-column gap-1 show-on-small z-30 width-100" style="max-width: 16rem; top:1rem; right:1rem;">
        <router-link class="text-2" v-if="authenticated && subscribed"  to="/dashboard">Dashboard</router-link>
        <hr class="width-100" v-if="authenticated && subscribed" style="border-top: 1px solid var(--color-grey)">
        <router-link class="text-2" @click="toggleDropdown()" to="/#about">About</router-link>
        <router-link class="text-2" @click="toggleDropdown()" to="/#faq">FAQ</router-link>
        <router-link class="text-2" @click="toggleDropdown()" to="/#contact">Contact</router-link>
        <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
        <router-link class="text-2" v-if="!authenticated" to="/signup">Sign Up</router-link>
        <router-link class="text-2" v-if="!authenticated" to="/login">Login</router-link>
        <router-link class="text-2" v-if="authenticated && !subscribed" to="/subscribe">Subscribe</router-link>
        <div class="text-2 text-link" v-if="authenticated" @click="toggleProfile">Profile</div>
      </div>
    </transition>

      <!-- Modal Backdrop -->
      <div v-if="showProfile" class="backdrop z-10" @click="toggleProfile"></div>
      <div v-if="showDropdown" class="backdrop z-10" @click="toggleDropdown"></div>
    </div>
  </div>
</template>

<script>
import ProfileComp from './ProfileComp.vue';
import webdata from '../webdata.json'

export default {
  components: {
    ProfileComp
  },
  props: {
    authenticated: Boolean, 
    subscribed: Boolean
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll);
  },
  unmounted() {
    window.removeEventListener('scroll', this.handleScroll);
  },
  data() {return {
    showProfile: false,
    showDropdown: false,
    projectName: webdata.projectName,
  }},
  computed: {
    profileComp() {return this.showProfile ? 'ProfileComp' : null},
    dropdownComp() {return this.showDropdown ? 'DropdownComp' : null}
  },
  methods: {
    toggleProfile() {this.showProfile = !this.showProfile; this.showDropdown = false},
    toggleDropdown() {this.showDropdown = !this.showDropdown},
    handleScroll() {
      const navbar = document.querySelector('.navbar');
      const container = this.$refs.container;
      if (container) {
        if (container.scrollY > 0) {navbar.classList.add('shadow');}
        else {navbar.classList.remove('shadow');}
      }
      else {
        if (window.scrollY > 0) {navbar.classList.add('shadow');} 
        else {navbar.classList.remove('shadow');}
      }
    },
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