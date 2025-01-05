<template>
  <TablePageLayout
    title="Customers"
    :is-loading="isLoading"
    :has-data="filteredCustomers.length > 0"
    :column-count="5"
    empty-state-message="No customers found. Add a new customer to get started."
  >
    <!-- Search Filter -->
    <template #filters>
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex-1 max-w-sm">
            <label for="search" class="sr-only">Search customers</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
              </div>
              <input
                id="search"
                v-model="searchQuery"
                type="text"
                placeholder="Search customers..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <BaseButton @click="openNewCustomerModal">
              New Customer
            </BaseButton>
          </div>
        </div>
      </div>
    </template>

    <!-- Table Header -->
    <template #table-header>
      <tr>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Customer
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Contact
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Location
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Actions
        </th>
      </tr>
    </template>

    <!-- Table Body -->
    <template #table-body>
      <tr v-for="customer in filteredCustomers" :key="customer.id" class="even:bg-gray-50">
        <td class="px-6 py-4 whitespace-nowrap">
          <div>
            <div class="text-sm font-medium text-gray-900">
              <NuxtLink 
                :to="`/reports/customer/${customer.id}`"
                class="text-green-600 hover:text-green-500"
              >
                {{ customer.first_name }} {{ customer.last_name }}
              </NuxtLink>
            </div>
            <div class="text-sm text-gray-500">{{ customer.customer_no }}</div>
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <div class="text-sm text-gray-900">{{ customer.email }}</div>
          <div class="text-sm text-gray-500">{{ customer.phone }}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <div class="text-sm text-gray-900">{{ customer.billing_address.city }}</div>
          <div class="text-sm text-gray-500">{{ customer.billing_address.state }}, {{ customer.billing_address.country }}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
          <div class="relative inline-block text-left options-container">
            <button
              @click="(event) => toggleDropdown(customer.id, event)"
              class="text-indigo-600 hover:text-indigo-900 flex items-center"
            >
              Options
              <svg class="ml-2 -mr-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <div v-if="openDropdownId === customer.id" class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none z-10">
              <div class="py-1">
                <button
                  @click="editCustomer(customer)"
                  class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 w-full text-left"
                >
                  <svg class="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit
                </button>
              </div>
              <div class="py-1">
                <button
                  @click="deleteCustomer(customer)"
                  class="group flex items-center px-4 py-2 text-sm text-red-700 hover:bg-red-100 hover:text-red-900 w-full text-left"
                >
                  <svg class="mr-3 h-5 w-5 text-red-400 group-hover:text-red-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </template>
  </TablePageLayout>

  <!-- Modals -->
  <NewCustomerModal
    ref="newCustomerModalRef"
    v-model="showNewCustomerModal"
    @submit="handleNewCustomer"
  />

  <EditCustomerModal
    v-if="selectedCustomer"
    :show="showEditCustomerModal"
    :customer="selectedCustomer"
    @close="closeEditCustomerModal"
    @submit="handleEditCustomer"
  />
</template>

<script setup>
import { getAuth } from 'firebase/auth'
definePageMeta({
  middleware: ['auth']
})
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRuntimeConfig } from '#app'
import BaseButton from '../components/BaseButton.vue'
import NewCustomerModal from '../components/NewCustomerModal.vue'
import EditCustomerModal from '../components/EditCustomerModal.vue'
import TablePageLayout from '../components/TablePageLayout.vue'

const config = useRuntimeConfig()
const customers = ref([])
const summary = ref({})
const searchQuery = ref('')
const showNewCustomerModal = ref(false)
const showEditCustomerModal = ref(false)
const selectedCustomer = ref(null)
const openDropdownId = ref(null)
const isLoading = ref(false)
const newCustomerModalRef = ref(null)

// Computed
const filteredCustomers = computed(() => {
  if (!searchQuery.value) return customers.value

  const query = searchQuery.value.toLowerCase()
  return customers.value.filter(customer => {
    return (
      customer.first_name.toLowerCase().includes(query) ||
      customer.last_name.toLowerCase().includes(query) ||
      customer.email.toLowerCase().includes(query) ||
      customer.customer_no.toLowerCase().includes(query)
    )
  })
})

// Methods
const fetchCustomers = async () => {
  isLoading.value = true
  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/customers/list_customers`, {
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    })
    const data = await response.json()
    customers.value = data.customers
  } catch (error) {
    console.error('Error fetching customers:', error)
  } finally {
    isLoading.value = false
  }
}

const handleClickOutside = (event) => {
  const dropdowns = document.querySelectorAll('.options-container')
  let clickedInsideDropdown = false
  
  dropdowns.forEach(dropdown => {
    if (dropdown.contains(event.target)) {
      clickedInsideDropdown = true
    }
  })
  
  if (!clickedInsideDropdown) {
    openDropdownId.value = null
  }
}

const toggleDropdown = (customerId, event) => {
  event.stopPropagation()
  if (openDropdownId.value === customerId) {
    openDropdownId.value = null
  } else {
    openDropdownId.value = customerId
  }
}

const openNewCustomerModal = () => {
  if (newCustomerModalRef.value) {
    newCustomerModalRef.value.resetForm()
  }
  showNewCustomerModal.value = true
}

const closeNewCustomerModal = () => {
  showNewCustomerModal.value = false
  if (newCustomerModalRef.value) {
    newCustomerModalRef.value.resetForm()
  }
}

const editCustomer = (customer) => {
  selectedCustomer.value = customer
  showEditCustomerModal.value = true
  openDropdownId.value = null
}

const closeEditCustomerModal = () => {
  showEditCustomerModal.value = false
  selectedCustomer.value = null
}

const handleNewCustomer = async (customerData) => {
  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/customers/create_customer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify(customerData)
    })
    const data = await response.json()
    if (response.ok) {
      customers.value.push(data.customer)
      closeNewCustomerModal()
      showSuccessToast('Customer created successfully')
    } else {
      showErrorToast(data.error || 'Failed to create customer')
    }
  } catch (error) {
    console.error('Error creating customer:', error)
    showErrorToast('Failed to create customer')
  }
}

const handleEditCustomer = async (customerData) => {
  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/customers/update_customer/${customerData.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify(customerData)
    })
    const data = await response.json()
    if (response.ok) {
      const index = customers.value.findIndex(c => c.id === customerData.id)
      if (index !== -1) {
        customers.value[index] = data.customer
      }
      closeEditCustomerModal()
      showSuccessToast('Customer updated successfully')
    } else {
      showErrorToast(data.error || 'Failed to update customer')
    }
  } catch (error) {
    console.error('Error updating customer:', error)
    showErrorToast('Failed to update customer')
  }
}

const deleteCustomer = async (customer) => {
  if (!confirm('Are you sure you want to delete this customer?')) return

  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/customers/delete_customer/${customer.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    })
    if (response.ok) {
      customers.value = customers.value.filter(c => c.id !== customer.id)
      showSuccessToast('Customer deleted successfully')
    } else {
      const data = await response.json()
      showErrorToast(data.error || 'Failed to delete customer')
    }
  } catch (error) {
    console.error('Error deleting customer:', error)
    showErrorToast('Failed to delete customer')
  }
}

onMounted(() => {
  fetchCustomers()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
