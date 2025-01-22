import axios from 'axios';
import { config } from '@/config';
import webdata from '../webdata.json'
import { createClient } from '@supabase/supabase-js'

export const authenticating = {

  async signupEmail(ctx, email) {
    ctx.responseIsProcessing = true;
    if (email === '') {this.sendManualAssistantMessage("<br>Please provide your email address.")}
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {this.sendManualAssistantMessage("<br>Please provide a valid email address.")}
    else {
      const response = await axios.post(`${config.apiUrl}/api/signup-email`, {token: localStorage.getItem('_u'), email: email, socketId: ctx.socketId});
      if (response.data.error) {ctx.sendManualAssistantMessage(ctx, '<br>' + response.data.error)}
      else {ctx.inputMode = 'default'; ctx.sendManualAssistantMessage(ctx, '<br>Success! An email with a confirmation link has been sent.');
      }
    }
    ctx.inputEmail = '';
    ctx.responseIsProcessing = false;
  },

  async signupPassword(ctx, password, passwordConfirm) {
    ctx.responseIsProcessing = true;
    const passwordStrengthRegex = /^(?=.*\d)(?=.*[!@#$%^&*:;_\-.])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    if (password === '' || passwordConfirm === '') {ctx.sendManualAssistantMessage(ctx, "<br>Please provide your password.")}
    else if (password !== passwordConfirm) {ctx.sendManualAssistantMessage(ctx, "<br>Passwords do not match.")}
    else if (!passwordStrengthRegex.test(password)) {ctx.sendManualAssistantMessage(ctx, "<br>This password is not strong enough. Try a different one.")}
    else {
      const response = await axios.post(`${config.apiUrl}/api/signup-password`, {token: localStorage.getItem('_u'), password: password, socketId: ctx.socketId});
      if (response.data.error) {ctx.sendManualAssistantMessage(ctx,'<br>' + response.data.error)}
      else {
        ctx.inputMode = 'default';
        ctx.sendManualAssistantMessage(ctx, '<br>Success! Now you can login anytime you want.');
        ctx.getPremadeSuggestions();
      }
    }
    ctx.inputEmail = '';
    ctx.inputPassword = '';
    ctx.responseIsProcessing = false;
  },

  async login(ctx, email, password) {
    ctx.inputEmail = '';
    ctx.inputPassword = '';
    const response = await axios.post(`${config.apiUrl}/api/login`, {token: localStorage.getItem('_u'), email: email, password: password});
    if (response.data.error) {ctx.sendManualAssistantMessage(ctx, response.data.error)}
    else {
      ctx.userStatus = response.data.user_status; 
      ctx.inputMode = 'default';
      ctx.getPremadeSuggestions()
      ctx.organicSuggestions = ['Tell me more']
      ctx.chat = [{ role: 'assistant', content: '' }];
      ctx.sendManualAssistantMessage(ctx, 'Welcome back!');
      localStorage.setItem('_u', response.data.token);
    }
  },

  async authenticateWithGoogle() {
    const SUPABASE_KEY = webdata.supabaseKey
    const SUPABASE_URL = webdata.supabaseURL
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
    await supabase.auth.signInWithOAuth({provider: 'google', "options": {"redirectTo": `${config.webUrl}/`}})
  },

  async HandleSupabaseAuth(ctx, urlSupabaseAccessToken, urlSupabaseRefreshToken) {
    const SUPABASE_KEY = webdata.supabaseKey
    const SUPABASE_URL = webdata.supabaseURL
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
    await supabase.auth.setSession({access_token: urlSupabaseAccessToken, refresh_token: urlSupabaseRefreshToken,})
    const { data } = await supabase.auth.getSession()
    const response = await axios.post(`${config.apiUrl}/api/authenticate-with-supabase`, {
      token: localStorage.getItem('_u'),
      supabase_user_id: data.session.user.id,
      email: data.session.user.email, 
      name: data.session.user.user_metadata.full_name, 
      auth_type: data.session.user.app_metadata.provider
    })
    if (response.data.error) {
      ctx.chat=[{ role: 'assistant', content: '' }];
      ctx.sendManualAssistantMessage(ctx, response.data.error);
    }
    else {
      localStorage.setItem('_u', response.data.token);
      ctx.userStatus = response.data.user_status; 
      ctx.inputMode = 'default';
      ctx.getPremadeSuggestions()
      ctx.organicSuggestions = ['Tell me more'];
      ctx.getXMoreMessages();
      ctx.sendManualAssistantMessage(ctx, 'Welcome back!');
    }
  },

  async forgotPassword(ctx, email) {
    ctx.responseIsProcessing = true;
    const response = await axios.post(`${config.apiUrl}/api/forgot-password`, {email: email, socketId: ctx.socketId});
    if (response.data.error) {ctx.sendManualAssistantMessage(ctx, response.data.error)}
    else {
      ctx.inputMode = 'default';
      ctx.sendManualAssistantMessage(ctx, '<br>Success! An email with a password reset link has been sent.');
    }
    ctx.inputEmail = '';
    ctx.responseIsProcessing = false;
  },

  async resetPassword(ctx, password, passwordConfirm) {
    ctx.responseIsProcessing = true;

    const passwordStrengthRegex = /^(?=.*\d)(?=.*[!@#$%^&*:;_\-.])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    if (password === '' || passwordConfirm === '') {ctx.sendManualAssistantMessage(ctx, "<br>Please provide your new password.")}
    else if (password !== passwordConfirm) {ctx.sendManualAssistantMessage(ctx, "<br>Passwords do not match.")}
    else if (!passwordStrengthRegex.test(password)) {ctx.sendManualAssistantMessage(ctx, "<br>ctx password is not strong enough. Try a different one.")}
    else {
      const urlToken = new URLSearchParams(window.location.search).get("token");
      const response = await axios.post(`${config.apiUrl}/api/reset-password`, {token: urlToken, password: password});
      if (response.data.error) {ctx.sendManualAssistantMessage(ctx, response.data.error)}
      else {
        localStorage.setItem('_q', 'Success! You can now login with your new password.');
        localStorage.removeItem('_u');
        window.location.href = '/'
      }
    }
    ctx.inputPassword = '';
    ctx.inputPasswordConfirm = '';
    ctx.responseIsProcessing = false;
  },

  signOut() {
    localStorage.removeItem('_u');
    window.location.reload()
  },
}