<!-- frontend/components/EditEstimateModal.vue -->
<template>
  <div v-if="props.estimate" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-[1000px] shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex justify-between items-center p-4 border-b">
        <h2 class="text-xl font-semibold">Edit Estimate</h2>
        <button @click="close" class="text-gray-500 hover:text-gray-700">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <form @submit.prevent="handleSubmit">
          <!-- Error Message -->
          <div v-if="errorMessage" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {{ errorMessage }}
          </div>

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
              You'll be redirected to add a new customer. Your estimate changes will be discarded.
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
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Estimate Date*
            </label>
            <input
              v-model="form.estimate_date"
              type="date"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            />
          </div>

          <!-- Status -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Status*
            </label>
            <select
              v-model="form.status"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            >
              <option value="">Select status</option>
              <option v-for="status in statusTypes" :key="status" :value="status">
                {{ status }}
              </option>
            </select>
          </div>

          <!-- Products Table -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Products</label>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(product, index) in form.products" :key="index">
                    <td class="px-4 py-4">
                      <select
                        v-model="product.id"
                        @change="handleProductSelect(index, $event.target.value)"
                        required
                        class="w-48 px-3 py-1.5 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      >
                        <option value="" disabled>Select a product</option>
                        <option value="new_product" class="font-medium text-green-600">+ Add New Product</option>
                        <option 
                          v-for="prod in products" 
                          :key="prod.id"
                          :value="prod.id"
                          :selected="prod.id === product.id"
                        >
                          {{ prod.name }}
                        </option>
                      </select>
                    </td>
                    <td class="px-4 py-4">
                      <input
                        v-model="product.description"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </td>
                    <td class="px-4 py-4">
                      <input
                        v-model.number="product.price"
                        type="number"
                        required
                        step="0.01"
                        class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </td>
                    <td class="px-4 py-4">
                      <input
                        v-model.number="product.quantity"
                        type="number"
                        required
                        min="1"
                        class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </td>
                    <td class="px-4 py-4 text-sm text-gray-900">
                      {{ formatCurrency(product.price * product.quantity) }}
                    </td>
                    <td class="px-4 py-4">
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
                @click="addProduct"
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
          <div class="mt-6 flex justify-between">
            <!-- Delete Button -->
            <button
              type="button"
              @click="confirmDelete"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              :disabled="isSubmitting"
            >
              Delete Estimate
            </button>

            <div class="flex space-x-3">
              <!-- Cancel Button -->
              <button
                type="button"
                @click="close"
                class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                :disabled="isSubmitting"
              >
                Cancel
              </button>

              <!-- Save Button -->
              <button
                type="submit"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                :disabled="isSubmitting"
              >
                Save Changes
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRuntimeConfig } from '#app'
import { useRouter } from 'vue-router'

const router = useRouter()
const customers = ref([])
const products = ref([])

const config = useRuntimeConfig()
const props = defineProps({
  estimate: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'update'])

const errorMessage = ref('')
const isSubmitting = ref(false)
const statusTypes = ['Draft', 'Sent', 'Accepted', 'Rejected']

const form = ref({
  customer_name: '',
  estimate_date: '',
  status: '',
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

const fetchProducts = async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/ProdServ/list`)
    const data = await response.json()
    if (response.ok && data.products) {
      products.value = data.products
    }
  } catch (error) {
    console.error('Error fetching products:', error)
  }
}

const navigateToCustomers = () => {
  close()
  router.push('/customers')
}

const navigateToProducts = () => {
  close()
  router.push('/prodServ')
}

onMounted(() => {
  fetchCustomers()
  fetchProducts()
})

watch(() => props.estimate, async (newEstimate) => {
  if (newEstimate) {
    // First fetch products to ensure we have the list
    await fetchProducts()
    
    form.value = {
      customer_name: newEstimate.customer_name,
      estimate_date: newEstimate.estimate_date,
      status: newEstimate.status,
      products: newEstimate.products.map(product => {
        // Find the matching product from our products list
        const matchingProduct = products.value.find(p => p.name === product.name)
        return {
          id: matchingProduct?.id || '',
          name: product.name,
          description: product.description || '',
          price: product.price || 0,
          quantity: product.quantity || 1,
          type: product.type || '',
          sell_enabled: product.sell_enabled || false,
          purchase_enabled: product.purchase_enabled || false,
          income_account_id: product.income_account_id || '',
          expense_account_id: product.expense_account_id || ''
        }
      })
    }
  }
}, { immediate: true })

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const calculateTotal = computed(() => {
  return form.value.products.reduce((sum, product) => sum + (Number(product.price) * Number(product.quantity) || 0), 0)
})

const addProduct = () => {
  form.value.products.push({
    id: '',
    name: '',
    description: '',
    price: 0,
    quantity: 1,
    type: '',
    sell_enabled: false,
    purchase_enabled: false,
    income_account_id: '',
    expense_account_id: ''
  })
}

const removeProduct = (index) => {
  form.value.products.splice(index, 1)
}

const close = () => {
  emit('close')
  errorMessage.value = ''
  form.value = {
    customer_name: '',
    estimate_date: '',
    status: ''
  }
}

async function handleSubmit() {
  try {
    isSubmitting.value = true
    errorMessage.value = ''

    const customer = customers.value.find(c => 
      `${c.first_name} ${c.last_name}` === form.value.customer_name
    )

    const updatedData = {
      id: props.estimate.id,
      customer_id: customer?.id,
      customer_name: form.value.customer_name,
      estimate_date: form.value.estimate_date,
      status: form.value.status,
      products: form.value.products.map(p => ({
        id: p.id,
        name: p.name,
        description: p.description,
        price: Number(p.price),
        quantity: Number(p.quantity),
        type: p.type,
        sell_enabled: p.sell_enabled,
        purchase_enabled: p.purchase_enabled,
        income_account_id: p.income_account_id,
        expense_account_id: p.expense_account_id
      })),
      total_amount: calculateTotal.value
    }

    emit('update', updatedData)
    close()
  } catch (error) {
    console.error('Error updating estimate:', error)
    errorMessage.value = 'Failed to update estimate. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

async function confirmDelete() {
  if (!confirm('Are you sure you want to delete this estimate? This action cannot be undone.')) return

  try {
    isSubmitting.value = true
    const response = await fetch(`${config.public.apiBase}/api/estimates/delete_estimate/${props.estimate.id}`, {
      method: 'DELETE'
    })

    if (!response.ok) throw new Error('Failed to delete estimate')

    emit('update', null)
    close()
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error deleting estimate:', error)
  } finally {
    isSubmitting.value = false
  }
}

function handleProductSelect(index, productId) {
  if (productId === 'new_product') {
    navigateToProducts()
    return
  }

  const selectedProduct = products.value.find(p => p.id === productId)
  if (selectedProduct) {
    const currentQuantity = form.value.products[index].quantity || 1
    form.value.products[index] = {
      id: selectedProduct.id,
      name: selectedProduct.name,
      description: selectedProduct.description || '',
      price: selectedProduct.unit_price,
      quantity: currentQuantity,
      type: selectedProduct.type,
      sell_enabled: selectedProduct.sell_enabled,
      purchase_enabled: selectedProduct.purchase_enabled,
      income_account_id: selectedProduct.income_account_id,
      expense_account_id: selectedProduct.expense_account_id
    }
  }
}
</script>
