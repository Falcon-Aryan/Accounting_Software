<template>
  <TablePageLayout
    title="Estimates"
    :error-message="errorMessage"
    :is-loading="isLoading"
    :has-data="filteredEstimates.length > 0"
    :column-count="6"
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
              <option value="draft">Draft</option>
              <option value="pending">Pending</option>
              <option value="accepted">Accepted</option>
              <option value="declined">Declined</option>
              <option value="expired">Expired</option>
              <option value="converted">Converted</option>
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
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        Estimate #
      </th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        Date
      </th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        Customer
      </th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        Amount
      </th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        Expiry Date
      </th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        Status
      </th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        Actions
      </th>
    </template>

    <!-- Table Body -->
    <template #table-body>
      <tr v-for="estimate in filteredEstimates" :key="estimate.id" class="even:bg-gray-50">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          <NuxtLink 
            :to="`/reports/estimate/${estimate.id}`"
            class="text-green-600 hover:text-green-500"
          >
            {{ estimate.id }}
          </NuxtLink>
          <div v-if="estimate.status === 'declined'" class="text-xs text-red-600 mt-1">
            {{ estimate.decline_reason || 'No reason provided' }}
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatDate(estimate.estimate_date) }}
          <div v-if="estimate.status === 'declined' && estimate.declined_at" class="text-xs text-gray-400 mt-1">
            Declined: {{ formatDate(estimate.declined_at) }}
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ estimate.customer_name }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatCurrency(estimate.total_amount) }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatDate(estimate.expiry_date) }}
          <div 
            v-if="isExpiringWithin7Days(estimate.expiry_date)" 
            class="text-xs text-orange-600 mt-1"
          >
            Expires soon
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span
            :class="{
              'px-2 py-1 text-xs font-medium rounded-full': true,
              'bg-gray-100 text-gray-800': estimate.status === 'draft',
              'bg-blue-100 text-blue-800': estimate.status === 'pending',
              'bg-green-100 text-green-800': estimate.status === 'accepted',
              'bg-red-100 text-red-800': estimate.status === 'declined',
              'bg-gray-100 text-gray-800': estimate.status === 'expired',
              'bg-yellow-100 text-yellow-800': estimate.status === 'converted'
            }"
          >
            {{ estimate.status }}
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
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
              v-if="openOptionsForEstimate === estimate.id"
              class="absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
              @click.stop
            >
            <div class="flex flex-col" role="menu">
              <!-- Edit Option -->
                <button
                  @click="editEstimate(estimate)"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  role="menuitem"
                  :disabled="estimate.status === 'accepted'"
                >
                  Edit Estimate
                </button>

                <!-- Send Option -->
                <button
                  v-if="estimate.status === 'draft'"
                  @click="sendEstimate(estimate)"
                  class="w-full text-left px-4 py-2 text-sm text-blue-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  Send Estimate
                </button>

                <!-- Convert to Invoice Option -->
                <button
                  v-if="estimate.status === 'accepted'"
                  @click="convertToInvoice(estimate)"
                  class="w-full text-left px-4 py-2 text-sm text-indigo-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  Convert to Invoice
                </button>

                <!-- Delete Option -->
                <button
                  @click="confirmDelete(estimate.id)"
                  class="w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  Delete Estimate
                </button>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </template>
  </TablePageLayout>

  <!-- Modals -->
  <Teleport to="body">
    <NewEstimateModal
      :is-open="showNewEstimateModal"
      @close="closeNewEstimateModal"
      @save="handleCreateEstimate"
    />
    <EditEstimateModal
      v-if="selectedEstimate"
      :estimate="selectedEstimate"
      :is-open="showEditEstimateModal"
      @save="handleUpdateEstimate"
      @close="closeEditEstimateModal"
    />
  </Teleport>
</template>

