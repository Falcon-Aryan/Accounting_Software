<template>
  <BaseEditFormModal
    :is-open="props.isOpen"
    title="Edit Estimate"
    width="lg"
    @close="close"
  >
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
        <label class="block text-sm font-medium text-gray-700 mb-1">Estimate Date*</label>
        <input
          v-model="form.estimate_date"
          type="date"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        />
      </div>

      <!-- Expiry Date -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Expiry Date*</label>
        <input
          v-model="form.expiry_date"
          type="date"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        />
      </div>

      <!-- Status -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Status*</label>
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
              <tr v-for="(product, index) in form.line_items" :key="index">
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
            {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
        </button>
        </div>
      </div>
    </form>
  </BaseEditFormModal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRuntimeConfig } from '#app'
import BaseEditFormModal from '~/components/BaseEditFormModal.vue'

const config = useRuntimeConfig()

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
    default: false
  },
  estimate: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'update'])

const customers = ref([])
const products = ref([])

const errorMessage = ref('')
const isSubmitting = ref(false)
const statusTypes = ['Draft', 'Sent', 'Accepted', 'Rejected']

const form = ref({
  customer_name: '',
  estimate_date: '',
  expiry_date: '',
  status: '',
  line_items: [],
  notes: '',
  terms_conditions: ''
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
      expiry_date: newEstimate.expiry_date,
      status: newEstimate.status,
      line_items: newEstimate.line_items.map(product => {
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
      }),
      notes: newEstimate.notes,
      terms_conditions: newEstimate.terms_conditions
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
  return form.value.line_items.reduce((sum, product) => sum + (Number(product.price) * Number(product.quantity) || 0), 0)
})

const addProduct = () => {
  form.value.line_items.push({
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
  form.value.line_items.splice(index, 1)
}

const close = () => {
  emit('close')
  errorMessage.value = ''
  form.value = {
    customer_name: '',
    estimate_date: '',
    expiry_date: '',
    status: ''
  }
}

async function handleSubmit() {
  try {
    isSubmitting.value = true
    errorMessage.value = ''

    // Prepare the invoice data
    const invoiceData = {
      customer_name: form.value.customer_name,
      invoice_date: form.value.invoice_date,
      due_date: form.value.due_date,
      payment_terms: form.value.payment_terms,
      status: form.value.status,
      line_items: form.value.line_items.map(item => ({
        product_id: item.id,
        description: item.description,
        quantity: Number(item.quantity),
        unit_price: Number(item.price)
      }))
    }

    // Make API call to update invoice
    const response = await fetch(`${config.public.apiBase}/api/invoices/update_invoice/${props.invoice.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getIdToken()}`
      },
      body: JSON.stringify(invoiceData)
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.error || 'Failed to update invoice')
    }

    // Close modal and emit event
    emit('invoice-updated')
    close()
  } catch (error) {
    console.error('Error updating invoice:', error)
    errorMessage.value = error.message || 'Failed to update invoice. Please try again.'
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
    const currentQuantity = form.value.line_items[index].quantity || 1
    form.value.line_items[index] = {
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
