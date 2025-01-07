<template>
  <BaseNewFormModal
    :is-open="isOpen"
    title="Create New Transaction"
    width="xl"
    @close="close"
  >
    <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
      <p class="text-sm text-red-600">{{ errorMessage }}</p>
    </div>

    <form @submit.prevent="handleSubmit">
      <!-- Basic Info -->
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Transaction Type</label>
          <select
            v-model="formData.transaction_type"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            required
          >
            <option value="" disabled>Select Type</option>
            <option
              v-for="type in transactionTypes"
              :key="type.value"
              :value="type.value"
              :title="type.description"
            >
              {{ type.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Date</label>
          <input
            type="date"
            v-model="formData.date"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            required
          />
        </div>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <input 
          type="text"
          v-model="formData.description"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
          placeholder="Enter transaction description"
        />
      </div>

      <!-- Transaction Entries -->
      <div class="mb-4">
        <div class="flex justify-between items-center mb-2">
          <label class="block text-sm font-medium text-gray-700">Entries</label>
          <button 
            type="button"
            @click="addDualEntry"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
          >
            Add Entry Pair
          </button>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <template v-for="(entry, index) in formData.entries" :key="index">
                <tr :class="{ 'bg-gray-50': index % 4 === 2 || index % 4 === 3 }">
                  <td class="px-6 py-4">
                    <select 
                      v-model="entry.accountId"
                      required
                      class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                    >
                      <option value="" disabled>Select Account</option>
                      <option 
                        v-for="account in filteredAccounts(entry.type)" 
                        :key="account.id" 
                        :value="account.id"
                      >
                        {{ account.name }} ({{ account.id }})
                      </option>
                    </select>
                  </td>
                  <td class="px-6 py-4">
                    <input 
                      type="text"
                      v-model="entry.description"
                      class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      placeholder="Entry description"
                    />
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm font-medium" :class="entry.type === 'debit' ? 'text-blue-600' : 'text-green-600'">
                      {{ entry.type }}
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <input 
                      type="number"
                      v-model="entry.amount"
                      required
                      min="0"
                      step="0.01"
                      class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                      placeholder="0.00"
                      @input="updatePairAmount(index)"
                    />
                  </td>
                  <td class="px-6 py-4">
                    <button 
                      v-if="index % 2 === 0"
                      type="button"
                      @click="removeDualEntry(index)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Remove Pair
                    </button>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>

        <div class="mt-3 flex justify-end">
          <div class="text-right">
            <span class="text-sm font-medium text-gray-700">Total Debits: </span>
            <span class="text-lg font-semibold">{{ formatAmount(totalDebits) }}</span>
            <span class="text-sm font-medium text-gray-700 ml-4">Total Credits: </span>
            <span class="text-lg font-semibold">{{ formatAmount(totalCredits) }}</span>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton 
          type="button" 
          variant="secondary"
          @click="close"
        >
          Cancel
        </BaseButton>
        <BaseButton 
          type="submit"
          :disabled="!isValid"
        >
          Create Transaction
        </BaseButton>
      </div>
    </form>
  </BaseNewFormModal>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRuntimeConfig } from '#app'
import { getAuth } from 'firebase/auth'
import BaseNewFormModal from './BaseNewFormModal.vue'
import BaseButton from './BaseButton.vue'

definePageMeta({
  middleware: ['auth']
})

const config = useRuntimeConfig()
const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close', 'save'])

const errorMessage = ref('')
const accounts = ref([])
const accountNormalBalances = ref({})

const formData = ref({
  date: new Date().toISOString().split('T')[0],
  transaction_type: '',
  description: '',
  entries: [
    {
      accountId: '',
      description: '',
      type: 'debit',
      amount: 0
    },
    {
      accountId: '',
      description: '',
      type: 'credit',
      amount: 0
    }
  ]
})

const transactionTypes = [
  { value: 'sale', label: 'Sale', description: 'Sale of goods or services' },
  { value: 'purchase', label: 'Purchase', description: 'Purchase of goods or services' },
  { value: 'payment_received', label: 'Payment Received', description: 'Money received from customers' },
  { value: 'payment_made', label: 'Payment Made', description: 'Money paid to vendors' },
  { value: 'expense', label: 'Expense', description: 'Business expenses' },
  { value: 'equity', label: 'Equity', description: 'Owner investments or withdrawals' },
  { value: 'journal', label: 'Journal Entry', description: 'Manual journal entries' },
  { value: 'transfer', label: 'Transfer', description: 'Fund transfers between accounts' },
  { value: 'adjustment', label: 'Adjustment', description: 'Inventory or account adjustments' },
  { value: 'other', label: 'Other', description: 'Other transactions' }
]

const filteredAccounts = (entryType) => {
  if (!accounts.value.length) return []
  
  return accounts.value.filter(account => {
    // Must be active
    if (!account.active) return false

    // Get the normal balance type for this account type
    const normalBalanceType = accountNormalBalances.value[account.accountType]

    // For debit entries, prefer accounts with debit normal balance
    if (entryType === 'debit' && normalBalanceType === 'debit') return true

    // For credit entries, prefer accounts with credit normal balance
    if (entryType === 'credit' && normalBalanceType === 'credit') return true

    // For bank accounts and similar, allow both debit and credit
    if (['Bank', 'Credit Card', 'Other Current Asset'].includes(account.accountType)) return true

    return false
  })
}

// Computed properties for validation
const totalDebits = computed(() => {
  return formData.value.entries
    .filter(entry => entry.type === 'debit')
    .reduce((sum, entry) => sum + Number(entry.amount), 0)
})

const totalCredits = computed(() => {
  return formData.value.entries
    .filter(entry => entry.type === 'credit')
    .reduce((sum, entry) => sum + Number(entry.amount), 0)
})

const isValid = computed(() => {
  return totalDebits.value === totalCredits.value && 
         totalDebits.value > 0 &&
         formData.value.entries.every(entry => entry.accountId && entry.amount > 0)
})

// Fetch accounts when component mounts
onMounted(async () => {
  await Promise.all([
    fetchAccounts(),
    fetchNormalBalanceTypes()
  ])
})

async function fetchAccounts() {
  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/coa/list_accounts`, {
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    })
    
    const data = await response.json()
    if (response.ok) {
      accounts.value = data.accounts.filter(acc => acc.active)
    } else {
      errorMessage.value = data.message || 'Error fetching accounts'
    }
  } catch (error) {
    console.error('Error fetching accounts:', error)
    errorMessage.value = 'Failed to fetch accounts'
  }
}

async function fetchNormalBalanceTypes() {
  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/coa/normal_balance_types`, {
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    })
    
    const data = await response.json()
    if (response.ok) {
      accountNormalBalances.value = data.normal_balance_types
    }
  } catch (error) {
    console.error('Error fetching normal balance types:', error)
  }
}

