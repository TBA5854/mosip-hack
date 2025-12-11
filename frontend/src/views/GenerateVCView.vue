<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { QrCodeIcon, ArrowDownTrayIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const fileId = ref('')
const verifiedData = ref('')
const isProcessing = ref(false)
const result = ref<any>(null)
const error = ref<string | null>(null)
const ocrUrl = import.meta.env.VITE_OCR_URL

onMounted(() => {
  if (route.query.fileId) {
    fileId.value = route.query.fileId as string
  }
  if (route.query.data) {
    verifiedData.value = route.query.data as string
  }
})

const generateVC = async () => {
  if (!fileId.value || !verifiedData.value) return

  isProcessing.value = true
  error.value = null
  result.value = null

  const formData = new FormData()
  formData.append('file_id', fileId.value)
  formData.append('verified_data', verifiedData.value)

  try {
    const response = await axios.post(`${import.meta.env.VITE_OCR_URL}/api/generate-vc`, formData)
    result.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'VC Generation failed'
  } finally {
    isProcessing.value = false
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-bold text-gray-100">Generate Credential</h1>
      <router-link to="/" class="text-cyan-400 hover:text-cyan-300 transition-colors">Back to Home</router-link>
    </div>

    <div class="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 shadow-2xl">
      <div v-if="!result" class="space-y-6">
        <div class="p-6 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-6">
          <h3 class="font-semibold text-lg mb-2">Ready to Issue</h3>
          <p class="text-sm opacity-80">Verification successful. You can now generate a cryptographically secure Verifiable Credential for this identity.</p>
        </div>

        <div class="grid gap-4">
           <div>
            <label class="block text-xs text-gray-500 mb-1">File ID</label>
            <input v-model="fileId" type="text" readonly class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-400 font-mono text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Verified Data Payload</label>
            <textarea v-model="verifiedData" rows="4" readonly class="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-gray-400 font-mono text-xs"></textarea>
          </div>
        </div>

        <button 
          @click="generateVC" 
          :disabled="isProcessing"
          class="w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:shadow-lg hover:shadow-emerald-500/25 hover:scale-[1.02]"
        >
          <span v-if="isProcessing" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
          {{ isProcessing ? 'Generating...' : 'Generate Verifiable Credential' }}
        </button>
        
        <div v-if="error" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
          {{ error }}
        </div>
      </div>

      <div v-else class="text-center space-y-8 animate-in fade-in zoom-in duration-500">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-emerald-500/20 text-emerald-400 mb-4">
          <QrCodeIcon class="w-10 h-10" />
        </div>
        
        <h2 class="text-3xl font-bold text-white">Credential Issued!</h2>
        <p class="text-gray-400 max-w-md mx-auto">Your Verifiable Credential has been successfully generated and signed.</p>

        <div class="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto mt-8">
          <!-- Download VC -->
          <a :href="`${ocrUrl}${result.vc_download_url}`" target="_blank" class="group p-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-left">
            <div class="flex items-center justify-between mb-4">
              <span class="p-2 rounded-lg bg-cyan-500/20 text-cyan-400">JSON</span>
              <ArrowDownTrayIcon class="w-5 h-5 text-gray-500 group-hover:text-white transition-colors" />
            </div>
            <h3 class="font-semibold text-gray-200">Download VC</h3>
            <p class="text-xs text-gray-500 mt-1">W3C Verifiable Credential Format</p>
          </a>

          <!-- Download QR -->
          <a :href="`${ocrUrl}${result.qr_download_url}`" target="_blank" class="group p-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-left">
            <div class="flex items-center justify-between mb-4">
              <span class="p-2 rounded-lg bg-purple-500/20 text-purple-400">PNG</span>
              <ArrowDownTrayIcon class="w-5 h-5 text-gray-500 group-hover:text-white transition-colors" />
            </div>
            <h3 class="font-semibold text-gray-200">Download QR Code</h3>
            <p class="text-xs text-gray-500 mt-1">For mobile wallet scanning</p>
          </a>
        </div>
        
        <div class="pt-8 mt-8 border-t border-white/10">
          <button @click="result = null" class="text-gray-500 hover:text-white transition-colors text-sm">Generate Another</button>
        </div>
      </div>
    </div>
  </div>
</template>
