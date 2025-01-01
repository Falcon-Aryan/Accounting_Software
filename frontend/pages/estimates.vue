<template>
  <TablePageLayout
    title="Estimates"
    :error-message="errorMessage"
    :is-loading="isLoading"
    :has-data="filteredEstimates.length > 0"
    :column-count="5"
    empty-state-message="No estimates found. Create a new estimate to get started."
  >
    <!-- Search Filter -->
    <template #filters>
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex-1 max-w-sm">
            <label for="search" class="sr-only">Search estimates</label>
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
                placeholder="Search estimates..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <select
              v-model="selectedStatus"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="All">All Status</option>
              <option value="Draft">Draft</option>
              <option value="Sent">Sent</option>
              <option value="Accepted">Accepted</option>
              <option value="Declined">Declined</option>
            </select>
            <BaseButton @click="openNewEstimateModal">
              New Estimate
            </BaseButton>
          </div>
        </div>
      </div>
    </template>

    <!-- Table Header -->
    <template #table-header>
      <tr>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Number
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Customer
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Date
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Total Amount
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Status
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Actions
        </th>
      </tr>
    </template>

    <!-- Table Body -->
    <template #table-body>
      <tr v-for="estimate in filteredEstimates" :key="estimate.id" class="even:bg-gray-50">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ estimate.estimate_no }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-black-500">
          {{ estimate.customer_name }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatDate(estimate.estimate_date) }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatCurrency(estimate.total_amount) }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm">
          <StatusBadge :status="estimate.status" />
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-sm font-medium">
          <div class="relative inline-block text-left options-container">
            <button
              @click="(event) => toggleOptions(estimate.id, event)"
              class="text-indigo-600 hover:text-indigo-900 flex items-center"
            >
              Options
              <svg class="ml-2 -mr-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div 
              v-if="openOptionsId === estimate.id"
              class="absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
              @click.stop
            >
              <div class="flex flex-col" role="menu">
                <div class="py-1">
                  <button
                    @click="editEstimate(estimate)"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-white disabled:cursor-not-allowed"
                    role="menuitem"
                    :disabled="estimate.status === 'accepted'"
                  >
                    Edit
                  </button>
                </div>
                <div class="py-1 border-t border-gray-100">
                  <button
                    @click="convertToInvoice(estimate.id)"
                    class="w-full text-left px-4 py-2 text-sm text-indigo-700 hover:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-white disabled:cursor-not-allowed"
                    role="menuitem"
                    :disabled="estimate.status === 'accepted'"
                  >
                    Convert to Invoice
                  </button>
                </div>
                <div class="py-1 border-t border-gray-100">
                  <button
                    @click="deleteEstimate(estimate.id)"
                    class="w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </template>

    <!-- Modals -->
    <template #modals>
      <NewEstimateModal
        :is-open="showNewEstimateModal"
        @close="closeNewEstimateModal"
        @save="handleCreateEstimate"
      />
      <EditEstimateModal
        v-if="isEditEstimateModalOpen"
        :is-open="isEditEstimateModalOpen"
        :estimate="selectedEstimate"
        @close="closeEditEstimateModal"
        @update="handleUpdateEstimate"
      />
    </template>
  </TablePageLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRuntimeConfig } from '#app'
import TablePageLayout from '../components/TablePageLayout.vue'
import NewEstimateModal from '../components/NewEstimateModal.vue'
import EditEstimateModal from '../components/EditEstimateModal.vue'
import StatusBadge from '../components/StatusBadge.vue'
import BaseButton from '../components/BaseButton.vue'

const config = useRuntimeConfig()
const estimates = ref([])
const searchQuery = ref('')
const selectedStatus = ref('All')
const isLoading = ref(true)
const errorMessage = ref('')
const showNewEstimateModal = ref(false)
const isEditEstimateModalOpen = ref(false)
const selectedEstimate = ref(null)
const openOptionsId = ref(null)

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (openOptionsId.value && !event.target.closest('.options-container')) {
    openOptionsId.value = null
  }
}

