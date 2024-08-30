import { createApp } from 'vue'
import { createStore } from 'vuex';
import { createRouter, createWebHistory } from 'vue-router'
import { config } from '@/config';
import axios from 'axios';
import App from './App.vue'

// This works, everything in here is needed
const store = createStore({state: {_u: null}});

// Route declarations
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {path: '/',                 component: () => import('./views/HomeView.vue')},
    {path: '/login',            component: () => import('./views/LoginView.vue')},
    {path: '/signup',           component: () => import('./views/SignupView.vue')},
    {path: '/handle-supabase',  component: () => import('./views/HandleSupabaseView.vue')},
    {path: '/reset-password',   component: () => import('./views/ResetPasswordView.vue')},
    {path: '/pricing',          component: () => import('./views/PricingView.vue')},
    {path: '/about-us',         component: () => import('./views/AboutUsView.vue')},
    {path: '/faq',              component: () => import('./views/FAQView.vue')},
    {path: '/contact',          component: () => import('./views/ContactView.vue')},
    {path: '/subscribe',        component: () => import('./views/SubscribeView.vue'), meta: { requiresAuthentication: true }}, // protected
    {path: '/dashboard',        component: () => import('./views/DashboardView.vue'), meta: { requiresAuthentication: true, requiresSubscription: true }}, // protected
    {path: '/change-email',     component: () => import('./views/ChangeEmailView.vue'), meta: { requiresAuthentication: true }}, // protected,
    {path: '/:pathMatch(.*)',   component: () => import('./views/404View.vue')}
  ]
})

// The routing masterpiece
router.beforeEach(async (to, from, next) => {

  const token = localStorage.getItem('_u'); // (Try to) Get the saved token before each request

  if (token) {
    let response
    response = await axios.get(`${config.apiUrl}/api/router?token=` + token)  // Verify if the token is legit
    if (response.data.critical) {localStorage.removeItem('_u'); return next('/')}
    
    if (response.data.authenticated) {
      if (response.data.onboarding) {if (to.path !== '/signup') {return next('/signup')}} 
      else {if (to.path === '/signup' || to.path === '/login') {return next('/dashboard')}}
    }

  // Avoid infinite redirects by allowing access to /signup if authenticated and onboarding
  if (to.path === '/signup' && !response.data.authenticated) {
    return next();
  }

    // Apparently needed to avoid infinite redirects, go figure
    if (to.path === '/signup') {return next()}

    // If the user is onboarding, lock him within /signup route
    else {
      if (to.meta.requiresAuthentication) {
        if (response.data.authenticated === true) { // If requires authentication and authenticated

          if (to.path === '/subscribe') {
            response = await axios.get(`${config.apiUrl}/api/get-user-data`, {params: {token: localStorage.getItem('_u')}})  // Get user data
            localStorage.setItem('_u', response.data.token)
            if (response.data.subscription !== 'none') { // If user wants to access /subscribe while already subscribed, redirect to /profile
              return next('/dashboard');
            }
          }
          if (to.path === '/dashboard') {
            response = await axios.get(`${config.apiUrl}/api/get-user-data`, {params: {token: localStorage.getItem('_u')}})
            localStorage.setItem('_u', response.data.token)
            if (response.data.subscription == 'none') { // If user wants to access /subscribe while already subscribed, redirect to /profile
              return next('/subscribe');
            }
          }
          if (to.meta.requiresSubscription) {
            if (response.data.subscription !== 'none') {
              return next()
            } return next('/subscribe') // If user wants to access any route that requires subscription, redirect to /subscribe
          } return next()
        } return next('/login') // If users token is invalid, redirect to /login
      } return next()
    }
  } 
  if (to.meta.requiresAuthentication) {
    return next('/login') // If user wants to access any route that requires authentication, redirect to /login
  } 
  next()
})

function getNavbarInfo() { // Get user authentication and subscription status
  return new Promise((resolve, reject) => {
    const token = localStorage.getItem('_u'); // Try to get the token from localStorage
    if (token) { // Get user data if token exists
      axios.get(`${config.apiUrl}/api/get-user-data`, { params: { token: token } })
      .then(response => {const subscription = response.data.subscription !== 'none'; resolve({ subscription })})
      .catch(error => {alert('Error retrieving user data:', error); reject(error)})} 
    else {resolve({ subscription: false })} // If no token exists, user is not subscribed
  });
}

export default getNavbarInfo;

// Run app | npm run serve
const app = createApp(App)
app.use(store)
app.use(router)
app.mount('#app')