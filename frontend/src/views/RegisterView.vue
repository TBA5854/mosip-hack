<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const isLoading = ref(false)

const handleRegister = async () => {
  if (!username.value || !password.value || !confirmPassword.value) {
    error.value = 'Please fill in all fields'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  isLoading.value = true
  error.value = ''
  
  try {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/register`, {
      username: username.value,
      password: password.value
    })
    
    // Auto login or redirect to login
    router.push('/login')
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Registration failed'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-white mb-2">Create Account</h1>
          <p class="text-gray-400">Join MOSIP OCR Verification System</p>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Username</label>
            <input 
              v-model="username"
              type="text" 
              class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
              placeholder="Choose a username"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Password</label>
            <input 
              v-model="password"
              type="password" 
              class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
              placeholder="Choose a password"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
            <input 
              v-model="confirmPassword"
              type="password" 
              class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
              placeholder="Confirm your password"
            />
          </div>

          <div v-if="error" class="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm text-center">
            {{ error }}
          </div>

          <button 
            type="submit"
            :disabled="isLoading"
            class="w-full py-3.5 rounded-xl font-semibold text-white bg-gradient-to-r from-cyan-500 to-blue-500 hover:shadow-lg hover:shadow-cyan-500/25 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></span>
            {{ isLoading ? 'Creating Account...' : 'Sign Up' }}
          </button>

          <div class="text-center text-sm text-gray-400">
            Already have an account? 
            <router-link to="/login" class="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">Sign in</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
