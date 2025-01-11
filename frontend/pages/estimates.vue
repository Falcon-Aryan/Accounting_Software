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
              <option value="sent">Sent</option>
              <option value="accepted">Accepted</option>
              <option value="declined">Declined</option>
              <option value="void">Void</option>
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
            {{ estimate.estimate_no }}
          </NuxtLink>
          <div v-if="estimate.status === 'void'" class="text-xs text-red-600 mt-1">
            {{ estimate.void_reason || 'No reason provided' }}
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatDate(estimate.estimate_date) }}
          <div v-if="estimate.status === 'void' && estimate.voided_at" class="text-xs text-gray-400 mt-1">
            Voided: {{ formatDate(estimate.voided_at) }}
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
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span
            :class="{
              'px-2 py-1 text-xs font-medium rounded-full': true,
              'bg-gray-100 text-gray-800': estimate.status === 'draft',
              'bg-blue-100 text-blue-800': estimate.status === 'sent',
              'bg-green-100 text-green-800': estimate.status === 'accepted',
              'bg-red-100 text-red-800': estimate.status === 'declined',
              'bg-gray-100 text-gray-800 line-through': estimate.status === 'void'
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
              <svg class="ml-2 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
            <div 
              v-if="openOptionsId === estimate.id"
              class="absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
              @click.stop
            >
              <div class="py-1" role="menu" aria-orientation="vertical">
                <!-- Edit Option -->
                <button
                  @click="editEstimate(estimate)"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  role="menuitem"
                  :disabled="estimate.status === 'accepted'"
                >
                  Edit
                </button>

                <!-- Convert to Invoice Option -->
                <button
                  v-if="estimate.status === 'accepted'"
                  @click="convertToInvoice(estimate.id)"
                  class="w-full text-left px-4 py-2 text-sm text-indigo-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  Convert to Invoice
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

                <!-- Void Option -->
                <button
                  v-if="estimate.status !== 'void'"
                  @click="voidEstimate(estimate.id)"
                  class="w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  Void
                </button>

                <!-- Delete Option -->
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
      :estimate="selectedEditEstimate"
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
import NewInvoiceModal from '~/components/NewInvoiceModal.vue'
import EditInvoiceModal from '~/components/EditInvoiceModal.vue'
import PayInvoiceModal from '~/components/PayInvoiceModal.vue'
import { useRuntimeConfig } from '#app'
import { initializeApp } from 'firebase/app'
import { firebaseConfig } from '../config/firebase.config'

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const config = useRuntimeConfig()

// Reactive state
const invoices = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const openOptionsForInvoice = ref(null)
const selectedStatus = ref('All')
const searchQuery = ref('')
const showNewInvoiceModal = ref(false)
const showEditInvoiceModal = ref(false)
const showPayInvoiceModal = ref(false)
const selectedEditInvoice = ref(null)
const selectedPaymentInvoice = ref(null)
const isAuthenticated = ref(false)

// Get current user's ID token
async function getIdToken() {
  const user = auth.currentUser
  if (!user) {
    throw new Error('No authenticated user')
  }
  return user.getIdToken()
}

