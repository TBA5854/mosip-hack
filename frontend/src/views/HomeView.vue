<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { DocumentTextIcon, CheckBadgeIcon, QrCodeIcon } from '@heroicons/vue/24/outline'
</script>

<template>
  <div class="container mx-auto px-4 py-12 max-w-6xl">
    <header class="text-center mb-16">
      <h1 class="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-400 mb-4">
        MOSIP OCR Verification
      </h1>
      <p class="text-xl text-gray-400 max-w-2xl mx-auto">
        Secure identity verification system with automated OCR extraction and verifiable credentials.
      </p>
    </header>

    <div class="grid md:grid-cols-3 gap-8">
      <!-- Extract Card -->
      <RouterLink to="/extract" class="group relative p-8 rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 transition-all duration-300 hover:-translate-y-1 shadow-xl">
        <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <div class="w-16 h-16 rounded-xl bg-cyan-500/20 flex items-center justify-center mb-6 text-cyan-400 group-hover:scale-110 transition-transform">
            <DocumentTextIcon class="w-8 h-8" />
          </div>
          <h2 class="text-2xl font-semibold text-gray-100 mb-3">Extract Data</h2>
          <p class="text-gray-400">Upload identity documents to automatically extract text fields using advanced OCR.</p>
        </div>
      </RouterLink>

      <!-- Verify Card -->
      <RouterLink to="/verify" class="group relative p-8 rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 transition-all duration-300 hover:-translate-y-1 shadow-xl">
        <div class="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <div class="w-16 h-16 rounded-xl bg-purple-500/20 flex items-center justify-center mb-6 text-purple-400 group-hover:scale-110 transition-transform">
            <CheckBadgeIcon class="w-8 h-8" />
          </div>
          <h2 class="text-2xl font-semibold text-gray-100 mb-3">Verify Identity</h2>
          <p class="text-gray-400">Compare extracted data with user submissions to validate identity claims.</p>
        </div>
      </RouterLink>

      <!-- Generate VC Card -->
      <RouterLink to="/generate-vc" class="group relative p-8 rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 transition-all duration-300 hover:-translate-y-1 shadow-xl">
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <div class="w-16 h-16 rounded-xl bg-emerald-500/20 flex items-center justify-center mb-6 text-emerald-400 group-hover:scale-110 transition-transform">
            <QrCodeIcon class="w-8 h-8" />
          </div>
          <h2 class="text-2xl font-semibold text-gray-100 mb-3">Generate VC</h2>
          <p class="text-gray-400">Issue cryptographically secure Verifiable Credentials and QR codes.</p>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
