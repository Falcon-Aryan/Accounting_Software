<template>
  <TablePageLayout
    title="Transactions"
    :error-message="errorMessage"
    :is-loading="isLoading"
    :has-data="filteredTransactions.length > 0"
    :column-count="8"
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
              v-model="filters.type"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All Types</option>
              <option value="sale">Sale</option>
              <option value="purchase">Purchase</option>
              <option value="payment_received">Payment Received</option>
              <option value="payment_made">Payment Made</option>
              <option value="expense">Expense</option>
              <option value="journal">Journal</option>
              <option value="transfer">Transfer</option>
              <option value="adjustment">Adjustment</option>
              <option value="estimate">Estimate</option>
              <option value="invoice">Invoice</option>
            </select>
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
          Type
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Status
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Amount
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Payment Status
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Actions
        </th>
      </tr>
    </template>

    <!-- Table Body -->
    <template #table-body>
      <tr v-for="transaction in filteredTransactions" :key="transaction.id" class="even:bg-gray-50">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ transaction.id }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(transaction.date) }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ transaction.description }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" 
                :class="getTransactionTypeClass(transaction.transaction_type)">
            {{ formatTransactionType(transaction.transaction_type) }}
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <StatusBadge :status="transaction.status" />
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ formatAmount(getTotalAmount(transaction)) }}
        </td>
        <td v-if="transaction.reference_type === 'invoice' || transaction.reference_type === 'invoice_payment'" class="px-6 py-4 whitespace-nowrap">
          <div class="flex flex-col space-y-1">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                  :class="{
                    'bg-green-100 text-green-800': transaction.invoice_status === 'paid',
                    'bg-yellow-100 text-yellow-800': transaction.invoice_status === 'partially_paid',
                    'bg-gray-100 text-gray-800': !transaction.invoice_status || transaction.invoice_status === 'unknown'
                  }">
              {{ transaction.invoice_status ? transaction.invoice_status.replace('_', ' ') : 'N/A' }}
            </span>
            <div v-if="transaction.invoice_total" class="text-xs text-gray-500">
              <div>Total: {{ formatAmount(transaction.invoice_total) }}</div>
              <div>Paid: {{ formatAmount(transaction.invoice_paid || 0) }}</div>
              <div>Balance: {{ formatAmount(transaction.invoice_balance || 0) }}</div>
              <div v-if="transaction.last_payment_date" class="text-xs text-gray-400">
                Last Payment: {{ formatDate(transaction.last_payment_date) }}
              </div>
            </div>
          </div>
        </td>
        <td v-else class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          -
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
      :show="!!selectedTransaction"
      :transaction="selectedTransaction"
      @close="selectedTransaction = null"
    />
  </Teleport>

  <!-- New Transaction Modal -->
  <Teleport to="body">
    <NewTransactionModal
      v-if="showNewTransactionModal"
      :show="showNewTransactionModal"
      @close="closeNewTransactionModal"
      @transaction-created="handleTransactionCreated"
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

const config = useRuntimeConfig()
const transactions = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const selectedTransaction = ref(null)
const showNewTransactionModal = ref(false)
const openOptionsForTransaction = ref(null)
const searchQuery = ref('')
const filters = ref({
  status: '',
  type: ''
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
  
  // Filter by type
  if (filters.value.type) {
    filtered = filtered.filter(trans => 
      trans.transaction_type && trans.transaction_type.toLowerCase() === filters.value.type.toLowerCase()
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
  if (!transaction || !transaction.entries || transaction.entries.length === 0) {
    return 0
  }

  // Find the first debit entry which represents the actual transaction amount
  const firstDebitEntry = transaction.entries.find(entry => entry.type === 'debit')
  return firstDebitEntry ? firstDebitEntry.amount : 0
}

// Get transaction type class
function getTransactionTypeClass(type) {
  if (!type) return 'bg-gray-100 text-gray-800'
  
  switch (type.toLowerCase()) {
    case 'sale':
      return 'bg-green-100 text-green-800'
    case 'purchase':
      return 'bg-blue-100 text-blue-800'
    case 'payment_received':
      return 'bg-emerald-100 text-emerald-800'
    case 'payment_made':
      return 'bg-indigo-100 text-indigo-800'
    case 'expense':
      return 'bg-red-100 text-red-800'
    case 'journal':
      return 'bg-purple-100 text-purple-800'
    case 'transfer':
      return 'bg-cyan-100 text-cyan-800'
    case 'adjustment':
      return 'bg-amber-100 text-amber-800'
    case 'estimate':
      return 'bg-sky-100 text-sky-800'
    case 'invoice':
      return 'bg-lime-100 text-lime-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Format transaction type
function formatTransactionType(type) {
  if (!type) return 'Unknown'
  
  const typeMap = {
    'sale': 'Sale',
    'purchase': 'Purchase',
    'payment_received': 'Payment Received',
    'payment_made': 'Payment Made',
    'expense': 'Expense',
    'journal': 'Journal Entry',
    'transfer': 'Transfer',
    'adjustment': 'Adjustment',
    'estimate': 'Estimate',
    'invoice': 'Invoice',
    'other': 'Other'
  }
  
  return typeMap[type.toLowerCase()] || 'Unknown'
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
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        reason: 'User requested void'
      })
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
const openNewTransactionModal = () => {
  console.log('Opening modal')  // Debug log
  showNewTransactionModal.value = true
}

// Close new transaction modal
const closeNewTransactionModal = () => {
  console.log('Closing modal')  // Debug log
  showNewTransactionModal.value = false
}

// Handle transaction creation
const handleTransactionCreated = async (transaction) => {
  console.log('Transaction created:', transaction)
  // Add the new transaction to the list immediately
  transactions.value = [...transactions.value, transaction]
  // Then refresh the full list from the server
  await fetchTransactions()
  closeNewTransactionModal()
}

// Watch for filter changes
watch([filters, searchQuery], () => {
  // No need to fetch transactions here, as filtering is done locally
})
</script>
