<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="md:flex md:items-center md:justify-between mb-6">
        <div class="flex-1 min-w-0">
          <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">Bills</h2>
        </div>
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <button @click="showNewBillModal = true" class="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
            Add Bill
          </button>
        </div>
      </div>

      <!-- Search and Filter -->
      <div class="mb-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label for="search" class="sr-only">Search bills</label>
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
              placeholder="Search bills"
              type="search"
            >
          </div>
        </div>
        <div>
          <select
            v-model="statusFilter"
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
          >
            <option value="">All Statuses</option>
            <option value="paid">Paid</option>
            <option value="unpaid">Unpaid</option>
            <option value="overdue">Overdue</option>
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
            v-model="dueDateFilter"
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
          >
            <option value="">All Due Dates</option>
            <option value="overdue">Overdue</option>
            <option value="due_today">Due Today</option>
            <option value="due_this_week">Due This Week</option>
            <option value="due_this_month">Due This Month</option>
          </select>
        </div>
      </div>

      <!-- Bills Table -->
      <div class="flex flex-col">
        <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Bill Number
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vendor
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" class="relative px-6 py-3">
                      <span class="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="bill in filteredBills" :key="bill.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ bill.billNumber }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ getVendorName(bill.vendorId) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ formatDate(bill.dueDate) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">${{ bill.amount.toFixed(2) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span :class="{
                        'px-2 inline-flex text-xs leading-5 font-semibold rounded-full': true,
                        'bg-green-100 text-green-800': bill.status === 'paid',
                        'bg-yellow-100 text-yellow-800': bill.status === 'unpaid',
                        'bg-red-100 text-red-800': bill.status === 'overdue'
                      }">
                        {{ formatStatus(bill.status) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button @click="editBill(bill)" class="text-green-600 hover:text-green-900 mr-4">Edit</button>
                      <button @click="deleteBill(bill.id)" class="text-red-600 hover:text-red-900">Delete</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New/Edit Bill Modal -->
    <div v-if="showNewBillModal" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <form @submit.prevent="saveBill">
            <div>
              <h3 class="text-lg leading-6 font-medium text-gray-900">{{ editingBill ? 'Edit' : 'New' }} Bill</h3>
              <div class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div class="sm:col-span-3">
                  <label for="billNumber" class="block text-sm font-medium text-gray-700">Bill Number</label>
                  <div class="mt-1">
                    <input type="text" v-model="billForm.billNumber" id="billNumber" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-3">
                  <label for="amount" class="block text-sm font-medium text-gray-700">Amount</label>
                  <div class="mt-1">
                    <input type="number" step="0.01" v-model="billForm.amount" id="amount" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-3">
                  <label for="dueDate" class="block text-sm font-medium text-gray-700">Due Date</label>
                  <div class="mt-1">
                    <input type="date" v-model="billForm.dueDate" id="dueDate" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-3">
                  <label for="vendor" class="block text-sm font-medium text-gray-700">Vendor</label>
                  <div class="mt-1">
                    <select
                      id="vendor"
                      v-model="billForm.vendorId"
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
                  <label for="status" class="block text-sm font-medium text-gray-700">Status</label>
                  <div class="mt-1">
                    <select
                      id="status"
                      v-model="billForm.status"
                      required
                      class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    >
                      <option value="">Select Status</option>
                      <option value="paid">Paid</option>
                      <option value="unpaid">Unpaid</option>
                      <option value="overdue">Overdue</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
              <button type="submit" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:col-start-2 sm:text-sm">
                {{ editingBill ? 'Save Changes' : 'Create Bill' }}
              </button>
              <button @click="showNewBillModal = false" type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:mt-0 sm:col-start-1 sm:text-sm">
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
import { ref, computed } from 'vue'
import { useRuntimeConfig } from '#imports'

const config = useRuntimeConfig()

// State
const bills = ref([])
const vendors = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const vendorFilter = ref('')
const dueDateFilter = ref('')
const showNewBillModal = ref(false)
const editingBill = ref(null)

const billForm = ref({
  billNumber: '',
  vendorId: '',
  dueDate: '',
  amount: '',
  status: ''
})

// Computed
const filteredBills = computed(() => {
  let filtered = bills.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(bill => 
      bill.billNumber.toLowerCase().includes(query) ||
      getVendorName(bill.vendorId).toLowerCase().includes(query)
    )
  }

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(bill => bill.status === statusFilter.value)
  }

  // Apply vendor filter
  if (vendorFilter.value) {
    filtered = filtered.filter(bill => bill.vendorId === vendorFilter.value)
  }

  // Apply due date filter
  if (dueDateFilter.value) {
    const today = new Date()
    const thisWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
    const thisMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)

    filtered = filtered.filter(bill => {
      const dueDate = new Date(bill.dueDate)
      switch (dueDateFilter.value) {
        case 'overdue':
          return dueDate < today
        case 'due_today':
          return dueDate.toDateString() === today.toDateString()
        case 'due_this_week':
          return dueDate <= thisWeek
        case 'due_this_month':
          return dueDate <= thisMonth
        default:
          return true
      }
    })
  }

  return filtered
})

// Methods
const fetchBills = async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/bills`)
    if (!response.ok) throw new Error('Failed to fetch bills')
    bills.value = await response.json()
  } catch (error) {
    console.error('Error fetching bills:', error)
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

const saveBill = async () => {
  try {
    const url = `${config.public.apiBase}/api/bills${editingBill.value ? `/${editingBill.value.id}` : ''}`
    const method = editingBill.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(billForm.value),
    })

    if (!response.ok) throw new Error('Failed to save bill')
    
    await fetchBills()
    showNewBillModal.value = false
    resetForm()
  } catch (error) {
    console.error('Error saving bill:', error)
  }
}

const editBill = (bill) => {
  editingBill.value = bill
  billForm.value = { ...bill }
  showNewBillModal.value = true
}

const deleteBill = async (id) => {
  if (!confirm('Are you sure you want to delete this bill?')) return
  
  try {
    const response = await fetch(`${config.public.apiBase}/api/bills/${id}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) throw new Error('Failed to delete bill')
    
    await fetchBills()
  } catch (error) {
    console.error('Error deleting bill:', error)
  }
}

const resetForm = () => {
  editingBill.value = null
  billForm.value = {
    billNumber: '',
    vendorId: '',
    dueDate: '',
    amount: '',
    status: ''
  }
}

const getVendorName = (vendorId) => {
  const vendor = vendors.value.find(v => v.id === vendorId)
  return vendor ? vendor.name : 'Unknown Vendor'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

// Initial fetch
fetchBills()
fetchVendors()
</script>
