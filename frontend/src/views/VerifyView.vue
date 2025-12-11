<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { CloudArrowUpIcon, CheckBadgeIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const file = ref<File | null>(null)
const isDragging = ref(false)
const isProcessing = ref(false)
const result = ref<any>(null)
const error = ref<string | null>(null)

const formData = ref({
  name: '',
  dob: '',
  age: null as number | null,
  address: '',
  gender: '',
  email: '',
  phone: ''
})

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    file.value = files[0] as File
  }
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    file.value = target.files[0] as File
  }
}

const verifyData = async () => {
  if (!file.value) return

  isProcessing.value = true
  error.value = null
  result.value = null

  const submitData = new FormData()
  submitData.append('file', file.value)
  submitData.append('submitted_data', JSON.stringify(formData.value))

  try {
    const response = await axios.post(`${import.meta.env.VITE_OCR_URL}/api/verify`, submitData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Verification failed'
  } finally {
    isProcessing.value = false
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-6xl">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-bold text-gray-100">Verify Identity</h1>
      <router-link to="/" class="text-cyan-400 hover:text-cyan-300 transition-colors">Back to Home</router-link>
    </div>

    <div class="grid lg:grid-cols-2 gap-8">
      <!-- Input Section -->
      <div class="space-y-8">
        <!-- File Upload -->
        <div 
          class="relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300"
          :class="[
            isDragging ? 'border-cyan-400 bg-cyan-400/10' : 'border-gray-700 bg-white/5 hover:border-gray-600'
          ]"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
        >
          <input type="file" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" @change="handleFileSelect" accept="image/*,.pdf" />
          
          <div v-if="file" class="flex items-center justify-center gap-4">
            <CheckBadgeIcon class="w-8 h-8 text-cyan-400" />
            <div class="text-left">
              <p class="text-sm font-medium text-gray-200">{{ file.name }}</p>
              <p class="text-xs text-gray-500">{{ (file.size / 1024 / 1024).toFixed(2) }} MB</p>
            </div>
            <button @click.prevent="file = null" class="ml-auto text-xs text-rose-400 hover:text-rose-300 z-10 relative">Remove</button>
          </div>
          
          <div v-else class="flex flex-col items-center">
            <CloudArrowUpIcon class="w-10 h-10 text-gray-500 mb-2" />
            <p class="text-sm text-gray-300">Upload ID Document</p>
          </div>
        </div>

        <!-- Form Data -->
        <div class="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6">
          <h2 class="text-lg font-semibold text-gray-200 mb-4">Claimed Data</h2>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Full Name</label>
                <input v-model="formData.name" type="text" class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50" placeholder="John Doe" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Date of Birth</label>
                <input v-model="formData.dob" type="text" class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50" placeholder="YYYY-MM-DD" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Age</label>
                <input v-model.number="formData.age" type="number" class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50" placeholder="25" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Gender</label>
                <select v-model="formData.gender" class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50">
                  <option value="">Select</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Address</label>
              <textarea v-model="formData.address" rows="2" class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50" placeholder="Full Address"></textarea>
            </div>
             <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Email</label>
                <input v-model="formData.email" type="email" class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50" placeholder="john@example.com" />
              </div>
              <div>
                 <label class="block text-xs text-gray-500 mb-1">Phone</label>
                <input v-model="formData.phone" type="tel" class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50" placeholder="+1234567890" />
              </div>
            </div>
          </div>
        </div>

        <button 
          @click="verifyData" 
          :disabled="!file || isProcessing"
          class="w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-2"
          :class="[
            !file || isProcessing 
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed' 
              : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg hover:shadow-purple-500/25 hover:scale-[1.02]'
          ]"
        >
          <span v-if="isProcessing" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
          {{ isProcessing ? 'Verifying...' : 'Verify Identity' }}
        </button>
        
        <div v-if="error" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
          {{ error }}
        </div>
      </div>

      <!-- Results Section -->
      <div class="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 min-h-[600px]">
        <h2 class="text-xl font-semibold text-gray-200 mb-6 flex items-center gap-2">
          <CheckBadgeIcon class="w-6 h-6 text-purple-400" />
          Verification Results
        </h2>

        <div v-if="result" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <!-- Overall Score -->
          <div class="p-6 rounded-xl border flex items-center justify-between"
            :class="result.overall_match ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-rose-500/10 border-rose-500/20'"
          >
            <div>
              <p class="text-sm text-gray-400 mb-1">Overall Status</p>
              <h3 class="text-2xl font-bold" :class="result.overall_match ? 'text-emerald-400' : 'text-rose-400'">
                {{ result.overall_match ? 'Verified' : 'Mismatch' }}
              </h3>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-400 mb-1">Confidence Score</p>
              <span class="text-3xl font-bold text-gray-100">{{ (result.overall_score * 100).toFixed(0) }}%</span>
            </div>
          </div>

          <!-- Field Breakdown -->
          <div class="space-y-3">
            <h3 class="text-sm font-medium text-gray-400 uppercase tracking-wider mb-2">Field Analysis</h3>
            <div v-for="(fieldData, fieldName) in result.verification_result" :key="fieldName" 
              class="p-3 rounded-lg border flex items-center justify-between transition-colors"
              :class="fieldData.match ? 'bg-emerald-500/5 border-emerald-500/10' : 'bg-rose-500/5 border-rose-500/10'"
            >
              <div class="flex items-center gap-3">
                <div class="w-2 h-2 rounded-full" :class="fieldData.match ? 'bg-emerald-500' : 'bg-rose-500'"></div>
                <span class="text-gray-200 capitalize">{{ fieldName }}</span>
              </div>
              <div class="flex items-center gap-4">
                <span class="text-xs text-gray-500" v-if="fieldData.confidence">
                  {{ (fieldData.confidence * 100).toFixed(0) }}% match
                </span>
                 <component :is="fieldData.match ? CheckBadgeIcon : ExclamationTriangleIcon" 
                  class="w-5 h-5" 
                  :class="fieldData.match ? 'text-emerald-400' : 'text-rose-400'" 
                />
              </div>
            </div>
          </div>
          
          <div class="pt-6 mt-6 border-t border-white/10 flex justify-end">
             <router-link 
               v-if="result.overall_match"
               :to="{ path: '/generate-vc', query: { fileId: result.file_id, data: JSON.stringify(result.verification_result) } }"
               class="px-6 py-2 rounded-lg bg-emerald-500 text-white font-medium hover:bg-emerald-600 transition-colors flex items-center gap-2"
             >
               Proceed to VC Generation
             </router-link>
          </div>
        </div>

        <div v-else-if="!isProcessing" class="h-full flex flex-col items-center justify-center text-gray-600">
          <CheckBadgeIcon class="w-16 h-16 mb-4 opacity-20" />
          <p>Submit data to see verification results</p>
        </div>
        
         <div v-else class="h-full flex flex-col items-center justify-center text-gray-500">
           <div class="animate-pulse flex flex-col items-center">
             <div class="h-4 w-32 bg-white/10 rounded mb-4"></div>
             <div class="h-4 w-48 bg-white/10 rounded"></div>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>
