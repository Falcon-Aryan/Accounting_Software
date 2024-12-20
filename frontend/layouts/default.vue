<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <Sidebar />
    
    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto pl-64">
      <slot />
    </main>
  </div>
</template>

<script setup>
import Sidebar from '~/components/Sidebar.vue'
</script>
