<template>
  <div class="backdrop" v-if="showError"><ErrorComp :action="action" @close="handleCloseError" /></div>
</template>


<script>
import { createClient } from '@supabase/supabase-js'
import ErrorComp from '../components/ErrorComp.vue';
import { config } from '@/config';
import axios from 'axios';
import webdata from '../webdata.json'
export default {
  components: {
    ErrorComp
  },
  name: 'SupabaseComponent',
  data() {
    return {
      supabase: null,
      user: null,
      showError: false,
      action: null
    }
  },
  async mounted() {
    const SUPABASE_KEY = webdata.supabaseKey
    const SUPABASE_URL = webdata.supabaseURL
    this.supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

    const params = new URLSearchParams(window.location.hash.substring(1))
    const accessToken = params.get('access_token')
    const refreshToken = params.get('refresh_token')

    if (accessToken && refreshToken) {

      await this.supabase.auth.setSession({access_token: accessToken, refresh_token: refreshToken,})
      const { data } = await this.supabase.auth.getSession()
      const response = await axios.post(`${config.apiUrl}/api/authenticate`, {
        id: data.session.user.id,
        email: data.session.user.email, 
        name: data.session.user.user_metadata.full_name, 
        auth_type: data.session.user.app_metadata.provider
      })
      if (response.data.error) {
        this.action = response.data.error
        this.showError = true
        return
      }

      localStorage.setItem('_u', response.data.token)
      this.$router.push('/dashboard')
    }
  }
}

</script>