<script setup>
definePageMeta({
  middleware: ['auth']
})

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { getAuth, onAuthStateChanged } from 'firebase/auth'
import TablePageLayout from '~/components/TablePageLayout.vue'
import NewEstimateModal from '~/components/NewEstimateModal.vue'
import EditEstimateModal from '~/components/EditEstimateModal.vue'
import { useRuntimeConfig } from '#app'
import { initializeApp } from 'firebase/app'
import { firebaseConfig } from '../config/firebase.config'

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const config = useRuntimeConfig()

// Reactive state
const estimates = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const openOptionsForEstimate = ref(null)
const selectedStatus = ref('All')
const searchQuery = ref('')
const showNewEstimateModal = ref(false)
const showEditEstimateModal = ref(false)
const selectedEstimate = ref(null)
const isAuthenticated = ref(false)

// Get current user's ID token
async function getIdToken() {
  const user = auth.currentUser
  if (!user) {
    throw new Error('No authenticated user')
  }
  return user.getIdToken()
}


const mapEstimateToBaseDocument = (estimate) => {
  const now = new Date().toISOString()
  return {
    ...estimate,
    created_at: now,
    updated_at: now,
    date: estimate.estimate_date || estimate.date,
    total: estimate.total_amount || estimate.total || 0,
    balance_due: estimate.balance_due || estimate.total || 0,
    notes: estimate.notes || "",
    status: estimate.status || "draft",
    payments: estimate.payments || [], 
    sent_at: estimate.sent_at || null,
    voided_at: estimate.voided_at || null,
    void_reason: estimate.void_reason || null,
    line_items: (estimate.line_items || []).map(item => ({
      ...item,
      unit_price: item.price || item.unit_price,
      total: (item.quantity * (item.price || item.unit_price))
    }))
  }
}

const mapBaseDocumentToEstimate = (doc) => {
  return {
    ...doc,
    estimate_date: doc.date,
    total_amount: doc.total,
    balance_due: doc.balance_due,
    line_items: (doc.line_items || []).map(item => ({
      ...item,
      price: item.unit_price
    }))
  }
}

// Fetch estimates from the API
async function fetchEstimates() {
  try {
    isLoading.value = true
    errorMessage.value = ''
    const token = await getIdToken()
    console.log('Token obtained')
    
    await fetch(`${config.public.apiBase}/api/estimates/update_summary`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    console.log('Summary updated') 

    const queryParams = new URLSearchParams()
    if (selectedStatus.value !== 'All') {
      queryParams.append('status', selectedStatus.value.toLowerCase())
    }
    if (searchQuery.value) {
      queryParams.append('search', searchQuery.value)
    }

    const response = await fetch(`${config.public.apiBase}/api/estimates/list_estimates?${queryParams.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    console.log('Response status:', response.status)
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to fetch estimates')
    }

    const data = await response.json()
    console.log('Raw response data:', data)

    estimates.value = data.estimates.map(mapBaseDocumentToEstimate)
    console.log('Mapped estimates:', estimates.value)
  } catch (error) {
    console.error('Error in fetchEstimates:', error)
    handleError(error)
  } finally {
    isLoading.value = false
  }
}

// Watch for auth state changes
onMounted(() => {
  const unsubscribe = onAuthStateChanged(auth, (user) => {
    isAuthenticated.value = !!user
    if (user) {
      console.log('User is authenticated:', user.email)
      fetchEstimates()
    } else {
      console.log('No user authenticated')
      estimates.value = []
      errorMessage.value = 'Please log in to view estimates'
    }
  })

  document.addEventListener('click', handleClickOutside)

  // Clean up subscription and event listener
  onUnmounted(() => {
    unsubscribe()
    document.removeEventListener('click', handleClickOutside)
  })
})

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (openOptionsForEstimate.value && !event.target.closest('.options-container')) {
    openOptionsForEstimate.value = null
  }
}

// Filter Estimates based on search query and status
const filteredEstimates = computed(() => {
  if (!estimates.value) return []
  
  let filtered = estimates.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(est => 
      est.id.toLowerCase().includes(query) ||
      est.estimate_no?.toLowerCase().includes(query) ||
      est.customer_name?.toLowerCase().includes(query)
    )
  }
  
  if (selectedStatus.value !== 'All') {
    filtered = filtered.filter(est => est.status === selectedStatus.value)
  }
  
  return filtered
})

function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString();
}

function calculateTotal(products) {
  return (products || []).reduce((sum, product) => sum + (Number(product.price) * Number(product.quantity) || 0), 0)
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

function toggleOptions(estimateId, event) {
  event.stopPropagation()
  openOptionsForEstimate.value = openOptionsForEstimate.value === estimateId ? null : estimateId
}

function editEstimate(estimate) {
  selectedEstimate.value = estimate
  showEditEstimateModal.value = true
  openOptionsForEstimate.value = null
}

function closeEditEstimateModal() {
  showEditEstimateModal.value = false
  selectedEstimate.value = null
}

async function handleUpdateEstimate(updatedData) {
  try {
    const token = await getIdToken()
    const mappedData = mapEstimateToBaseDocument(updatedData)

    const response = await fetch(`${config.public.apiBase}/api/estimates/update_estimate/${updatedData.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(mappedData)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to update estimate')
    }

    await fetchEstimates()
    closeEditEstimateModal()
  } catch (error) {
    handleError(error)
  }
}

async function sendEstimate(estimate) {
  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/estimates/send/${estimate.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to send estimate')
    }

    await fetchEstimates()
    openOptionsForEstimate.value = null
  } catch (error) {
    handleError(error)
  }
}

async function convertToInvoice(estimate) {
  if (!estimate || !estimate.id) {
    console.error('Invalid estimate:', estimate)
    return
  }

  if (!confirm('Are you sure you want to convert this estimate to an invoice?')) {
    return
  }

  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/estimates/convert_to_invoice/${estimate.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to convert estimate to invoice')
    }

    await fetchEstimates()
    openOptionsForEstimate.value = null
  } catch (error) {
    handleError(error)
  }
}


