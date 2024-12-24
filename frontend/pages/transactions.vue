<template>
  <TablePageLayout
    title="Transactions"
    :error-message="errorMessage"
    :is-loading="isLoading"
    :has-data="filteredTransactions.length > 0"
    :column-count="6"
    empty-state-message="No transactions found. Create a new transaction to get started."
  >
    <!-- Search Filter -->
    <template #filters>
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex-1 max-w-sm">
            <label for="search" class="sr-only">Search transactions</label>
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
                placeholder="Search transactions..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <select
              v-model="filters.status"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="posted">Posted</option>
              <option value="void">Void</option>
            </select>
            <BaseButton @click="openNewTransactionModal">
              New Transaction
            </BaseButton>
          </div>
        </div>
      </div>
    </template>

    <!-- Table Header -->
    <template #table-header>
      <tr>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          ID
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Date
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Description
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Status
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Amount
        </th>
        <th scope="col" class="relative px-6 py-3">
          <span class="sr-only">Actions</span>
        </th>
      </tr>
    </template>

    <!-- Table Body -->
    <template #table-body>
      <tr v-for="transaction in filteredTransactions" :key="transaction.id" class="even:bg-gray-50">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ transaction.id }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(transaction.date) }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ transaction.description }}</td>
        <td class="px-6 py-4 whitespace-nowrap">
          <StatusBadge :status="transaction.status" />
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatAmount(getTotalAmount(transaction)) }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
          <div class="relative inline-block text-left options-container">
            <button
              @click="(event) => toggleOptions(transaction.id, event)"
              class="text-indigo-600 hover:text-indigo-900 flex items-center"
            >
              Options
              <svg class="ml-2 -mr-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div 
              v-if="openOptionsForTransaction === transaction.id"
              class="absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
              @click.stop
            >
              <div class="py-1">
                <button
                  @click="viewTransactionDetails(transaction)"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  View Details
                </button>
              </div>
              <div class="py-1 border-t border-gray-100">
                <button
                  @click="postTransaction(transaction.id)"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  Post Transaction
                </button>
              </div>
              <div class="py-1 border-t border-gray-100">
                <button
                  @click="voidTransaction(transaction.id)"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  role="menuitem"
                >
                  Void Transaction
                </button>
              </div>
              <div class="py-1 border-t border-gray-100">
                <button
                  @click="deleteTransaction(transaction.id)"
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

  <!-- Transaction Details Modal -->
  <Teleport to="body">
    <TransactionDetailsModal
      v-if="selectedTransaction"
      :transaction="selectedTransaction"
      @close="selectedTransaction = null"
    />
    <NewTransactionModal
      v-if="showNewTransactionModal"
      :is-open="showNewTransactionModal"
      @close="closeNewTransactionModal"
      @save="handleCreateTransaction"
    />
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRuntimeConfig } from '#app'
import TablePageLayout from '~/components/TablePageLayout.vue'
import BaseButton from '~/components/BaseButton.vue'
import StatusBadge from '~/components/StatusBadge.vue'
import TransactionDetailsModal from '~/components/TransactionDetailsModal.vue'
import NewTransactionModal from '~/components/NewTransactionModal.vue'
import { Teleport } from 'vue'

const config = useRuntimeConfig()
const transactions = ref([])
const searchQuery = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const selectedTransaction = ref(null)
const openOptionsForTransaction = ref(null)
const showNewTransactionModal = ref(false)

const filters = ref({
  status: '',
  startDate: '',
  endDate: ''
})

// Filter transactions based on search query and status
const filteredTransactions = computed(() => {
  if (!transactions.value) return []
  
  let filtered = [...transactions.value]
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(trans => 
      (trans.id && trans.id.toString().toLowerCase().includes(query)) ||
      (trans.description && trans.description.toLowerCase().includes(query))
    )
  }
  
  // Filter by status
  if (filters.value.status) {
    filtered = filtered.filter(trans => 
      trans.status && trans.status.toLowerCase() === filters.value.status.toLowerCase()
    )
  }
  
  return filtered
})

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (openOptionsForTransaction.value && !event.target.closest('.options-container')) {
    openOptionsForTransaction.value = null
  }
}

onMounted(() => {
  fetchTransactions()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Fetch transactions
async function fetchTransactions() {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    const response = await fetch(`${config.public.apiBase}/api/transactions/list`)
    if (!response.ok) throw new Error('Failed to fetch transactions')
    
    const data = await response.json()
    transactions.value = data.transactions
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error fetching transactions:', error)
  } finally {
    isLoading.value = false
  }
}

// Format date
function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString('en-US', { dateStyle: 'short' });
}

// Format currency
function formatAmount(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

// Calculate total amount
function getTotalAmount(transaction) {
  return transaction.entries.reduce((total, entry) => {
    return total + (entry.type === 'debit' ? entry.amount : 0)
  }, 0)
}

// Toggle options dropdown
function toggleOptions(transactionId, event) {
  event.stopPropagation()
  openOptionsForTransaction.value = openOptionsForTransaction.value === transactionId ? null : transactionId
}

// View transaction details
function viewTransactionDetails(transaction) {
  selectedTransaction.value = transaction
  openOptionsForTransaction.value = null
}

// Post transaction
async function postTransaction(transactionId) {
  if (!confirm('Are you sure you want to post this transaction?')) return

  try {
    const response = await fetch(`${config.public.apiBase}/api/transactions/post/${transactionId}`, {
      method: 'POST'
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.message || 'Failed to post transaction')
    }

    await fetchTransactions()
    openOptionsForTransaction.value = null
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error posting transaction:', error)
  }
}

// Void transaction
async function voidTransaction(transactionId) {
  if (!confirm('Are you sure you want to void this transaction?')) return

  try {
    const response = await fetch(`${config.public.apiBase}/api/transactions/void/${transactionId}`, {
      method: 'POST'
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.message || 'Failed to void transaction')
    }

    await fetchTransactions()
    openOptionsForTransaction.value = null
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error voiding transaction:', error)
  }
}

// Delete transaction
async function deleteTransaction(transactionId) {
  if (!confirm('Are you sure you want to delete this transaction?')) return

  try {
    const response = await fetch(`${config.public.apiBase}/api/transactions/delete/${transactionId}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.message || 'Failed to delete transaction')
    }

    await fetchTransactions()
    openOptionsForTransaction.value = null
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error deleting transaction:', error)
  }
}

// Open new transaction modal
function openNewTransactionModal() {
  showNewTransactionModal.value = true
}

// Close new transaction modal
function closeNewTransactionModal() {
  showNewTransactionModal.value = false
}

// Handle create transaction
async function handleCreateTransaction(transactionData) {
  try {
    const response = await fetch(`${config.public.apiBase}/api/transactions/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(transactionData)
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.message || 'Failed to create transaction')
    }

    // Refresh transactions list and close modal
    await fetchTransactions()
    closeNewTransactionModal()
  } catch (error) {
    errorMessage.value = error.message
    console.error('Error creating transaction:', error)
  }
}

// Watch for filter changes
watch([filters, searchQuery], () => {
  // No need to fetch transactions here, as filtering is done locally
})
</script>
