<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
    <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold">Transaction Details</h2>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
          ✕
        </button>
      </div>
      
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500">Transaction ID</p>
            <p class="font-medium">{{ transaction.id }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Date</p>
            <p class="font-medium">{{ formatDate(transaction.date) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Status</p>
            <p class="font-medium">{{ transaction.status }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Reference</p>
            <p class="font-medium">{{ transaction.reference }}</p>
          </div>
        </div>

        <div>
          <h3 class="font-medium mb-2">Entries</h3>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Account</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Type</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Amount</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="entry in transaction.entries" :key="entry.accountId">
                <td class="px-4 py-2 text-sm">{{ entry.accountId }}</td>
                <td class="px-4 py-2 text-sm">{{ entry.description }}</td>
                <td class="px-4 py-2 text-sm">{{ entry.type }}</td>
                <td class="px-4 py-2 text-sm">{{ formatAmount(entry.amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-4 pt-4 border-t">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500">Created At</p>
              <p class="font-medium">{{ formatDate(transaction.created_at) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Updated At</p>
              <p class="font-medium">{{ formatDate(transaction.updated_at) }}</p>
            </div>
            <div v-if="transaction.posted_at">
              <p class="text-sm text-gray-500">Posted At</p>
              <p class="font-medium">{{ formatDate(transaction.posted_at) }}</p>
            </div>
            <div v-if="transaction.voided_at">
              <p class="text-sm text-gray-500">Voided At</p>
              <p class="font-medium">{{ formatDate(transaction.voided_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  transaction: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

function formatAmount(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
</script>
