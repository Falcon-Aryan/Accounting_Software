<template>
  <div v-if="props.invoice" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
    <div class="bg-white rounded-lg w-full max-w-2xl">
      <!-- Modal Header -->
      <div class="flex justify-between items-center p-4 border-b">
        <h2 class="text-xl font-semibold">Edit Invoice</h2>
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
              You'll be redirected to add a new customer. Your invoice changes will be discarded.
            </p>
            <button
              type="button"
              @click="navigateToCustomers"
              class="mt-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Continue to Add Customer
            </button>
          </div>

          <!-- Invoice Date -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Invoice Date*
            </label>
            <input
              v-model="form.invoice_date"
              type="date"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            />
          </div>

          <!-- Due Date -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Due Date*
            </label>
            <input
              v-model="form.due_date"
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
                        v-model="product.price"
                        type="number"
                        required
                        step="0.01"
                        min="0"
                        class="w-32 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </td>
                    <td class="px-6 py-4">
                      <button
                        @click="removeProduct(index)"
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
              Delete Invoice
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
import { ref, watch, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRuntimeConfig } from '#app'

const router = useRouter()
const config = useRuntimeConfig()

const props = defineProps({
  invoice: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'update'])

const errorMessage = ref('')
const isSubmitting = ref(false)
const statusTypes = ['draft', 'posted', 'paid', 'overdue', 'void']
const customers = ref([])

const form = ref({
  customer_name: props.invoice?.customer_name || '',
  invoice_date: props.invoice?.invoice_date || '',
  due_date: props.invoice?.due_date || '',
  products: props.invoice?.products.map(p => ({
    name: p.name,
    description: p.description,
    price: p.price
  })),
  status: props.invoice?.status || ''
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
    errorMessage.value = 'Failed to load customers. Please try again.'
  }
}

onMounted(() => {
  fetchCustomers()
})

const navigateToCustomers = () => {
  close()
  router.push('/customers')
}

// Watch for changes in the invoice prop
watch(() => props.invoice, (newInvoice) => {
  if (newInvoice) {
    form.value = {
      customer_name: newInvoice.customer_name,
      invoice_date: newInvoice.invoice_date,
      due_date: newInvoice.due_date,
      products: newInvoice.products.map(p => ({
        name: p.name,
        description: p.description,
        price: p.price
      })),
      status: newInvoice.status
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
  if (!form.value.products) return 0
  return form.value.products.reduce((sum, product) => {
    const price = parseFloat(product.price) || 0
    return sum + price
  }, 0)
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
  form.value = {
    customer_name: '',
    invoice_date: '',
    due_date: '',
    products: [],
    status: ''
  }
  errorMessage.value = ''
  emit('close')
}

async function handleSubmit() {
  if (form.value.customer_name === 'new_customer') {
    navigateToCustomers()
    return
  }

  try {
    isSubmitting.value = true
    const response = await fetch(`${config.public.apiBase}/api/invoices/update_invoice/${props.invoice.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        customer_name: form.value.customer_name,
        invoice_date: form.value.invoice_date,
        due_date: form.value.due_date,
        status: form.value.status,
        products: form.value.products
      })
    })

    if (!response.ok) throw new Error('Failed to update invoice')

    const updatedInvoice = await response.json()
    emit('update', updatedInvoice)
    close()
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error updating invoice:', error)
  } finally {
    isSubmitting.value = false
  }
}

async function confirmDelete() {
  if (confirm('Are you sure you want to delete this invoice?')) {
    try {
      const response = await fetch(`${config.public.apiBase}/api/invoices/delete_invoice/${props.invoice.id}`, {
        method: 'DELETE'
      })

      if (!response.ok) throw new Error('Failed to delete invoice')

      emit('update')
      close()
    } catch (error) {
      errorMessage.value = error.message
      console.error('Error deleting invoice:', error)
    }
  }
}
</script>
