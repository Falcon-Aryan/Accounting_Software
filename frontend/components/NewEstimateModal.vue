<template>
  <BaseNewFormModal
    :is-open="isOpen"
    title="Create New Estimate"
    width="lg"
    @close="close"
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

      <!-- Expiry Date -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Expiry Date</label>
        <input
          v-model="form.expiry_date"
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

      <!-- Line Items Table -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Line Items</label>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(item, index) in form.line_items" :key="index">
                <td class="px-4 py-4">
                  <select
                    v-model="item.product_id"
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
                    v-model="item.description"
                    type="text"
                    class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                  />
                </td>
                <td class="px-4 py-4">
                  <input
                    v-model.number="item.unit_price"
                    type="number"
                    required
                    step="0.01"
                    class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                  />
                </td>
                <td class="px-4 py-4">
                  <input
                    v-model.number="item.quantity"
                    type="number"
                    required
                    min="1"
                    class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                  />
                </td>
                <td class="px-4 py-4 text-sm text-gray-900">
                  {{ formatCurrency(item.unit_price * item.quantity) }}
                </td>
                <td class="px-4 py-4">
                  <button
                    @click.prevent="removeItem(index)"
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
            @click.prevent="addItem"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
          >
            Add Line Item
          </button>
          
          <div class="text-right">
            <span class="text-sm font-medium text-gray-700">Total: </span>
            <span class="text-lg font-semibold">{{ formatCurrency(calculateTotal) }}</span>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Notes</label>
        <textarea
          v-model="form.notes"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
          placeholder="Add any notes about this estimate..."
        />
      </div>

      <!-- Terms & Conditions -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Terms & Conditions</label>
        <textarea
          v-model="form.terms_conditions"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
          placeholder="Add terms and conditions..."
        />
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
  </BaseNewFormModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseNewFormModal from '~/components/BaseNewFormModal.vue'
import { useRouter } from 'vue-router'
import { useRuntimeConfig } from '#app'

const router = useRouter()
const config = useRuntimeConfig()

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'save'])

const customers = ref([])
const products = ref([])
const form = ref({
  customer_name: '',
  estimate_date: new Date().toISOString().split('T')[0],
  expiry_date: new Date(Date.now() + 30*24*60*60*1000).toISOString().split('T')[0], // 30 days from now
  status: 'draft',
  line_items: [],
  notes: '',
  terms_conditions: ''
})

async function fetchCustomers() {
  try {
    const response = await fetch(`${config.public.apiBase}/api/customers/list_customers`)
    if (!response.ok) throw new Error('Failed to fetch customers')
    const data = await response.json()
    customers.value = data.customers
  } catch (error) {
    console.error('Error fetching customers:', error)
  }
}

async function fetchProducts() {
  try {
    const response = await fetch(`${config.public.apiBase}/api/products/list_products`)
    if (!response.ok) throw new Error('Failed to fetch products')
    const data = await response.json()
    products.value = data.products
  } catch (error) {
    console.error('Error fetching products:', error)
  }
}

// Fetch data on component mount
fetchCustomers()
fetchProducts()

function navigateToCustomers() {
  router.push('/customers?action=new')
}

function navigateToProducts() {
  router.push('/prodServ?action=new')
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount || 0)
}

const calculateTotal = computed(() => {
  return form.value.line_items.reduce((sum, item) => sum + (Number(item.unit_price) * Number(item.quantity) || 0), 0)
})

function addItem() {
  form.value.line_items.push({
    product_id: '',
    description: '',
    unit_price: 0,
    quantity: 1
  })
}

function removeItem(index) {
  form.value.line_items.splice(index, 1)
}

function handleProductSelect(index, selectedProductId) {
  if (selectedProductId === 'new_product') {
    navigateToProducts()
    return
  }

  const product = products.value.find(p => p.id === selectedProductId)
  if (product) {
    form.value.line_items[index] = {
      ...form.value.line_items[index],
      product_id: product.id,
      description: product.description || '',
      unit_price: product.unit_price
    }
  }
}

function close() {
  resetForm()
  emit('close')
}

function resetForm() {
  form.value = {
    customer_name: '',
    estimate_date: new Date().toISOString().split('T')[0],
    expiry_date: new Date(Date.now() + 30*24*60*60*1000).toISOString().split('T')[0],
    status: 'draft',
    line_items: [],
    notes: '',
    terms_conditions: ''
  }
}

async function handleSubmit() {
  try {
    if (form.value.customer_name === 'new_customer') {
      navigateToCustomers()
      return
    }

    const customer = customers.value.find(c => 
      `${c.first_name} ${c.last_name}` === form.value.customer_name
    )

    const estimateData = {
      customer_name: form.value.customer_name,
      customer_id: customer?.id,
      estimate_date: form.value.estimate_date,
      expiry_date: form.value.expiry_date,
      status: form.value.status,
      line_items: form.value.line_items.map(item => ({
        product_id: item.product_id,
        description: item.description || '',
        unit_price: Number(item.unit_price),
        quantity: Number(item.quantity)
      })),
      notes: form.value.notes,
      terms_conditions: form.value.terms_conditions,
      total_amount: calculateTotal.value
    }

    emit('save', estimateData)
    close()
  } catch (error) {
    console.error('Error creating estimate:', error)
  }
}
</script>
