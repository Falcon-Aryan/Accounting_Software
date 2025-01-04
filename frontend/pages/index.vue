<template>
  <div>
    <!-- This page will redirect to dashboard -->
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { navigateTo } from '#app'

onMounted(() => {
  navigateTo('/dashboard')
})
</script>