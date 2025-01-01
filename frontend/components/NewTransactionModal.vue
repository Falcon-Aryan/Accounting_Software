<template>
  <BaseNewFormModal
    :is-open="show"
    title="Create New Transaction"
    width="md"
    @close="close"
  >
    <form @submit.prevent="handleSubmit">
      <!-- Basic Info -->
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Date</label>
          <input 
            type="date" 
            v-model="formData.date"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Transaction Type</label>
          <select 
            v-model="formData.transaction_type"
            @change="handleTypeChange"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
          >
            <option value="">Select Type</option>
            <option v-for="type in transactionTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Sub Type</label>
          <select 
            v-model="formData.sub_type"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            :disabled="!formData.transaction_type"
          >
            <option value="">Select Sub Type</option>
            <option v-for="subType in availableSubTypes" :key="subType.value" :value="subType.value">
              {{ subType.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <input 
          type="text"
          v-model="formData.description"
          placeholder="Enter transaction description"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
        />
      </div>

      <!-- Entries -->
      <div class="mb-4">
        <div class="flex justify-between items-center mb-2">
          <label class="block text-sm font-medium text-gray-700">Entries</label>
          <button 
            type="button"
            @click="addDualEntry"
            class="px-3 py-1 text-sm text-green-600 hover:text-green-700 focus:outline-none"
          >
            Add Entry
          </button>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(entry, index) in formData.entries" :key="index">
                <td class="px-6 py-4">
                  <select
                    v-model="entry.accountId"
                    required
                    @change="handleAccountSelection(entry, index)"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
                  >
                    <option value="">Select Account</option>
                    <option 
                      v-for="account in getFilteredAccountOptions" 
                      :key="account.value" 
                      :value="account.value"
                    >
                      {{ account.label }}
                    </option>
                  </select>
                </td>
                <td class="px-6 py-4">
                  <div v-if="index < 2">
                    <span class="px-3 py-2 text-sm capitalize">{{ index === 0 ? 'debit' : 'credit' }}</span>
                  </div>
                  <select
                    v-else
                    v-model="entry.type"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
                  >
                    <option value="debit">Debit</option>
                    <option value="credit">Credit</option>
                  </select>
                </td>
                <td class="px-6 py-4">
                  <input
                    type="number"
                    v-model="entry.amount"
                    required
                    step="0.01"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
                    @input="updatePairAmount(index)"
                  />
                </td>
                <td class="px-6 py-4">
                  <input
                    type="text"
                    v-model="entry.description"
                    placeholder="Optional"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
                  />
                </td>
                <td class="px-6 py-4">
                  <button
                    type="button"
                    @click="removeDualEntry(index)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
        <p class="text-sm text-red-700">{{ errorMessage }}</p>
      </div>

      <!-- Form Actions -->
      <div class="flex justify-end space-x-3 mt-6">
        <button
          type="button"
          @click="close"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          Create Transaction
        </button>
      </div>
    </form>
  </BaseNewFormModal>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRuntimeConfig } from '#app'
import BaseNewFormModal from '~/components/BaseNewFormModal.vue'

const config = useRuntimeConfig()
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close', 'transaction-created'])

const errorMessage = ref('')
const accountsByType = ref({})
const accounts = ref([])
const formData = ref({
  date: new Date().toISOString().split('T')[0],
  transaction_type: '',
  sub_type: '',
  description: '',
  entries: [
    {
      accountId: '',
      accountName: '',
      type: 'debit',
      amount: 0,
      description: ''
    },
    {
      accountId: '',
      accountName: '',
      type: 'credit',
      amount: 0,
      description: ''
    }
  ]
})

const close = () => {
  emit('close')
  resetForm()
}

const resetForm = () => {
  formData.value = {
    date: new Date().toISOString().split('T')[0],
    transaction_type: '',
    sub_type: '',
    description: '',
    entries: [
      {
        accountId: '',
        accountName: '',
        type: 'debit',
        amount: 0,
        description: ''
      },
      {
        accountId: '',
        accountName: '',
        type: 'credit',
        amount: 0,
        description: ''
      }
    ]
  }
  errorMessage.value = ''
}

const transactionTypes = [
  { value: 'sale', label: 'Sale' },
  { value: 'purchase', label: 'Purchase' },
  { value: 'expense', label: 'Expense' },
  { value: 'income', label: 'Income' },
  { value: 'payment_received', label: 'Payment Received' },
  { value: 'payment_made', label: 'Payment Made' },
  { value: 'transfer', label: 'Transfer' },
  { value: 'adjustment', label: 'Adjustment' }
]

const subTypesByType = {
  'sale': [
    { value: 'product_sale', label: 'Product Sale' },
    { value: 'service_sale', label: 'Service Sale' }
  ],
  'purchase': [
    { value: 'product_purchase', label: 'Product Purchase' },
    { value: 'service_purchase', label: 'Service Purchase' }
  ],
  'expense': [
    { value: 'general_expense', label: 'General Expense' },
    { value: 'utility_expense', label: 'Utility Expense' }
  ],
  'income': [
    { value: 'interest_income', label: 'Interest Income' },
    { value: 'rental_income', label: 'Rental Income' },
    { value: 'other_income', label: 'Other Income' }
  ],
  'payment_received': [
    { value: 'customer_payment', label: 'Customer Payment' },
    { value: 'other_payment', label: 'Other Payment' }
  ],
  'payment_made': [
    { value: 'vendor_payment', label: 'Vendor Payment' },
    { value: 'other_payment', label: 'Other Payment' }
  ],
  'transfer': [
    { value: 'bank_transfer', label: 'Bank Transfer' },
    { value: 'asset_transfer', label: 'Asset Transfer' }
  ],
  'adjustment': [
    { value: 'inventory_adjustment', label: 'Inventory Adjustment' },
    { value: 'balance_adjustment', label: 'Balance Adjustment' }
  ]
}

const availableSubTypes = computed(() => {
  if (!formData.value.transaction_type) return []
  return subTypesByType[formData.value.transaction_type.toLowerCase()] || []
})

const validAccountTypes = {
  'sale': ['Accounts Receivable', 'Income', 'Bank', 'Other Current Asset'],
  'purchase': ['Accounts Payable', 'Other Current Asset', 'Expense', 'Bank'],
  'payment_received': ['Bank', 'Accounts Receivable'],
  'payment_made': ['Bank', 'Accounts Payable'],
  'expense': ['Expense', 'Bank', 'Credit Card'],
  'transfer': ['Bank', 'Other Current Asset'],
  'adjustment': ['Other Current Asset', 'Income', 'Expense'],
  'income': ['Bank', 'Other Current Asset', 'Income']
}

const getAccountOptions = computed(() => {
  const options = []
  for (const account of accounts.value) {
    options.push({
      value: account.id,
      label: account.name
    })
  }
  return options
})

const getFilteredAccountOptions = computed(() => {
  if (!formData.value.transaction_type) {
    return []
  }

  const validTypes = validAccountTypes[formData.value.transaction_type.toLowerCase()]
  if (!validTypes) {
    return []
  }

  return accounts.value
    .filter(account => validTypes.includes(account.accountType))
    .map(account => ({
      value: account.id,
      label: `${account.name} (${account.accountType})`
    }))
})

const loadAccountsByType = async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/coa/accounts_by_type`)
    if (!response.ok) {
      throw new Error('Failed to load accounts')
    }
    const data = await response.json()
    accountsByType.value = data.accounts_by_type || {}
    accounts.value = data.all_accounts || []
  } catch (error) {
    errorMessage.value = 'Failed to load accounts'
  }
}

const addDualEntry = () => {
  formData.value.entries.push(
    {
      accountId: '',
      accountName: '',
      type: 'debit',
      amount: 0,
      description: ''
    },
    {
      accountId: '',
      accountName: '',
      type: 'credit',
      amount: 0,
      description: ''
    }
  )
}

const removeDualEntry = (index) => {
  formData.value.entries.splice(index, 1)
}

const updatePairAmount = (index) => {
  const entry = formData.value.entries[index]
  const pairIndex = index % 2 === 0 ? index + 1 : index - 1
  if (formData.value.entries[pairIndex]) {
    formData.value.entries[pairIndex].amount = entry.amount
  }
}

const handleTypeChange = () => {
  formData.value.sub_type = ''
}

const handleAccountSelection = (entry, index) => {
  if (!entry.accountId) {
    entry.accountName = ''
    return
  }
  
  // Find the selected account from the options
  const selectedAccount = getAccountOptions.value.find(acc => acc.value === entry.accountId)
  if (selectedAccount) {
    // Set the account name
    entry.accountName = selectedAccount.label
  }
}

watch(() => formData.value.transaction_type, () => {
  formData.value.sub_type = ''
  // Clear account selections when transaction type changes
  formData.value.entries.forEach(entry => {
    entry.accountId = ''
    entry.description = ''
  })
})

const handleSubmit = async () => {
  try {
    // First validate the transaction
    const validateResponse = await fetch(`${config.public.apiBase}/api/transactions/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })

    if (!validateResponse.ok) {
      const error = await validateResponse.json()
      throw new Error(error.message || 'Validation failed')
    }

    // Then create the transaction
    const createResponse = await fetch(`${config.public.apiBase}/api/transactions/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })

    if (!createResponse.ok) {
      const error = await createResponse.json()
      throw new Error(error.message || 'Failed to create transaction')
    }

    const result = await createResponse.json()
    emit('transaction-created', result.transaction) // Emit the created transaction data
    close()
  } catch (error) {
    console.error('Transaction error:', error)
    errorMessage.value = error.message
  }
}

// Load accounts on mount
onMounted(() => {
  loadAccountsByType()
})
</script>
