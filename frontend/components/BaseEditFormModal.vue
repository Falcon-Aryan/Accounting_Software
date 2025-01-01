<template>
  <div v-if="isOpen" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border shadow-lg rounded-md bg-white" :class="modalWidth">
      <div class="mt-3">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium leading-6 text-gray-900">{{ title }}</h3>
          <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Main Content -->
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  width: {
    type: String,
    default: 'md'
  }
})

const modalWidth = computed(() => {
  const widths = {
    sm: 'w-[500px]',
    md: 'w-[800px]',
    lg: 'w-[1000px]',
    xl: 'w-[1200px]'
  }
  return widths[props.width] || widths.md
})

defineEmits(['close'])
</script>

<style scoped>
/* Add any edit-specific styling here if needed */
</style>
