<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Customer Report</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">Detailed information about the customer.</p>
          </div>
          <BaseButton @click="$router.push('/customers')">
            Back to Customers
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
              <dt class="text-sm font-medium text-gray-500">Customer ID</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ customer.customer_no }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Full name</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ customer.first_name }} {{ customer.last_name }}
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Company name</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ customer.company_name || 'N/A' }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Email address</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ customer.email }}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Phone number</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ customer.phone }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Website</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <a v-if="customer.website" :href="customer.website" target="_blank" class="text-green-600 hover:text-green-500">
                  {{ customer.website }}
                </a>
                <span v-else>N/A</span>
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Billing Address</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatAddress(customer.billing_address) }}
              </dd>
            </div>
            <div v-if="!customer.use_billing_for_shipping" class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Shipping Address</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatAddress(customer.shipping_address) }}
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Created At</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ new Date(customer.created_at).toLocaleString() }}
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ new Date(customer.updated_at).toLocaleString() }}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRuntimeConfig, useRoute } from '#app'

const config = useRuntimeConfig()
const route = useRoute()
const customer = ref(null)
const isLoading = ref(true)
const error = ref(null)

const formatAddress = (address) => {
  if (!address) return 'N/A'
  const parts = [
    address.street,
    address.city,
    address.state,
    address.postal_code,
    address.country
  ]
  return parts.filter(Boolean).join(', ')
}

const fetchCustomer = async () => {
  try {
    isLoading.value = true
    error.value = null
    const response = await fetch(`${config.public.apiBase}/api/customers/get_customer/${route.params.id}`)
    if (!response.ok) {
      throw new Error('Failed to fetch customer data')
    }
    const data = await response.json()
    customer.value = data.customer
  } catch (err) {
    error.value = err.message
    console.error('Error fetching customer:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchCustomer()
})
</script>
