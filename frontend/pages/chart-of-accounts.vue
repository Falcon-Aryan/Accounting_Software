<template>
  <TablePageLayout
    title="Chart of Accounts"
    :error-message="errorMessage"
    :is-loading="isLoading"
    :has-data="filteredAccounts.length > 0"
    :column-count="6"
    empty-state-message="No accounts found. Create a new account to get started."
  >
    <!-- Header Actions -->
    <template #header-actions>
    </template>

    <!-- Search Filter -->
    <template #filters>
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex-1 max-w-sm">
            <label for="search" class="sr-only">Search accounts</label>
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
                placeholder="Search accounts..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <select
              v-model="selectedType"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="All">All</option>
              <option v-for="type in accountTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
            <BaseButton @click="openNewAccountModal">
              New Account
            </BaseButton>
          </div>
        </div>
      </div>
    </template>

    <!-- Table Header -->
    <template #table-header>
      <tr>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Account ID
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Name
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Type
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Detail Type
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Balance
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Actions
        </th>
      </tr>
    </template>

    <!-- Table Body -->
    <template #table-body>
      <tr v-for="account in filteredAccounts" :key="account.id" class="even:bg-gray-50">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ account.id }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
          {{ account.name }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ account.accountType }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ account.detailType }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          <div>Opening: {{ formatCurrency(account.openingBalance || 0) }}</div>
          <div>Current: {{ formatCurrency(account.quickbooksBalance || 0) }}</div>
          <span
            :class="[
              'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
              account.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            ]"
          >
            {{ account.active ? 'Active' : 'Inactive' }}
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
          <div class="relative inline-block text-left">
            <button
              @click="toggleOptions(account.id)"
              class="text-indigo-600 hover:text-indigo-900 flex items-center"
            >
              Options
              <svg class="ml-2 -mr-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div 
              v-if="openOptionsId === account.id"
              class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
              style="right: 0;"
              @click.stop
            >
              <div class="flex flex-col" role="menu">
                <div class="py-1">
                  <button
                    @click="editAccount(account)"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    Edit
                  </button>
                </div>
                <div class="py-1 border-t border-gray-100">
                  <button
                    @click="viewReport(account)"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    View Report
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
      <NewAccountModal
        :is-open="isNewAccountModalOpen"
        :account-types="Object.keys(detailTypes)"
        :detail-types="detailTypes"
        @close="closeNewAccountModal"
        @save="handleNewAccount"
      />
      <EditAccountModal
        :is-open="isEditAccountModalOpen"
        :account="selectedAccount"
        :account-types="Object.keys(detailTypes)"
        :detail-types="detailTypes"
        @close="closeEditAccountModal"
        @save="handleEditAccount"
        @delete="handleDeleteAccount"
      />
    </template>
  </TablePageLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRuntimeConfig } from '#app'
import TablePageLayout from '../components/TablePageLayout.vue'
import BaseButton from '../components/BaseButton.vue'
import NewAccountModal from '../components/NewAccountModal.vue'
import EditAccountModal from '../components/EditAccountModal.vue'

// Account types from backend ACCOUNT_TYPE_DETAILS
const accountTypes = [
  'Bank',
  'Accounts Receivable',
  'Other Current Asset',
  'Fixed Asset',
  'Other Asset',
  'Accounts payable',
  'Credit Card',
  'Other Current Liability',
  'Long Term Liabilities',
  'Equity',
  'Income',
  'Other Income',
  'Cost of Goods Sold',
  'Expense',
  'Other Expense'
]

