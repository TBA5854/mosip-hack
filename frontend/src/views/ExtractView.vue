<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { CloudArrowUpIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'

const file = ref<File | null>(null)
const isDragging = ref(false)
const isProcessing = ref(false)
const result = ref<any>(null)
const error = ref<string | null>(null)

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

const uploadFile = async () => {
  if (!file.value) return

  isProcessing.value = true
  error.value = null
  result.value = null

  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('include_quality_score', 'true')

  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/ocr/extract`, formData, {
      headers: { 
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      }
    })
    result.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Extraction failed'
  } finally {
    isProcessing.value = false
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-5xl">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-bold text-gray-100">Extract Data</h1>
      <router-link to="/" class="text-cyan-400 hover:text-cyan-300 transition-colors">Back to Home</router-link>
    </div>

    <div class="grid lg:grid-cols-2 gap-8">
      <!-- Upload Section -->
      <div class="space-y-6">
        <div 
          class="relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300"
          :class="[
            isDragging ? 'border-cyan-400 bg-cyan-400/10' : 'border-gray-700 bg-white/5 hover:border-gray-600'
          ]"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
        >
          <input type="file" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" @change="handleFileSelect" accept="image/*,.pdf" />
          
          <div v-if="file" class="flex flex-col items-center">
            <DocumentTextIcon class="w-12 h-12 text-cyan-400 mb-4" />
            <p class="text-lg font-medium text-gray-200">{{ file.name }}</p>
            <p class="text-sm text-gray-500 mt-1">{{ (file.size / 1024 / 1024).toFixed(2) }} MB</p>
            <button @click.prevent="file = null" class="mt-4 text-sm text-rose-400 hover:text-rose-300 z-10 relative">Remove</button>
          </div>
          
          <div v-else class="flex flex-col items-center">
            <CloudArrowUpIcon class="w-16 h-16 text-gray-500 mb-4" />
            <p class="text-lg font-medium text-gray-300">Drop your file here</p>
            <p class="text-sm text-gray-500 mt-2">or click to browse</p>
            <p class="text-xs text-gray-600 mt-4">Supports PDF, JPG, PNG</p>
          </div>
        </div>

        <button 
          @click="uploadFile" 
          :disabled="!file || isProcessing"
          class="w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-2"
          :class="[
            !file || isProcessing 
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed' 
              : 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:shadow-lg hover:shadow-cyan-500/25 hover:scale-[1.02]'
          ]"
        >
          <span v-if="isProcessing" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
          {{ isProcessing ? 'Processing...' : 'Extract Text' }}
        </button>

        <div v-if="error" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
          {{ error }}
        </div>
      </div>

      <!-- Results Section -->
      <div class="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 min-h-[500px]">
        <h2 class="text-xl font-semibold text-gray-200 mb-6 flex items-center gap-2">
          <DocumentTextIcon class="w-6 h-6 text-cyan-400" />
          Extraction Results
        </h2>

        <div v-if="result" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <!-- Quality Score -->
          <div v-if="result.quality_scores" class="grid grid-cols-2 gap-4">
            <div v-for="score in result.quality_scores" :key="score.page" class="p-4 rounded-xl bg-white/5 border border-white/10">
              <p class="text-sm text-gray-400 mb-1">Page {{ score.page }} Quality</p>
              <div class="flex items-end gap-2">
                <span class="text-2xl font-bold" :class="score.score > 0.8 ? 'text-emerald-400' : 'text-amber-400'">
                  {{ (score.score * 100).toFixed(0) }}%
                </span>
                <span class="text-xs text-gray-500 mb-1">confidence</span>
              </div>
            </div>
          </div>

          <!-- Fields -->
          <div class="space-y-4">
            <div v-for="(value, key) in result.extracted_fields" :key="key" class="group">
              <label class="text-xs uppercase tracking-wider text-gray-500 font-medium ml-1">{{ key }}</label>
              <div class="mt-1 p-3 rounded-lg bg-black/20 border border-white/5 text-gray-200 font-mono text-sm group-hover:border-cyan-500/30 transition-colors">
                {{ value || 'Not detected' }}
              </div>
            </div>
          </div>
          
          <div class="pt-4 border-t border-white/10">
             <p class="text-xs text-gray-500">File ID: <span class="font-mono text-gray-400">{{ result.file_id }}</span></p>
          </div>
        </div>

        <div v-else-if="!isProcessing" class="h-full flex flex-col items-center justify-center text-gray-600">
          <DocumentTextIcon class="w-16 h-16 mb-4 opacity-20" />
          <p>Upload a document to see results</p>
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
