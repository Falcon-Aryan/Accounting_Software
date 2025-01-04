<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="md:flex md:items-center md:justify-between mb-6">
        <div class="flex-1 min-w-0">
          <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">Vendors</h2>
        </div>
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <button @click="showNewVendorModal = true" class="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
            Add Vendor
          </button>
        </div>
      </div>

      <!-- Search -->
      <div class="mb-6">
        <label for="search" class="sr-only">Search vendors</label>
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
            placeholder="Search vendors"
            type="search"
          >
        </div>
      </div>

      <!-- Vendors Table -->
      <div class="flex flex-col">
        <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Phone
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Address
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Balance
                    </th>
                    <th scope="col" class="relative px-6 py-3">
                      <span class="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="vendor in filteredVendors" :key="vendor.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ vendor.name }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ vendor.email }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ vendor.phone }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-sm text-gray-900">{{ vendor.address }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">${{ vendor.balance.toFixed(2) }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button @click="editVendor(vendor)" class="text-green-600 hover:text-green-900 mr-4">Edit</button>
                      <button @click="deleteVendor(vendor.id)" class="text-red-600 hover:text-red-900">Delete</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New/Edit Vendor Modal -->
    <div v-if="showNewVendorModal" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <form @submit.prevent="saveVendor">
            <div>
              <h3 class="text-lg leading-6 font-medium text-gray-900">{{ editingVendor ? 'Edit' : 'New' }} Vendor</h3>
              <div class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div class="sm:col-span-6">
                  <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
                  <div class="mt-1">
                    <input type="text" v-model="vendorForm.name" id="name" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-3">
                  <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                  <div class="mt-1">
                    <input type="email" v-model="vendorForm.email" id="email" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-3">
                  <label for="phone" class="block text-sm font-medium text-gray-700">Phone</label>
                  <div class="mt-1">
                    <input type="tel" v-model="vendorForm.phone" id="phone" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>

                <div class="sm:col-span-6">
                  <label for="address" class="block text-sm font-medium text-gray-700">Address</label>
                  <div class="mt-1">
                    <textarea v-model="vendorForm.address" id="address" rows="3" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md"></textarea>
                  </div>
                </div>

                <div class="sm:col-span-6">
                  <label for="balance" class="block text-sm font-medium text-gray-700">Balance</label>
                  <div class="mt-1">
                    <input type="number" step="0.01" v-model="vendorForm.balance" id="balance" required class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md">
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
              <button type="submit" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:col-start-2 sm:text-sm">
                {{ editingVendor ? 'Save Changes' : 'Create Vendor' }}
              </button>
              <button @click="showNewVendorModal = false" type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:mt-0 sm:col-start-1 sm:text-sm">
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
const vendors = ref([])
const searchQuery = ref('')
const showNewVendorModal = ref(false)
const editingVendor = ref(null)

const vendorForm = ref({
  name: '',
  email: '',
  phone: '',
  address: '',
  balance: 0
})

// Computed
const filteredVendors = computed(() => {
  if (!searchQuery.value) return vendors.value

  const query = searchQuery.value.toLowerCase()
  return vendors.value.filter(vendor => 
    vendor.name.toLowerCase().includes(query) ||
    vendor.email.toLowerCase().includes(query) ||
    vendor.phone.includes(query)
  )
})

// Methods
const fetchVendors = async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/vendors`)
    if (!response.ok) throw new Error('Failed to fetch vendors')
    vendors.value = await response.json()
  } catch (error) {
    console.error('Error fetching vendors:', error)
  }
}

const saveVendor = async () => {
  try {
    const url = `${config.public.apiBase}/api/vendors${editingVendor.value ? `/${editingVendor.value.id}` : ''}`
    const method = editingVendor.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(vendorForm.value),
    })

    if (!response.ok) throw new Error('Failed to save vendor')
    
    await fetchVendors()
    showNewVendorModal.value = false
    resetForm()
  } catch (error) {
    console.error('Error saving vendor:', error)
  }
}

const editVendor = (vendor) => {
  editingVendor.value = vendor
  vendorForm.value = { ...vendor }
  showNewVendorModal.value = true
}

const deleteVendor = async (id) => {
  if (!confirm('Are you sure you want to delete this vendor?')) return
  
  try {
    const response = await fetch(`${config.public.apiBase}/api/vendors/${id}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) throw new Error('Failed to delete vendor')
    
    await fetchVendors()
  } catch (error) {
    console.error('Error deleting vendor:', error)
  }
}

const resetForm = () => {
  editingVendor.value = null
  vendorForm.value = {
    name: '',
    email: '',
    phone: '',
    address: '',
    balance: 0
  }
}

// Initial fetch
fetchVendors()
</script>
