<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Estimate Report</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">Detailed information about the estimate.</p>
          </div>
          <BaseButton @click="$router.push('/estimates')">
            Back to Estimates
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
              <dt class="text-sm font-medium text-gray-500">Estimate Number</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ estimate.estimate_no }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Status</dt>
              <dd class="mt-1 text-sm sm:mt-0 sm:col-span-2">
                {{ estimate.status }}
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Customer</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ estimate.customer_name }}
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Date</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(estimate.date) }}
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Due Date</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(estimate.expiry_date) }}
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Products</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div class="border rounded-md">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                        <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                        <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
                        <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Price</th>
                        <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="item in estimate.line_items" :key="item.product_id">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ item.product_id }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900">{{ item.description }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ item.quantity }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(item.unit_price) }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(item.total) }}</td>
                      </tr>
                      <tr class="bg-gray-50">
                        <td colspan="4" class="px-4 py-3 text-sm font-medium text-gray-900 text-left">Total:</td>
                        <td class="px-4 py-3 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(estimate.total) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Notes</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 whitespace-pre-wrap">{{ estimate.notes || 'No notes' }}</dd>
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
import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { firebaseConfig } from '../../../config/firebase.config'

definePageMeta({
  middleware: ['auth']
})

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

async function getIdToken() {
  const user = auth.currentUser
  if (!user) {
    throw new Error('No authenticated user')
  }
  return user.getIdToken()
}

const config = useRuntimeConfig()
const route = useRoute()
const estimate = ref(null)
const isLoading = ref(true)
const error = ref(null)


const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatCurrency = (value) => {
  if (!value) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const fetchEstimate = async () => {
  try {
    isLoading.value = true
    error.value = null
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/estimates/get_estimate/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!response.ok) {
      throw new Error('Failed to fetch estimate data')
    }
    const data = await response.json()
    estimate.value = data
  } catch (err) {
    handleError(err)
  } finally {
    isLoading.value = false
  }
}

function handleError(error) {
  if (error.message === 'No authenticated user') {
    error.value = 'Please log in to perform this action'
  } else {
    error.value = error.message
  }
  console.error('Error:', error)
}

onMounted(() => {
  fetchEstimate()
})
</script>
