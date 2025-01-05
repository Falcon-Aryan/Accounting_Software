<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="md:flex md:items-center md:justify-between mb-6">
        <div class="flex-1 min-w-0">
          <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">Expenses</h2>
        </div>
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <button @click="showNewExpenseModal = true" class="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
            Add Expense
          </button>
        </div>
      </div>

      <!-- Search and Filter -->
      <div class="mb-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label for="search" class="sr-only">Search expenses</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
              </svg>
            </div>
            <input
              id="search"
              v-model="searchQuery"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="Search expenses"
              type="search"
            >
          </div>
        </div>
        <div>
          <select
            v-model="categoryFilter"
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
          >
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
        <div>
          <select
            v-model="vendorFilter"
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
          >
            <option value="">All Vendors</option>
            <option v-for="vendor in vendors" :key="vendor.id" :value="vendor.id">
              {{ vendor.name }}
            </option>
          </select>
        </div>
        <div>
          <select
            v-model="paymentMethodFilter"
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
          >
            <option value="">All Payment Methods</option>
            <option value="cash">Cash</option>
            <option value="credit_card">Credit Card</option>
            <option value="bank_transfer">Bank Transfer</option>
            <option value="check">Check</option>
          </select>
        </div>
      </div>

      <!-- Expenses Table -->
      <div class="flex flex-col">
        <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vendor
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Payment Method
                    </th>
                    <th scope="col" class="relative px-6 py-3">
                      <span class="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="expense in filteredExpenses" :key="expense.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatDate(expense.date) }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-sm text-gray-900">{{ expense.description }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ expense.category }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ getVendorName(expense.vendorId) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">${{ expense.amount.toFixed(2) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatPaymentMethod(expense.paymentMethod) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button @click="editExpense(expense)" class="text-green-600 hover:text-green-900 mr-4">Edit</button>
                      <button @click="deleteExpense(expense.id)" class="text-red-600 hover:text-red-900">Delete</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New/Edit Expense Modal -->
    <div v-if="showNewExpenseModal" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <form @submit.prevent="saveExpense">
            <div>
              <h3 class="text-lg leading-6 font-medium text-gray-900">{{ editingExpense ? 'Edit' : 'New' }} Expense</h3>
              <div class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div class="sm:col-span-3">
                  <label for="date" class="block text-sm font-medium text-gray-700">Date</label>
                  <div class="mt-1">
                    <input type="date" v-model="expenseForm.date" id="date" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-3">
                  <label for="amount" class="block text-sm font-medium text-gray-700">Amount</label>
                  <div class="mt-1">
                    <input type="number" step="0.01" v-model="expenseForm.amount" id="amount" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-6">
                  <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
                  <div class="mt-1">
                    <input type="text" v-model="expenseForm.description" id="description" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-3">
                  <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
                  <div class="mt-1">
                    <select
                      id="category"
                      v-model="expenseForm.category"
                      required
                      class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    >
                      <option value="">Select Category</option>
                      <option v-for="category in categories" :key="category" :value="category">
                        {{ category }}
                      </option>
                    </select>
                  </div>
                </div>

                <div class="sm:col-span-3">
                  <label for="vendor" class="block text-sm font-medium text-gray-700">Vendor</label>
                  <div class="mt-1">
                    <select
                      id="vendor"
                      v-model="expenseForm.vendorId"
                      required
                      class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    >
                      <option value="">Select Vendor</option>
                      <option v-for="vendor in vendors" :key="vendor.id" :value="vendor.id">
                        {{ vendor.name }}
                      </option>
                    </select>
                  </div>
                </div>

                <div class="sm:col-span-6">
                  <label for="paymentMethod" class="block text-sm font-medium text-gray-700">Payment Method</label>
                  <div class="mt-1">
                    <select
                      id="paymentMethod"
                      v-model="expenseForm.paymentMethod"
                      required
                      class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    >
                      <option value="">Select Payment Method</option>
                      <option value="cash">Cash</option>
                      <option value="credit_card">Credit Card</option>
                      <option value="bank_transfer">Bank Transfer</option>
                      <option value="check">Check</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
              <button type="submit" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:col-start-2 sm:text-sm">
                {{ editingExpense ? 'Save Changes' : 'Create Expense' }}
              </button>
              <button @click="showNewExpenseModal = false" type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:mt-0 sm:col-start-1 sm:text-sm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: ['auth']
})

