<template>
  <button
    :type="type"
    :class="[
      'px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2',
      variant === 'primary' ? 'text-white bg-green-600 hover:bg-green-700 focus:ring-green-500' :
      variant === 'secondary' ? 'text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-green-500' :
      variant === 'danger' ? 'text-white bg-red-600 hover:bg-red-700 focus:ring-red-500' :
      'text-white bg-green-600 hover:bg-green-700 focus:ring-green-500'
    ]"
    @click="$emit('click')"
  >
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'button'
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger'].includes(value)
  }
})

defineEmits(['click'])
</script>