// Detail types mapping from backend
const detailTypes = {
  'Bank': ['Cash on hand', 'Checking', 'Money Market', 'Rents Held in Trust', 'Savings', 'Trust account'],
  'Accounts Receivable': ['Accounts Receivable (A/R)'],
  'Other Current Asset': [
    'Allowance for Bad Debts', 'Development Costs', 'Employee Cash Advances',
    'Inventory', 'Investment - Mortgage/Real Estate Loans', 'Investment - Tax-Exempt Securities',
    'Investment - U.S. Government Obligations', 'Investments - Other', 'Loans To Officers',
    'Loans to Others', 'Loans to Stockholders', 'Other Current Assets', 'Prepaid Expenses',
    'Retainage', 'Undeposited Funds'
  ],
  'Fixed Asset': [
    'Accumulated Amortization', 'Accumulated Depletion', 'Accumulated Depreciation',
    'Buildings', 'Depletable Assets', 'Fixed Asset Computers', 'Fixed Asset Copiers',
    'Fixed Asset Furniture', 'Fixed Asset Other Tools Equipment', 'Fixed Asset Phone',
    'Fixed Asset Photo Video', 'Fixed Asset Software', 'Furniture & Fixtures',
    'Intangible Assets', 'Land', 'Leasehold Improvements', 'Machinery & Equipment',
    'Other fixed assets', 'Vehicles'
  ],
  'Other Asset': [
    'Accumulated Amortization of Other Assets', 'Goodwill', 'Lease Buyout', 'Licenses',
    'Organizational Costs', 'Other Long-term Assets', 'Security Deposits'
  ],
  'Accounts payable': ['Accounts Payable (A/P)'],
  'Credit Card': ['Credit Card'],
  'Other Current Liability': [
    'Deferred Revenue', 'Federal Income Tax Payable', 'Insurance Payable',
    'Line of Credit', 'Loan Payable', 'Other Current Liabilities', 'Payroll Clearing',
    'Payroll Tax Payable', 'Prepaid Expenses Payable', 'Rents in trust - Liability',
    'Sales Tax Payable', 'State/Local Income Tax Payable', 'Trust Accounts - Liabilities',
    'Undistributed Tips'
  ],
  'Long Term Liabilities': [
    'Notes Payable', 'Other Long Term Liabilities', 'Shareholder Notes Payable'
  ],
  'Equity': [
    'Accumulated Adjustment', 'Common Stock', 'Estimated Taxes', 'Health Insurance Premium',
    'Health Savings Account Contribution', 'Opening Balance Equity', 'Owner\'s Equity',
    'Paid-In Capital or Surplus', 'Partner Contributions', 'Partner Distributions',
    'Partner\'s Equity', 'Personal Expense', 'Personal Income', 'Preferred Stock',
    'Retained Earnings', 'Treasury Stock'
  ],
  'Income': [
    'Discounts/Refunds Given', 'Non-Profit Income', 'Other Primary Income',
    'Sales of Product Income', 'Service/Fee Income', 'Unapplied Cash Payment Income'
  ],
  'Other Income': [
    'Dividend Income', 'Interest Earned', 'Other Investment Income',
    'Other Miscellaneous Income', 'Tax-Exempt Interest'
  ],
  'Cost of Goods Sold': [
    'Cost of labor - COS', 'Equipment Rental - COS', 'Other Costs of Services - COS',
    'Shipping, Freight & Delivery - COS', 'Supplies & Materials - COGS'
  ],
  'Expense': [
    'Advertising/Promotional', 'Auto', 'Bad Debts', 'Bank Charges', 'Charitable Contributions',
    'Communication', 'Cost of Labor', 'Dues & subscriptions', 'Entertainment',
    'Entertainment Meals', 'Equipment Rental', 'Finance costs', 'Insurance', 'Interest Paid',
    'Legal & Professional Fees', 'Office/General Administrative Expenses',
    'Other Business Expenses', 'Other Miscellaneous Service Cost', 'Payroll Expenses',
    'Payroll Tax Expenses', 'Payroll Wage Expenses', 'Promotional Meals',
    'Rent or Lease of Buildings', 'Repair & Maintenance', 'Shipping, Freight & Delivery',
    'Supplies & Materials', 'Taxes Paid', 'Travel', 'Travel Meals',
    'Unapplied Cash Bill Payment Expense', 'Utilities'
  ],
  'Other Expense': [
    'Amortization', 'Depreciation', 'Exchange Gain or Loss', 'Gas And Fuel', 'Home Office',
    'Homeowner Rental Insurance', 'Mortgage Interest Home Office', 'Other Home Office Expenses',
    'Other Miscellaneous Expense', 'Other Vehicle Expenses', 'Parking and Tolls',
    'Penalties & Settlements', 'Property Tax Home Office', 'Rent and Lease Home Office',
    'Repairs and Maintenance Home Office', 'Utilities Home Office', 'Vehicle',
    'Vehicle Insurance', 'Vehicle Lease', 'Vehicle Loan', 'Vehicle Loan Interest',
    'Vehicle Registration', 'Vehicle Repairs', 'Wash and Road Services'
  ]
}

