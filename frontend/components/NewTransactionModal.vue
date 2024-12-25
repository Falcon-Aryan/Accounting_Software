<template>
  <div v-if="isOpen" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-[800px] shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Create New Transaction</h3>
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
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
              >
                <option value="" disabled>Select Type</option>
                <option value="invoice">Invoice</option>
                <option value="payment">Payment</option>
                <option value="journal">Journal Entry</option>
                <option value="reversal">Reversal</option>
              </select>
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
              <div class="flex gap-2">
                <button 
                  type="button"
                  @click="addDualEntry"
                  class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                >
                  Add Entry Pair
                </button>
                <button 
                  type="button"
                  @click="validateTransaction"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Validate
                </button>
              </div>
            </div>

            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
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
                        <div class="text-sm font-medium">
                          <span
                            :class="{
                              'px-2 py-1 rounded': true,
                              'bg-blue-100 text-blue-800': entry.type === 'debit',
                              'bg-purple-100 text-purple-800': entry.type === 'credit'
                            }"
                          >
                            {{ entry.type }}
                          </span>
                        </div>
                      </td>
                      <td class="px-6 py-4">
                        <input 
                          type="number"
                          v-model="entry.amount"
                          required
                          min="0"
                          step="0.01"
                          class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 text-right"
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
                <tfoot class="bg-gray-50 font-medium">
                  <tr>
                    <td colspan="3" class="px-6 py-3 text-right">Total Debits:</td>
                    <td class="px-6 py-3 text-right">{{ formatAmount(totalDebits) }}</td>
                    <td></td>
                  </tr>
                  <tr>
                    <td colspan="3" class="px-6 py-3 text-right">Total Credits:</td>
                    <td class="px-6 py-3 text-right">{{ formatAmount(totalCredits) }}</td>
                    <td></td>
                  </tr>
                  <tr>
                    <td colspan="3" class="px-6 py-3 text-right">Difference:</td>
                    <td 
                      class="px-6 py-3 text-right"
                      :class="isBalanced ? 'text-green-600' : 'text-red-600'"
                    >
                      {{ formatAmount(Math.abs(totalDebits - totalCredits)) }}
                    </td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p class="text-sm text-red-700">{{ errorMessage }}</p>
          </div>

          <!-- Form Actions -->
          <div class="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              @click="close"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="!isBalanced || !isValid"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Transaction
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { api } from '../utils/api'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'save'])
const toast = useToast()

const errorMessage = ref('')
const accounts = ref([])
const isValid = ref(true)

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

// Computed
const totalDebits = computed(() => {
  return formData.value.entries
    .filter(e => e.type === 'debit')
    .reduce((sum, e) => sum + (Number(e.amount) || 0), 0)
})

const totalCredits = computed(() => {
  return formData.value.entries
    .filter(e => e.type === 'credit')
    .reduce((sum, e) => sum + (Number(e.amount) || 0), 0)
})

const isBalanced = computed(() => {
  return Math.abs(totalDebits.value - totalCredits.value) < 0.01
})

// Methods
const loadAccounts = async () => {
  try {
    const response = await api.get('/chart-of-accounts/list')
    accounts.value = response.data
  } catch (error) {
    toast.error('Failed to load accounts')
    console.error('Error loading accounts:', error)
  }
}

const filteredAccounts = (type) => {
  // Filter accounts based on transaction type and entry type
  // This is a placeholder - implement actual filtering logic based on your requirements
  return accounts.value
}

const addDualEntry = () => {
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

const removeDualEntry = (index) => {
  if (formData.value.entries.length > 2) {
    formData.value.entries.splice(index, 2)
  } else {
    toast.warning('Transaction must have at least two entries')
  }
}

const updatePairAmount = (index) => {
  if (index % 2 === 0) {
    // Update the credit amount to match the debit
    const amount = Number(formData.value.entries[index].amount) || 0
    if (formData.value.entries[index + 1]) {
      formData.value.entries[index + 1].amount = amount
    }
  }
}

const validateTransaction = async () => {
  try {
    const response = await api.post('/transactions/validate', formData.value)
    if (response.data.is_valid) {
      isValid.value = true
      errorMessage.value = ''
      toast.success('Transaction is valid')
    } else {
      isValid.value = false
      errorMessage.value = response.data.error
      toast.error('Transaction validation failed')
    }
  } catch (error) {
    isValid.value = false
    errorMessage.value = 'Failed to validate transaction'
    toast.error('Failed to validate transaction')
    console.error('Error validating transaction:', error)
  }
}

const handleSubmit = async () => {
  errorMessage.value = ''

  if (!isBalanced.value) {
    errorMessage.value = 'Transaction must be balanced (debits must equal credits)'
    return
  }

  try {
    // Validate before submitting
    await validateTransaction()
    if (!isValid.value) return

    emit('save', formData.value)
  } catch (error) {
    errorMessage.value = 'Failed to create transaction'
    console.error('Error creating transaction:', error)
  }
}

const close = () => {
  resetForm()
  emit('close')
}

const resetForm = () => {
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
  isValid.value = true
}

// Lifecycle
onMounted(() => {
  loadAccounts()
})
</script>