function isExpiringWithin7Days(expiryDate) {
  if (!expiryDate) return false;
  const expiry = new Date(expiryDate);
  const now = new Date();
  const daysUntilExpiry = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
  return daysUntilExpiry > 0 && daysUntilExpiry <= 7;
}

async function confirmDelete(estimateId) {

  const estimate = filteredEstimates.value.find(est => est.id === estimateId)
  
  if (!estimate) {
    handleError('Estimate not found')
    return
  }
  
  const message = estimate.status !== 'draft' 
    ? `Are you sure you want to delete estimate ${estimate.estimate_no}?\n\nWarning: This will reverse all associated transactions.` 
    : `Are you sure you want to delete estimate ${estimate.estimate_no}?`;

  if (!confirm(message)) {
    return;
  }

  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/estimates/delete_estimate/${estimateId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,  
        'Content-Type': 'application/json'      
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to delete estimate');
    }

    await fetchEstimates();
    openOptionsForEstimate.value = null;
  } catch (error) {
    handleError(error);
  }
}

function openNewEstimateModal() {
  showEditEstimateModal.value = false
  showNewEstimateModal.value = true
}

function closeNewEstimateModal() {
  showNewEstimateModal.value = false
}

async function handleCreateEstimate(estimateData) {
  try {
    const token = await getIdToken()
    const mappedData = mapEstimateToBaseDocument(estimateData)

    const response = await fetch(`${config.public.apiBase}/api/estimates/create_estimate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(mappedData)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to create estimate')
    }

    await fetchEstimates()
    closeNewEstimateModal()
  } catch (error) {
    handleError(error)
  }
}

function handleError(error) {
  if (error.message === 'No authenticated user') {
    errorMessage.value = 'Please log in to perform this action'
  } else {
    errorMessage.value = error.message
  }
  console.error('Error:', error)
}

// Watch for changes in search query or status to refresh Estimates
watch([searchQuery, selectedStatus], () => {
  fetchEstimates()
})
</script>
