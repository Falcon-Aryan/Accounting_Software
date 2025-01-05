<template>
  <TablePageLayout
    title="Invoices"
    :error-message="errorMessage"
    :is-loading="isLoading"
    :has-data="filteredInvoices.length > 0"
    :column-count="7"
    empty-state-message="No invoices found. Create a new invoice to get started."
  >
    <!-- Search Filter -->
    <template #filters>
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex-1 max-w-sm">
            <label for="search" class="sr-only">Search invoices</label>
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
                placeholder="Search invoices..."
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
              <option value="posted">Posted</option>
              <option value="paid">Paid</option>
              <option value="overdue">Overdue</option>
              <option value="void">Void</option>
            </select>
            <BaseButton @click="openNewInvoiceModal">
              New Invoice
            </BaseButton>
          </div>
        </div>
      </div>
    </template>

    <!-- Table Header -->
    <template #table-header>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
        Invoice #
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
        Balance Due
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
      <tr v-for="invoice in filteredInvoices" :key="invoice.id" class="even:bg-gray-50">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          <NuxtLink 
            :to="`/reports/invoice/${invoice.id}`"
            class="text-green-600 hover:text-green-500"
          >
            {{ invoice.invoice_no }}
          </NuxtLink>
          <div v-if="invoice.status === 'void'" class="text-xs text-red-600 mt-1">
            {{ invoice.void_reason || 'No reason provided' }}
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatDate(invoice.invoice_date) }}
          <div v-if="invoice.status === 'void' && invoice.voided_at" class="text-xs text-gray-400 mt-1">
            Voided: {{ formatDate(invoice.voided_at) }}
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ invoice.customer_name }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatCurrency(invoice.total_amount) }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatCurrency(invoice.balance_due) }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span
            :class="{
              'px-2 py-1 text-xs font-medium rounded-full': true,
              'bg-gray-100 text-gray-800': invoice.status === 'draft',
              'bg-green-100 text-green-800': invoice.status === 'posted',
              'bg-blue-100 text-blue-800': invoice.status === 'paid',
              'bg-red-100 text-red-800': invoice.status === 'overdue',
              'bg-gray-100 text-gray-800 line-through': invoice.status === 'void'
            }"
          >
            {{ invoice.status }}
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
          <div class="relative inline-block text-left options-container">
            <button
              @click="(event) => toggleOptions(invoice.id, event)"
              class="text-indigo-600 hover:text-indigo-900 flex items-center"
            >
              Options
              <svg class="ml-2 -mr-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div 
              v-if="openOptionsForInvoice === invoice.id"
              class="absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
              @click.stop
            >
              <div class="flex flex-col" role="menu">
                <!-- Pay Invoice Option -->
                <div v-if="invoice.status !== 'void' && invoice.balance_due > 0" class="py-1">
                  <button
                    @click="payInvoice(invoice)"
                    class="w-full text-left px-4 py-2 text-sm text-indigo-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    Pay Invoice
                  </button>
                </div>

                <!-- Post Option - Only for draft invoices -->
                <div v-if="invoice.status === 'draft'" class="py-1 border-t border-gray-100">
                  <button
                    @click="postInvoice(invoice.id)"
                    class="w-full text-left px-4 py-2 text-sm text-green-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    Post
                  </button>
                </div>

                <!-- Edit Option -->
                <div class="py-1 border-t border-gray-100">
                  <button
                    @click="editInvoice(invoice)"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                    :disabled="invoice.status === 'void'"
                  >
                    Edit
                  </button>
                </div>

                <!-- Void Option -->
                <div v-if="invoice.status !== 'void'" class="py-1 border-t border-gray-100">
                  <button
                    @click="voidInvoice(invoice.id)"
                    class="w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    Void
                  </button>
                </div>

                <!-- Delete Option -->
                <div class="py-1 border-t border-gray-100">
                  <button
                    @click="confirmDelete(invoice)"
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
  </TablePageLayout>

  <!-- Modals -->
  <Teleport to="body">
    <NewInvoiceModal
      :is-open="showNewInvoiceModal"
      @close="closeNewInvoiceModal"
      @save="handleCreateInvoice"
    />
    <EditInvoiceModal
      v-if="selectedInvoice"
      :invoice="selectedInvoice"
      :is-open="showEditInvoiceModal"
      @close="closeEditInvoiceModal"
      @save="handleUpdateInvoice"
    />
    <PayInvoiceModal
      :show="showPayInvoiceModal"
      :invoice="selectedPaymentInvoice"
      @close="closePayInvoiceModal"
      @payment-recorded="handlePaymentRecorded"
    />
  </Teleport>
