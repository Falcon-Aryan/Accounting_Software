<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Product Report</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">Detailed information about the product or service.</p>
          </div>
          <BaseButton @click="$router.push('/prodServ')">
            Back to Products & Services
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
              <dt class="text-sm font-medium text-gray-500">Name</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ product.name }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Type</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <span :class="getTypeClass">{{ formatType(product.type) }}</span>
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">SKU</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ product.sku || 'N/A' }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Description</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ product.description || 'No description available' }}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Price</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ formatCurrency(product.price) }}</dd>
            </div>
            <template v-if="product.type === 'inventory_item'">
              <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-500">Quantity on Hand</dt>
                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ product.quantity_on_hand || 0 }}</dd>
              </div>
              <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-500">Reorder Point</dt>
                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ product.reorder_point || 'Not set' }}</dd>
              </div>
              <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-500">Purchase Price</dt>
                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ formatCurrency(product.purchase_price) }}</dd>
              </div>
            </template>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Created At</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(product.created_at) }}
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(product.updated_at) }}
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
const product = ref(null)
const isLoading = ref(true)
const error = ref(null)

const getTypeClass = computed(() => {
  const baseClasses = 'px-2 py-1 text-xs font-medium rounded-full'
  if (product.value?.type === 'service') {
    return `${baseClasses} bg-purple-100 text-purple-800`
  }
  return `${baseClasses} bg-blue-100 text-blue-800`
})

const formatType = (type) => {
  switch (type) {
    case 'service':
      return 'Service'
    case 'inventory_item':
      return 'Inventory Item'
    default:
      return type
  }
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value || 0)
}

const fetchProduct = async () => {
  try {
    isLoading.value = true
    error.value = null
    const response = await fetch(`${config.public.apiBase}/api/ProdServ/get/${route.params.id}`)
    if (!response.ok) {
      throw new Error('Failed to fetch product data')
    }
    const data = await response.json()
    product.value = data
  } catch (err) {
    error.value = err.message
    console.error('Error fetching product:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchProduct()
})
</script>
