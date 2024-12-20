<template>
  <div v-if="isOpen" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-[800px] shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Create New Estimate</h3>
        <form @submit.prevent="handleSubmit">
          <!-- Customer Selection -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Customer</label>
            <select
              v-model="form.customer_name"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            >
              <option value="" disabled>Select a customer</option>
              <option value="new_customer" class="font-medium text-green-600">+ Add New Customer</option>
              <option 
                v-for="customer in customers" 
                :key="customer.id"
                :value="customer.first_name + ' ' + customer.last_name"
              >
                {{ customer.first_name }} {{ customer.last_name }}
              </option>
            </select>
          </div>
          
          <!-- New Customer Navigation -->
          <div v-if="form.customer_name === 'new_customer'" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
            <p class="text-sm text-green-700">
              You'll be redirected to add a new customer. Your estimate draft will be discarded.
            </p>
            <button
              type="button"
              @click="navigateToCustomers"
              class="mt-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Continue to Add Customer
            </button>
          </div>

          <!-- Estimate Date -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Estimate Date</label>
            <input
              v-model="form.estimate_date"
              type="date"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            />
          </div>

          <!-- Status -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              v-model="form.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            >
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="accepted">Accepted</option>
              <option value="declined">Declined</option>
            </select>
          </div>

          <!-- Products Table -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Products</label>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(product, index) in form.products" :key="index">
                    <td class="px-6 py-4">
                      <input
                        v-model="product.name"
                        type="text"
                        required
                        class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </td>
                    <td class="px-6 py-4">
                      <input
                        v-model="product.description"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </td>
                    <td class="px-6 py-4">
                      <input
                        v-model.number="product.price"
                        type="number"
                        required
                        step="0.01"
                        class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </td>
                    <td class="px-6 py-4">
                      <button
                        @click.prevent="removeProduct(index)"
                        type="button"
                        class="text-red-600 hover:text-red-900"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="mt-3 flex justify-between items-center">
              <button
                type="button"
                @click.prevent="addProduct"
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
              >
                Add Product
              </button>
              
              <div class="text-right">
                <span class="text-sm font-medium text-gray-700">Total: </span>
                <span class="text-lg font-semibold">{{ formatCurrency(calculateTotal) }}</span>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              @click="close"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Create Estimate
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRuntimeConfig } from '#app'

const router = useRouter()
const config = useRuntimeConfig()

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'save'])

const customers = ref([])
const form = ref({
  customer_name: '',
  estimate_date: new Date().toISOString().split('T')[0],
  status: 'draft',
  products: []
})


const fetchCustomers = async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/customers/list_customers`)
    const data = await response.json()
    if (response.ok && data.customers) {
      customers.value = data.customers
    }
  } catch (error) {
    console.error('Error fetching customers:', error)
  }
}


onMounted(() => {
  fetchCustomers()
})

const navigateToCustomers = () => {
  close()
  router.push('/customers')
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const calculateTotal = computed(() => {
  return form.value.products.reduce((sum, product) => sum + (Number(product.price) || 0), 0)
})

const addProduct = () => {
  form.value.products.push({
    name: '',
    description: '',
    price: 0
  })
}

const removeProduct = (index) => {
  form.value.products.splice(index, 1)
}

const close = () => {
  resetForm()
  emit('close')
}

const resetForm = () => {
  form.value = {
    customer_name: '',
    estimate_date: new Date().toISOString().split('T')[0],
    status: 'draft',
    products: []
  }
}

const handleSubmit = () => {
  if (form.value.customer_name === 'new_customer') {
    navigateToCustomers()
    return
  }
  
  emit('save', {
    ...form.value,
    products: form.value.products.map(p => ({
      ...p,
      price: Number(p.price)
    }))
  })
}
</script>