onMounted(() => {
  fetchEstimates()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Fetch estimates from the API
const fetchEstimates = async () => {
  try {
    isLoading.value = true
    const response = await fetch(`${config.public.apiBase}/api/estimates/list_estimates`)
    if (!response.ok) throw new Error('Failed to fetch estimates')
    const data = await response.json()
    estimates.value = data.estimates || []
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error fetching estimates:', error)
  } finally {
    isLoading.value = false
  }
}

// Filter estimates based on search query and status
const filteredEstimates = computed(() => {
  if (!estimates.value) return []
  
  let filtered = [...estimates.value]
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(est => 
      (est.estimate_no && est.estimate_no.toLowerCase().includes(query)) ||
      (est.customer_name && est.customer_name.toLowerCase().includes(query)) ||
      (est.total_amount && est.total_amount.toString().includes(query))
    )
  }
  
  // Filter by status
  if (selectedStatus.value && selectedStatus.value !== 'All') {
    filtered = filtered.filter(est => 
      est.status && est.status.toLowerCase() === selectedStatus.value.toLowerCase()
    )
  }
  
  return filtered
})

// Format date
function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString('en-US', { dateStyle: 'short' });
}

// Calculate total amount
function calculateTotal(products) {
  if (!products) return 0
  return products.reduce((sum, product) => sum + (product.price || 0), 0)
}

// Format currency
function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

// Toggle options menu
function toggleOptions(estimateId, event) {
  event.stopPropagation()
  openOptionsId.value = openOptionsId.value === estimateId ? null : estimateId
}

// Delete estimate
async function deleteEstimate(estimateId) {
  if (!confirm('Are you sure you want to delete this estimate?')) return

  try {
    const response = await fetch(`${config.public.apiBase}/api/estimates/delete_estimate/${estimateId}`, {
      method: 'DELETE'
    })

    if (!response.ok) throw new Error('Failed to delete estimate')

    await fetchEstimates()
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error deleting estimate:', error)
  }
}

// Edit estimate handler
function editEstimate(estimate) {
  selectedEstimate.value = estimate
  isEditEstimateModalOpen.value = true
  openOptionsId.value = null
}

// Close edit modal
function closeEditEstimateModal() {
  isEditEstimateModalOpen.value = false
  selectedEstimate.value = null
}

// Handle update estimate
async function handleUpdateEstimate(updatedData) {
  try {
    const response = await fetch(`${config.public.apiBase}/api/estimates/update_estimate/${selectedEstimate.value.id}`, {
      method: 'PATCH',  // Changed from PUT to PATCH to match backend
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updatedData)
    })

    if (!response.ok) throw new Error('Failed to update estimate')

    await fetchEstimates()
    closeEditEstimateModal()
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error updating estimate:', error)
  }
}

// Convert estimate to invoice
const convertToInvoice = async (estimateId) => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/estimates/convert_to_invoice/${estimateId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to convert estimate')
    }

    const result = await response.json()
    
    // Refresh estimates list
    await fetchEstimates()
    
    // Close options menu
    openOptionsId.value = null
    
    // Show success message (you can implement this)
    console.log('Successfully converted estimate to invoice:', result.invoice_id)
  } catch (error) {
    console.error('Error converting estimate:', error)
    errorMessage.value = error.message
  }
}

// Modal handlers
function openNewEstimateModal() {
  showNewEstimateModal.value = true
}

function closeNewEstimateModal() {
  showNewEstimateModal.value = false
}

async function handleCreateEstimate(estimateData) {
  try {
    const response = await fetch(`${config.public.apiBase}/api/estimates/create_estimate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(estimateData)
    })

    if (!response.ok) throw new Error('Failed to create estimate')

    await fetchEstimates()
    closeNewEstimateModal()
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error creating estimate:', error)
  }
}
</script>