</template>

<script setup>
definePageMeta({
  middleware: ['auth']
})

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRuntimeConfig } from '#app'
import TablePageLayout from '~/components/TablePageLayout.vue'
import BaseButton from '~/components/BaseButton.vue'
import NewInvoiceModal from '~/components/NewInvoiceModal.vue'
import EditInvoiceModal from '~/components/EditInvoiceModal.vue'
import PayInvoiceModal from '~/components/PayInvoiceModal.vue'
import { Teleport } from 'vue'

const config = useRuntimeConfig()
const invoices = ref([])
const searchQuery = ref('')
const selectedStatus = ref('All')
const showNewInvoiceModal = ref(false)
const selectedInvoice = ref(null)
const selectedPaymentInvoice = ref(null)
const openOptionsForInvoice = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const showPayInvoiceModal = ref(false)
const showEditInvoiceModal = ref(false)

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (openOptionsForInvoice.value && !event.target.closest('.options-container')) {
    openOptionsForInvoice.value = null
  }
}

onMounted(() => {
  fetchInvoices()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Fetch invoices from the API
async function fetchInvoices() {
  try {
    isLoading.value = true
    errorMessage.value = ''

    const queryParams = new URLSearchParams()
    if (selectedStatus.value !== 'All') {
      queryParams.append('status', selectedStatus.value)
    }
    if (searchQuery.value) {
      queryParams.append('search', searchQuery.value)
    }

    const response = await fetch(`${config.public.apiBase}/api/invoices/list_invoices?${queryParams.toString()}`)
    if (!response.ok) {
      throw new Error('Failed to fetch invoices')
    }

    const data = await response.json()
    invoices.value = data.invoices
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error fetching invoices:', error)
  } finally {
    isLoading.value = false
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
  selectedInvoice.value = invoice
  openOptionsForInvoice.value = null
  showEditInvoiceModal.value = true
}

function closeEditInvoiceModal() {
  selectedInvoice.value = null
  showEditInvoiceModal.value = false
}

async function handleUpdateInvoice(updatedData) {
  try {
    const response = await fetch(`${config.public.apiBase}/api/invoices/update_invoice/${updatedData.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updatedData)
    })

    if (!response.ok) throw new Error('Failed to update invoice')

    await fetchInvoices()
    closeEditInvoiceModal()
  } catch (error) {
    errorMessage.value = error.message
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
    const response = await fetch(`${config.public.apiBase}/api/invoices/delete_invoice/${invoice.id}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      const data = await response.json();
      if (data.error_code === 'HAS_PAYMENTS') {
        alert(data.message);
        return;
      }
      throw new Error(data.message || 'Error deleting invoice');
    }

    // Remove invoice from list
    invoices.value = invoices.value.filter(inv => inv.id !== invoice.id);
    openOptionsForInvoice.value = null;
  } catch (error) {
    errorMessage.value = `Failed to delete invoice: ${error.message}`;
  }
}

async function voidInvoice(invoiceId) {
  if (!confirm('Are you sure you want to void this invoice? This action cannot be undone.')) return

  const reason = prompt('Please enter a reason for voiding this invoice:', 'User requested void')
  if (!reason) return // User cancelled the prompt

  try {
    const response = await fetch(`${config.public.apiBase}/api/invoices/void_invoice/${invoiceId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ reason })
    })

    const data = await response.json()
    
    if (!response.ok) {
      if (data.error_code === 'ALREADY_VOIDED') {
        errorMessage.value = data.message
      } else {
        throw new Error(data.message || 'Failed to void invoice')
      }
      return
    }

    await fetchInvoices()
    openOptionsForInvoice.value = null
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error voiding invoice:', error)
  }
}

async function postInvoice(invoiceId) {
  try {
    const response = await fetch(`${config.public.apiBase}/api/invoices/post_invoice/${invoiceId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to post invoice')
    }

    // Refresh invoices list
    await fetchInvoices()
    
  } catch (error) {
    console.error('Error posting invoice:', error)
    errorMessage.value = error.message
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
    const response = await fetch(`${config.public.apiBase}/api/invoices/create_invoice`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(invoiceData)
    })

    if (!response.ok) throw new Error('Failed to create invoice')

    await fetchInvoices()
    closeNewInvoiceModal()
  } catch (error) {
    errorMessage.value = error.message
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
  await fetchInvoices()
  showPayInvoiceModal.value = false
  selectedPaymentInvoice.value = null
}

// Watch for changes in search query or status to refresh invoices
watch([searchQuery, selectedStatus], () => {
  fetchInvoices()
})
</script>