const config = useRuntimeConfig()

const selectedType = ref('All')
const accounts = ref([])
const isLoading = ref(true)
const isNewAccountModalOpen = ref(false)
const errorMessage = ref('')
const openOptionsId = ref(null)
const isEditAccountModalOpen = ref(false)
const selectedAccount = ref(null)
const searchQuery = ref('')

async function fetchAccounts() {
  try {
    const config = useRuntimeConfig()
    isLoading.value = true
    const response = await fetch(`${config.public.apiBase}/api/coa/list_accounts`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    accounts.value = data.accounts || []
    errorMessage.value = ''
  } catch (error) {
    console.error('Error fetching accounts:', error)
    errorMessage.value = 'Failed to load accounts. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const filteredAccounts = computed(() => {
  if (!accounts.value) return []
  
  let filtered = accounts.value
  
  if (selectedType.value !== 'All') {
    filtered = filtered.filter(account => account.accountType === selectedType.value)
  }
  
  if (searchQuery.value) {
    filtered = filtered.filter(account => account.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  
  return filtered
})

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(amount)
}

function openNewAccountModal() {
  isNewAccountModalOpen.value = true
}

function closeNewAccountModal() {
  isNewAccountModalOpen.value = false
}

function toggleOptions(accountId) {
  if (openOptionsId.value === accountId) {
    openOptionsId.value = null
  } else {
    openOptionsId.value = accountId
  }
}

function editAccount(account) {
  selectedAccount.value = account
  isEditAccountModalOpen.value = true
  openOptionsId.value = null
}

function closeEditAccountModal() {
  isEditAccountModalOpen.value = false
  selectedAccount.value = null
}

function viewReport(account) {
  openOptionsId.value = null
  console.log('View Report:', account.id)
}

async function handleNewAccount(accountData) {
  try {
    const response = await fetch(`${config.public.apiBase}/api/coa/create_account`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(accountData)
    })
    
    console.log('Response status:', response.status);
    
    if (response.status === 409) {
      errorMessage.value = 'An account with this name already exists'
      return
    }
    
    if (!response.ok) {
      const error = await response.json()
      console.error('Error response:', error);
      errorMessage.value = error.error || 'Failed to create account'
      return
    }
    
    const result = await response.json();
    console.log('Created account:', result);
    
    await fetchAccounts()
    errorMessage.value = ''
    closeNewAccountModal()
  } catch (error) {
    console.error('Error creating account:', error)
    errorMessage.value = error.message || 'An unexpected error occurred'
  }
}

async function handleEditAccount(accountData) {
  try {
    const response = await fetch(`${config.public.apiBase}/api/coa/update/${accountData.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(accountData)
    })
    
    if (!response.ok) {
      throw new Error('Failed to update account')
    }
    
    await fetchAccounts() // Refresh the accounts list
    closeEditAccountModal()
  } catch (error) {
    console.error('Error updating account:', error)
    errorMessage.value = 'Failed to update account. Please try again.'
  }
}

async function handleDeleteAccount(accountId) {
  try {
    const response = await fetch(`${config.public.apiBase}/api/coa/delete/${accountId}`, {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      throw new Error('Failed to delete account')
    }
    
    await fetchAccounts() // Refresh the accounts list
    closeEditAccountModal()
  } catch (error) {
    console.error('Error deleting account:', error)
    errorMessage.value = 'Failed to delete account. Please try again.'
  }
}

onMounted(() => {
  fetchAccounts()
  
  // Close dropdown when clicking outside
  document.addEventListener('click', (event) => {
    const target = event.target
    if (!target.closest('.relative')) {
      openOptionsId.value = null
    }
  })
})
</script>