function addDualEntry() {
  formData.value.entries.push(
    {
      accountId: '',
      description: '',
      type: 'debit',
      amount: 0
    },
    {
      accountId: '',
      description: '',
      type: 'credit',
      amount: 0
    }
  )
}

function removeDualEntry(index) {
  formData.value.entries.splice(index, 2)
}

function updatePairAmount(index) {
  // If this is a debit entry, update the corresponding credit
  if (index % 2 === 0) {
    formData.value.entries[index + 1].amount = formData.value.entries[index].amount
  } else {
    // If this is a credit entry, update the corresponding debit
    formData.value.entries[index - 1].amount = formData.value.entries[index].amount
  }
}

function close() {
  resetForm()
  emit('close')
}

function resetForm() {
  formData.value = {
    date: new Date().toISOString().split('T')[0],
    transaction_type: '',
    description: '',
    entries: [
      {
        accountId: '',
        description: '',
        type: 'debit',
        amount: 0
      },
      {
        accountId: '',
        description: '',
        type: 'credit',
        amount: 0
      }
    ]
  }
  errorMessage.value = ''
}

function formatAmount(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

async function handleSubmit() {
  if (!isValid.value) {
    errorMessage.value = 'Please ensure debits equal credits and all required fields are filled'
    return
  }

  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/transactions/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${idToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })
    
    const data = await response.json()
    if (response.ok) {
      emit('save', data.transaction)
      resetForm()
    } else {
      errorMessage.value = data.message || 'Failed to create transaction'
    }
  } catch (error) {
    console.error('Error submitting transaction:', error)
    errorMessage.value = error.message || 'Failed to create transaction'
  }
}

defineExpose({ resetForm, setError: (msg) => errorMessage.value = msg })
</script>