// Fetch invoices from the API
async function fetchInvoices() {
  try {
    isLoading.value = true
    errorMessage.value = ''
    const token = await getIdToken()
    
    await fetch(`${config.public.apiBase}/api/invoices/update_summary`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    const queryParams = new URLSearchParams()
    if (selectedStatus.value !== 'All') {
      queryParams.append('status', selectedStatus.value)
    }
    if (searchQuery.value) {
      queryParams.append('search', searchQuery.value)
    }

    const response = await fetch(`${config.public.apiBase}/api/invoices/list_invoices?${queryParams.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to fetch invoices')
    }

    const data = await response.json()
    invoices.value = data.invoices
  } catch (error) {
    if (error.message === 'No authenticated user') {
      errorMessage.value = 'Please log in to view invoices'
    } else {
      errorMessage.value = error.message
    }
    console.error('Error fetching invoices:', error)
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
      fetchInvoices()
    } else {
      console.log('No user authenticated')
      invoices.value = []
      errorMessage.value = 'Please log in to view invoices'
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
  if (openOptionsForInvoice.value && !event.target.closest('.options-container')) {
    openOptionsForInvoice.value = null
  }
}

// Filter invoices based on search query and status
const filteredInvoices = computed(() => {
  if (!invoices.value) return []
  
  let filtered = invoices.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(inv => 
      inv.invoice_no.toLowerCase().includes(query) ||
      inv.customer_name?.toLowerCase().includes(query)
    )
  }
  
  if (selectedStatus.value !== 'All') {
    filtered = filtered.filter(inv => inv.status === selectedStatus.value)
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

function toggleOptions(invoiceId, event) {
  event.stopPropagation()
  openOptionsForInvoice.value = openOptionsForInvoice.value === invoiceId ? null : invoiceId
}

function editInvoice(invoice) {
  showPayInvoiceModal.value = false
  showNewInvoiceModal.value = false
  selectedEditInvoice.value = invoice
  openOptionsForInvoice.value = null
  showEditInvoiceModal.value = true
}

function closeEditInvoiceModal() {
  selectedEditInvoice.value = null
  showEditInvoiceModal.value = false
}

async function handleUpdateInvoice(updatedData) {
  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/invoices/update_invoice/${updatedData.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(updatedData)
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.error || 'Failed to update invoice')
    }

    await fetchInvoices()
    closeEditInvoiceModal()
  } catch (error) {
    if (error.message === 'No authenticated user') {
      errorMessage.value = 'Please log in to update invoices'
    } else {
      errorMessage.value = error.message
    }
    console.error('Error updating invoice:', error)
  }
}

async function confirmDelete(invoice) {
  const message = invoice.status !== 'draft' 
    ? `Are you sure you want to delete invoice ${invoice.invoice_no}?\n\nWarning: This will reverse all associated transactions.` 
    : `Are you sure you want to delete invoice ${invoice.invoice_no}?`;

  if (!confirm(message)) {
    return;
  }

  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/invoices/delete_invoice/${invoice.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,  
        'Content-Type': 'application/json'      
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to delete invoice');
    }

    await fetchInvoices();
    openOptionsForInvoice.value = null;
  } catch (error) {
    if (error.message === 'No authenticated user') {
      errorMessage.value = 'Please log in to delete invoices'
    } else {
      errorMessage.value = error.message
    }
    console.error('Error deleting invoice:', error);
  }
}

async function voidInvoice(invoiceId) {
  const reason = prompt('Please provide a reason for voiding this invoice:')
  if (!reason) return // User cancelled the prompt

  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/invoices/void/${invoiceId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ void_reason: reason })
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.error || 'Failed to void invoice')
    }

    await fetchInvoices()
    openOptionsForInvoice.value = null
  } catch (error) {
    if (error.message === 'No authenticated user') {
      errorMessage.value = 'Please log in to void invoices'
    } else {
      errorMessage.value = error.message
    }
    console.error('Error voiding invoice:', error)
  }
}

async function sendInvoice(invoice) {
  if (!confirm(`Are you sure you want to send invoice ${invoice.invoice_no}?`)) {
    return;
  }

  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/invoices/send/${invoice.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to send invoice');
    }

    await fetchInvoices();
    openOptionsForInvoice.value = null;
  } catch (error) {
    errorMessage.value = error.message;
    console.error('Error sending invoice:', error);
  }
}

async function postInvoice(invoiceId) {
  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/invoices/post/${invoiceId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.error || 'Failed to post invoice')
    }

    await fetchInvoices()
    openOptionsForInvoice.value = null
  } catch (error) {
    if (error.message === 'No authenticated user') {
      errorMessage.value = 'Please log in to post invoices'
    } else {
      errorMessage.value = error.message
    }
    console.error('Error posting invoice:', error)
  }
}

function openNewInvoiceModal() {
  showEditInvoiceModal.value = false
  showPayInvoiceModal.value = false
  showNewInvoiceModal.value = true
}

function closeNewInvoiceModal() {
  showNewInvoiceModal.value = false
}

async function handleCreateInvoice(invoiceData) {
  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/invoices/create_invoice`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(invoiceData)
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.error || 'Failed to create invoice')
    }

    await fetchInvoices()
    closeNewInvoiceModal()
  } catch (error) {
    if (error.message === 'No authenticated user') {
      errorMessage.value = 'Please log in to create invoices'
    } else {
      errorMessage.value = error.message
    }
    console.error('Error creating invoice:', error)
  }
}

function payInvoice(invoice) {
  showEditInvoiceModal.value = false
  showNewInvoiceModal.value = false
  selectedPaymentInvoice.value = invoice
  openOptionsForInvoice.value = null
  showPayInvoiceModal.value = true
}

function closePayInvoiceModal() {
  selectedPaymentInvoice.value = null
  showPayInvoiceModal.value = false
}

async function handlePaymentRecorded(result) {
  try {
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/invoices/add_payment/${selectedPaymentInvoice.value.id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(result)
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.error || 'Failed to record payment')
    }

    await fetchInvoices()
    closePayInvoiceModal()
  } catch (error) {
    if (error.message === 'No authenticated user') {
      errorMessage.value = 'Please log in to record payments'
    } else {
      errorMessage.value = error.message
    }
    console.error('Error recording payment:', error)
  }
}

// Watch for changes in search query or status to refresh invoices
watch([searchQuery, selectedStatus], () => {
  fetchInvoices()
})
</script>
