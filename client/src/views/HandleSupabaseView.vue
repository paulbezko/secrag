<template>
  <div></div>
</template>


<script>
import { createClient } from '@supabase/supabase-js'
import { config } from '@/config';
import axios from 'axios';
export default {
  name: 'LoginComponent',
  data() {
    return {
      supabase: null,
      user: null,
    }
  },
  async mounted() {
    const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpiemtzcWFrdG15bXJzcXJndmZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTg4MTkyNjQsImV4cCI6MjAzNDM5NTI2NH0.d2PgiDLfP5AVPBaJM_s--TgTfIAErZu0FmdHuPV-5Fs'
    const SUPABASE_URL = 'https://jbzksqaktmymrsqrgvfo.supabase.co'
    this.supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

    const params = new URLSearchParams(window.location.hash.substring(1))
    const accessToken = params.get('access_token')
    const refreshToken = params.get('refresh_token')

    if (accessToken && refreshToken) {

      await this.supabase.auth.setSession({access_token: accessToken, refresh_token: refreshToken,})
      const { data } = await this.supabase.auth.getSession()

      console.log(config.apiUrl)

      const response = await axios.post(`${config.apiUrl}/api/authenticate`, {
        id: data.session.user.id,
        email: data.session.user.email, 
        name: data.session.user.user_metadata.full_name, 
        auth_type: data.session.user.app_metadata.provider
      })

      localStorage.setItem('_u', response.data.token)
      this.$router.push('/dashboard')
    }
  }
}

</script>