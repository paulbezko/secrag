import { createApp } from 'vue';
import { createStore } from 'vuex';
import { createRouter, createWebHistory } from 'vue-router';
import { config } from '@/config';
import axios from 'axios';
import App from './App.vue';

// Define Vuex store
const store = createStore({
  state: {
    _u: null,
    isAuthenticated: false,
    isSubscribed: false,
    subscription: null,
    subscriptionTokensLeft: null
  },
  mutations: {
    setAuthentication(state, status) {
      state.isAuthenticated = status;
    },
    setIsSubscribed(state, status) {
      state.isSubscribed = status;
    },
    setSubscription(state, subscription) {
      state.subscription = subscription;
    },
    setSubscriptionTokensLeft(state, subscriptionTokensLeft) {
      state.subscriptionTokensLeft = subscriptionTokensLeft;
    }
  },
});

// Route declarations
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./views/HomeView.vue') },
    { path: '/terms-and-conditions', component: () => import('./views/TermsAndConditionsView.vue') },
    { path: '/login', component: () => import('./views/LoginView.vue') },
    { path: '/signup', component: () => import('./views/SignupView.vue') },
    { path: '/handle-supabase', component: () => import('./views/HandleSupabaseView.vue') },
    { path: '/reset-password', component: () => import('./views/ResetPasswordView.vue') },
    { path: '/subscribe', component: () => import('./views/SubscribeView.vue'), meta: { requiresAuthentication: true } },
    { path: '/dashboard', component: () => import('./views/DashboardView.vue'), meta: { requiresAuthentication: true, requiresSubscription: true } },
    { path: '/change-email', component: () => import('./views/ChangeEmailView.vue'), meta: { requiresAuthentication: true } },
    { path: '/:pathMatch(.*)', component: () => import('./views/404View.vue') },
  ],
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' };
    }
    return { left: 0, top: 0 };
  },
});

// The routing masterpiece
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('_u'); // Get the saved token before each request

  if (token) {
    let response;
    response = await axios.get(`${config.apiUrl}/api/router?token=` + token); // Verify if the token is legit

    if (response.data.critical) {
      localStorage.removeItem('_u');
      store.commit('setAuthentication', false)
      return next('/'); // Redirect to home if token is critical
    }

    if (response.data.authenticated) {
      store.commit('setAuthentication', true); // Update Vuex state

      // Get user subscription info
      const navbarInfo = await getNavbarInfo();
      store.commit('setIsSubscribed', navbarInfo.isSubscribed);
      if (navbarInfo.subscription) {
        store.commit('setSubscription', navbarInfo.subscription);
        store.commit('setSubscriptionTokensLeft', navbarInfo.subscriptionTokensLeft);
      }

      // Redirect to onboarding if necessary
      if (response.data.onboarding) {
        if (to.path !== '/signup') {
          return next('/signup');
        }
      } else {
        if (to.path === '/signup' || to.path === '/login') {
          return next('/dashboard');
        }
      }

      // Check if user is trying to access the dashboard
      if (to.path === '/dashboard') {
        if (navbarInfo.isSubscribed === false) {
          return next('/subscribe'); // Redirect to subscribe if not subscribed
        }
      }

      // Check for other routes requiring authentication or subscription
      if (to.meta.requiresSubscription && navbarInfo.isSubscribed === false) {
        return next('/subscribe'); // Redirect if subscription is required
      }

      return next(); // Allow access if everything checks out
    }

    if (to.meta.requiresAuthentication) {
      return next('/login'); // Redirect to login if authentication is required
    }
    
    return next(); // Proceed for non-protected routes
  }

  if (to.meta.requiresAuthentication) {
    return next('/login'); // Redirect to login if user is unauthenticated
  }
  
  next(); // Proceed to next middleware or route
});

function getNavbarInfo() {
  return new Promise((resolve, reject) => {
    const token = localStorage.getItem('_u');
    if (token) {
      axios.get(`${config.apiUrl}/api/get-user-data`, { params: { token: token } })
        .then(response => {
          const isSubscribed = response.data.subscription !== 'none';
          const subscription = response.data.subscription ? response.data.subscription : null;
          const subscriptionTokensLeft = response.data.subscription_tokens_left ? response.data.subscription_tokens_left : null;
          resolve({ isSubscribed, subscription, subscriptionTokensLeft });
        })
        .catch(error => {
          alert('Error retrieving user data:', error);
          reject(error);
        });
    } else {
      resolve({ isSubscribed: false, subscription: null }); // If no token exists, user is not subscribed
    }
  });
}

const app = createApp(App);
app.use(store);
app.use(router);
app.mount('#app');