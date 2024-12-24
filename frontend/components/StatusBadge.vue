<template>
  <span
    :class="[
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
      statusClasses[status.toLowerCase()] || 'bg-gray-100 text-gray-800'
    ]"
  >
    {{ status }}
  </span>
</template>

<script setup>
const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const statusClasses = {
  draft: 'bg-gray-100 text-gray-800',
  sent: 'bg-blue-100 text-blue-800',
  accepted: 'bg-green-100 text-green-800',
  declined: 'bg-red-100 text-red-800',
  paid: 'bg-green-100 text-green-800',
  pending: 'bg-yellow-100 text-yellow-800',
  posted: 'bg-green-100 text-green-800',
  voided: 'bg-red-100 text-red-800',
  deleted: 'bg-gray-100 text-gray-800',
  overdue: 'bg-red-100 text-red-800'
}
</script>