import { ref, computed } from 'vue'
import { useRuntimeConfig } from '#imports'

const config = useRuntimeConfig()

// State
const expenses = ref([])
const vendors = ref([])
const searchQuery = ref('')
const categoryFilter = ref('')
const vendorFilter = ref('')
const paymentMethodFilter = ref('')
const showNewExpenseModal = ref(false)
const editingExpense = ref(null)

const categories = [
  'Office Supplies',
  'Utilities',
  'Rent',
  'Travel',
  'Meals',
  'Equipment',
  'Software',
  'Marketing',
  'Insurance',
  'Professional Services',
  'Maintenance',
  'Other'
]

const expenseForm = ref({
  date: '',
  description: '',
  category: '',
  vendorId: '',
  amount: '',
  paymentMethod: ''
})

// Computed
const filteredExpenses = computed(() => {
  let filtered = expenses.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(expense => 
      expense.description.toLowerCase().includes(query) ||
      getVendorName(expense.vendorId).toLowerCase().includes(query)
    )
  }

  // Apply category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(expense => expense.category === categoryFilter.value)
  }

  // Apply vendor filter
  if (vendorFilter.value) {
    filtered = filtered.filter(expense => expense.vendorId === vendorFilter.value)
  }

  // Apply payment method filter
  if (paymentMethodFilter.value) {
    filtered = filtered.filter(expense => expense.paymentMethod === paymentMethodFilter.value)
  }

  return filtered
})

// Methods
const fetchExpenses = async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/expenses`)
    if (!response.ok) throw new Error('Failed to fetch expenses')
    expenses.value = await response.json()
  } catch (error) {
    console.error('Error fetching expenses:', error)
  }
}

const fetchVendors = async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/vendors`)
    if (!response.ok) throw new Error('Failed to fetch vendors')
    vendors.value = await response.json()
  } catch (error) {
    console.error('Error fetching vendors:', error)
  }
}

const saveExpense = async () => {
  try {
    const url = `${config.public.apiBase}/api/expenses${editingExpense.value ? `/${editingExpense.value.id}` : ''}`
    const method = editingExpense.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(expenseForm.value),
    })

    if (!response.ok) throw new Error('Failed to save expense')
    
    await fetchExpenses()
    showNewExpenseModal.value = false
    resetForm()
  } catch (error) {
    console.error('Error saving expense:', error)
  }
}

const editExpense = (expense) => {
  editingExpense.value = expense
  expenseForm.value = { ...expense }
  showNewExpenseModal.value = true
}

const deleteExpense = async (id) => {
  if (!confirm('Are you sure you want to delete this expense?')) return
  
  try {
    const response = await fetch(`${config.public.apiBase}/api/expenses/${id}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) throw new Error('Failed to delete expense')
    
    await fetchExpenses()
  } catch (error) {
    console.error('Error deleting expense:', error)
  }
}

const resetForm = () => {
  editingExpense.value = null
  expenseForm.value = {
    date: '',
    description: '',
    category: '',
    vendorId: '',
    amount: '',
    paymentMethod: ''
  }
}

const getVendorName = (vendorId) => {
  const vendor = vendors.value.find(v => v.id === vendorId)
  return vendor ? vendor.name : 'Unknown Vendor'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const formatPaymentMethod = (method) => {
  return method.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

// Initial fetch
fetchExpenses()
fetchVendors()
</script>
