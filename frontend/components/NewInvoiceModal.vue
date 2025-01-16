<template>
  <BaseNewFormModal
    :is-open="isOpen"
    title="Create New Invoice"
    width="md"
    @close="close"
    @save="handleSubmit"
  >
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
          You'll be redirected to add a new customer. Your invoice draft will be discarded.
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
        <label class="block text-sm font-medium text-gray-700 mb-2">Invoice Date</label>
        <input
          v-model="form.date"
          type="date"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        />
      </div>

      <!-- Payment Terms -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Payment Terms</label>
        <select
          v-model="form.payment_terms"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        >
          <option value="due_on_receipt">Due on Receipt</option>
          <option value="net_15">Net 15</option>
          <option value="net_30">Net 30</option>
          <option value="net_60">Net 60</option>
          <option value="custom">Custom</option>
        </select>
      </div>

      <!-- Due Date -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
        <input
          v-model="form.due_date"
          type="date"
          required
          :disabled="form.payment_terms !== 'custom'"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        />
      </div>

      <!-- Status -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
        <select
          v-model="form.status"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        >
          <option value="Select status" disabled>Select status</option>
          <option value="draft">Draft</option>
          <option value="sent">Sent</option>
          <option value="paid">Paid</option>
          <option value="partial">Partially Paid</option>
          <option value="overdue">Overdue</option>
          <option value="void">Void</option>
        </select>
      </div>

      <!-- Add Notes Section -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700">Notes</label>
        <textarea
          v-model="form.notes"
          rows="3"
          class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
          placeholder="Add any notes for this invoice..."
        ></textarea>
      </div>

      <!-- Line Items Table -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Line Items</label>
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
                      class="text-sm"
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
                    v-model.number="product.unit_price"
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
                  {{ formatCurrency(product.unit_price * product.quantity) }}
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
      <div class="mt-6 flex justify-end space-x-3">
        <button
          type="button"
          @click="close"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? 'Creating...' : 'Create Invoice' }}
        </button>
      </div>
    </form>
  </BaseNewFormModal>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useRuntimeConfig } from '#app'
import { getAuth } from 'firebase/auth'
import BaseNewFormModal from '~/components/BaseNewFormModal.vue'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'save'])
const router = useRouter()
const config = useRuntimeConfig()
const auth = getAuth()

const isSubmitting = ref(false)
const errorMessage = ref('')

// Reactive state
const customers = ref([])
const products = ref([])
const form = ref({
  customer_name: '',
  date: new Date().toISOString().split('T')[0],
  due_date: new Date().toISOString().split('T')[0],
  payment_terms: 'due_on_receipt',
  status: 'draft',
  notes: '',
  line_items: [{
    id: '',
    description: '',
    unit_price: '',
    quantity: 1
  }]
})

// Get current user's ID token
async function getIdToken() {
  const user = auth.currentUser
  if (!user) {
    throw new Error('No authenticated user')
  }
  return user.getIdToken()
}

// Fetch customers
async function fetchCustomers() {
  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/customers/list_customers`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to fetch customers')
    }

    const data = await response.json()
    if (data.customers) {
      customers.value = data.customers
    }
  } catch (error) {
    if (error.message === 'No authenticated user') {
      console.error('Please log in to fetch customers')
    } else {
      console.error('Error fetching customers:', error)
    }
  }
}

// Fetch products
async function fetchProducts() {
  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/ProdServ/list`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to fetch products')
    }

    const data = await response.json()
    if (data.products) {
      products.value = data.products
    }
  } catch (error) {
    handleError(error)
  }
}

onMounted(() => {
  fetchCustomers()
  fetchProducts()
})

function navigateToCustomers() {
  close()
  router.push('/customers?action=new')
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const calculateTotal = computed(() => {
  return form.value.line_items.reduce((sum, item) => 
    sum + (Number(item.unit_price) * Number(item.quantity) || 0), 0)
})

function addProduct() {
  form.value.line_items.push({
    id: '',
    description: '',
    unit_price: 0,
    quantity: 1
  })
}

function removeProduct(index) {
  form.value.line_items.splice(index, 1)
}

function handleProductSelect(index, productId) {
  if (productId === 'new_product') {
    router.push('/prodServ?action=new')
    return
  }

  const selectedProduct = products.value.find(p => p.id === productId)
  if (selectedProduct) {
    form.value.line_items[index] = {
      id: selectedProduct.id,
      description: selectedProduct.description || '',
      unit_price: selectedProduct.unit_price,
      quantity: form.value.line_items[index]?.quantity || 1
    }
  }
}

const updateDueDate = (terms) => {
  const invoiceDate = new Date(form.value.date)
  let dueDate = new Date(invoiceDate)

  switch (terms) {
    case 'net_15':
      dueDate.setDate(invoiceDate.getDate() + 15)
      break
    case 'net_30':
      dueDate.setDate(invoiceDate.getDate() + 30)
      break
    case 'net_60':
      dueDate.setDate(invoiceDate.getDate() + 60)
      break
    default: // due_on_receipt or custom
      dueDate = invoiceDate
      break
  }
  
  form.value.due_date = dueDate.toISOString().split('T')[0]
}

watch(() => form.value.payment_terms, (newTerms) => {
  updateDueDate(newTerms)
})

watch(() => form.value.date, (newDate) => {
  updateDueDate(form.value.payment_terms)
})

async function handleSubmit() {
  try {
    if (form.value.customer_name === 'new_customer') {
      navigateToCustomers()
      return
    }

    isSubmitting.value = true
    const customer = customers.value.find(c => 
      `${c.first_name} ${c.last_name}` === form.value.customer_name
    )

    if (!customer?.id) {
      throw new Error('Please select a valid customer')
    }

    const invoiceData = {
      customer_id: customer.id,
      customer_name: form.value.customer_name,
      date: form.value.date,
      due_date: form.value.due_date,
      payment_terms: form.value.payment_terms,
      status: form.value.status,
      line_items: form.value.line_items.map(p => ({
        product_id: p.id,
        description: p.description || '',
        unit_price: Number(p.unit_price),
        quantity: Number(p.quantity),
        total: Number(p.unit_price) * Number(p.quantity)
      })),
      total: calculateTotal.value,
      balance_due: calculateTotal.value,
      notes: form.value.notes,
    }
  emit('save', invoiceData)
  close()
  } catch (error) {
    handleError(error)
  } finally {
    isSubmitting.value = false
  }
}

function close() {
  form.value = {
    customer_name: '',
    date: new Date().toISOString().split('T')[0],
    due_date: new Date().toISOString().split('T')[0],
    payment_terms: 'due_on_receipt',
    status: 'draft',
    notes: '',
    line_items: [{
      id: '',
      description: '',
      unit_price: '',
      quantity: 1
    }]
  }
  emit('close')
}


function handleError(error) {
  console.error('Operation failed:', error)
  if (error.message === 'No authenticated user') {
    errorMessage.value = 'Please log in to continue'
  } else {
    errorMessage.value = error.message || 'An error occurred'
  }
}

// Watch for product changes to update the form
watch(() => products.value, (newProducts) => {
  if (newProducts.length > 0) {
    form.value.line_items.forEach((product, index) => {
      if (product.id) {
        const matchingProduct = newProducts.find(p => p.id === product.id)
        if (matchingProduct) {
          form.value.line_items[index] = {
            ...form.value.line_items[index],
            name: matchingProduct.name,
            description: matchingProduct.description,
            unit_price: matchingProduct.unit_price
          }
        }
      }
    })
  }
}, { deep: true })
</script>