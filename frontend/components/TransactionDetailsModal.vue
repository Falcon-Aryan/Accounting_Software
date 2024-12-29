<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100]" style="margin-left: 256px;">
    <div class="fixed inset-0 z-[101]" @click="$emit('close')"></div>
    <div class="bg-white rounded-lg shadow-lg w-full max-w-4xl mx-auto relative z-[102]">
      <!-- Header -->
      <div class="flex justify-between items-center px-6 py-4 border-b">
        <div class="flex items-center gap-3">
          <h2 class="text-lg font-medium">Transaction Details</h2>
          <span :class="{
            'px-2 py-0.5 rounded text-sm font-medium': true,
            'bg-green-100 text-green-800': transaction.status === 'posted',
            'bg-yellow-100 text-yellow-800': transaction.status === 'draft',
            'bg-red-100 text-red-800': transaction.status === 'voided',
          }">
            {{ transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1) }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>
      </div>
      
      <!-- Content -->
      <div class="p-6 space-y-6">
        <!-- Basic Info -->
        <div class="grid grid-cols-2 gap-x-12 gap-y-4">
          <div>
            <p class="text-sm text-gray-500 mb-1">Transaction ID</p>
            <p class="font-medium">{{ transaction.id }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">Reference Number</p>
            <p class="font-medium">{{ transaction.reference_number || 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">Date</p>
            <p class="font-medium">{{ formatDate(transaction.date) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">Transaction Type</p>
            <p class="font-medium">{{ formatTransactionType(transaction.transaction_type) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">Sub Type</p>
            <p class="font-medium">{{ formatSubType(transaction.sub_type) }}</p>
          </div>
          <div v-if="transaction.customer_name">
            <p class="text-sm text-gray-500 mb-1">Customer</p>
            <p class="font-medium">{{ transaction.customer_name }}</p>
          </div>
        </div>

        <!-- Products Section -->
        <div v-if="transaction.products && transaction.products.length > 0">
          <h3 class="font-medium mb-3">Products</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Name</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Price</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Quantity</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Total</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="product in transaction.products" :key="product.id">
                  <td class="px-4 py-2">{{ product.name }}</td>
                  <td class="px-4 py-2">{{ product.description }}</td>
                  <td class="px-4 py-2">{{ formatAmount(product.price) }}</td>
                  <td class="px-4 py-2">{{ product.quantity }}</td>
                  <td class="px-4 py-2">{{ formatAmount(product.price * product.quantity) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="4" class="px-4 py-2 text-sm font-medium text-right">Total:</td>
                  <td class="px-4 py-2 text-sm font-medium">{{ formatAmount(calculateTotal(transaction.products)) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- Entries Section -->
        <div>
          <h3 class="font-medium mb-3">Entries</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Account</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Type</th>
                  <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Amount</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="entry in transaction.entries" :key="entry.accountId">
                  <td class="px-4 py-2">{{ entry.accountName }} <span class="text-gray-500 text-sm">({{ entry.accountId }})</span></td>
                  <td class="px-4 py-2">{{ entry.description }}</td>
                  <td class="px-4 py-2">
                    <span :class="{
                      'px-2 py-0.5 rounded text-sm': true,
                      'bg-blue-50 text-blue-700': entry.type === 'debit',
                      'bg-purple-50 text-purple-700': entry.type === 'credit'
                    }">
                      {{ entry.type.charAt(0).toUpperCase() + entry.type.slice(1) }}
                    </span>
                  </td>
                  <td class="px-4 py-2 text-right">{{ formatAmount(entry.amount) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Audit Info -->
        <div class="grid grid-cols-2 gap-x-12 gap-y-4 pt-4 border-t">
          <div>
            <p class="text-sm text-gray-500 mb-1">Created At</p>
            <p class="font-medium">{{ formatDate(transaction.created_at) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">Updated At</p>
            <p class="font-medium">{{ formatDate(transaction.updated_at) }}</p>
          </div>
          <div v-if="transaction.posted_at">
            <p class="text-sm text-gray-500 mb-1">Posted At</p>
            <p class="font-medium">{{ formatDate(transaction.posted_at) }}</p>
          </div>
          <div v-if="transaction.voided_at">
            <p class="text-sm text-gray-500 mb-1">Voided At</p>
            <p class="font-medium">{{ formatDate(transaction.voided_at) }}</p>
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

function calculateTotal(products) {
  if (!products) return 0
  return products.reduce((sum, product) => sum + (Number(product.price) * Number(product.quantity) || 0), 0)
}

function formatTransactionType(type) {
  if (!type) return ''
  // Convert snake_case to Title Case
  return type.split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

function formatSubType(subType) {
  if (!subType) return ''
  // Convert snake_case to Title Case
  return subType.split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}
</script>
