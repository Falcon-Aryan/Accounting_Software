<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Account Report</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">Detailed information about the account.</p>
          </div>
          <BaseButton @click="$router.push('/chart-of-accounts')">
            Back to Chart of Accounts
          </BaseButton>
        </div>
        
        <div v-if="isLoading" class="px-4 py-5 sm:p-6">
          <div class="flex justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </div>

        <div v-else-if="error" class="px-4 py-5 sm:p-6">
          <p class="text-red-600">{{ error }}</p>
        </div>

        <div v-else class="border-t border-gray-200">
          <dl>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Account ID</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ account.id }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Name</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ account.name }}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Type</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ account.accountType }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Detail Type</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ account.detailType }}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Description</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ account.description || 'No description' }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Current Balance</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ formatCurrency(account.balance) }}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Status</dt>
              <dd class="mt-1 text-sm sm:mt-0 sm:col-span-2">
                <span :class="getStatusClass">{{ account.isActive ? 'Active' : 'Inactive' }}</span>
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Default Account</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ account.isDefault ? 'Yes' : 'No' }}
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Created At</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(account.created_at) }}
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(account.updated_at) }}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRuntimeConfig, useRoute } from '#app'

const config = useRuntimeConfig()
const route = useRoute()
const account = ref(null)
const isLoading = ref(true)
const error = ref(null)

const getStatusClass = computed(() => {
  const baseClasses = 'px-2 py-1 text-xs font-medium rounded-full'
  return account.value?.isActive
    ? `${baseClasses} bg-green-100 text-green-800`
    : `${baseClasses} bg-gray-100 text-gray-800`
})

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value || 0)
}

const fetchAccount = async () => {
  try {
    isLoading.value = true
    error.value = null
    const response = await fetch(`${config.public.apiBase}/api/coa/get/${route.params.id}`)
    if (!response.ok) {
      throw new Error('Failed to fetch account data')
    }
    const data = await response.json()
    account.value = data
  } catch (err) {
    error.value = err.message
    console.error('Error fetching account:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAccount()
})
</script>
