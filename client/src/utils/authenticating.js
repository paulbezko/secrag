import axios from 'axios';
import { config } from '@/config';
import webdata from '../webdata.json'
import { createClient } from '@supabase/supabase-js'

export const authenticating = {

  async login(ctx, email, password) {
    ctx.inputEmail = '';
    ctx.inputPassword = '';
    const response = await axios.post(`${config.apiUrl}/api/login`, {token: localStorage.getItem('_u'), email: email, password: password});
    if (response.data.error) {ctx.sendManualAssistantMessage(response.data.error)}
    else {
      ctx.userStatus = response.data.user_status; 
      ctx.inputMode = 'default';
      ctx.getPremadeSuggestions()
      ctx.organicSuggestions = ['Tell me more']
      ctx.chat = [{ role: 'assistant', content: '' }];
      ctx.sendManualAssistantMessage('Welcome back!');
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
      ctx.sendManualAssistantMessage(response.data.error);
    }
    else {
      ctx.userStatus = response.data.user_status; 
      ctx.inputMode = 'default';
      ctx.getPremadeSuggestions()
      ctx.organicSuggestions = ['Tell me more']
      ctx.chat = [{ role: 'assistant', content: '' }];
      ctx.sendManualAssistantMessage('Welcome back!');
      localStorage.setItem('_u', response.data.token);
    }
  },

  async forgotPassword(ctx, email) {
    ctx.responseIsProcessing = true;
    const response = await axios.post(`${config.apiUrl}/api/forgot-password`, {email: email, socketId: ctx.socketId});
    if (response.data.error) {ctx.sendManualAssistantMessage(response.data.error)}
    else {
      ctx.inputMode = 'default';
      ctx.sendManualAssistantMessage('<br>Success! An email with a password reset link has been sent.');
    }
    ctx.inputEmail = '';
    ctx.responseIsProcessing = false;
  },

  async resetPassword(ctx, password, passwordConfirm) {
    ctx.responseIsProcessing = true;

    const passwordStrengthRegex = /^(?=.*\d)(?=.*[!@#$%^&*:;_\-.])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    if (password === '' || passwordConfirm === '') {ctx.sendManualAssistantMessage("<br>Please provide your new password.")}
    else if (password !== passwordConfirm) {ctx.sendManualAssistantMessage("<br>Passwords do not match.")}
    else if (!passwordStrengthRegex.test(password)) {ctx.sendManualAssistantMessage("<br>ctx password is not strong enough. Try a different one.")}
    else {
      const urlToken = new URLSearchParams(window.location.search).get("token");
      const response = await axios.post(`${config.apiUrl}/api/reset-password`, {token: urlToken, password: password});
      if (response.data.error) {ctx.sendManualAssistantMessage(response.data.error)}
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