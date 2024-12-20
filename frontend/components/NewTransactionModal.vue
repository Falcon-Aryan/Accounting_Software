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
                <option value="payment">Payment</option>
                <option value="invoice">Invoice</option>
                <option value="bill">Bill</option>
                <option value="expense">Expense</option>
                <option value="journal">Journal</option>
                <option value="transfer">Transfer</option>
                <option value="other">Other</option>
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
                            v-for="account in accounts" 
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
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
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
import { useRuntimeConfig } from '#app'

const config = useRuntimeConfig()
const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'save'])

const errorMessage = ref('')
const accounts = ref([])
const formData = ref({
  date: new Date().toISOString().split('T')[0],
  transaction_type: 'other',
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

// Fetch accounts when component mounts
onMounted(async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/coa/list_accounts`)
    const data = await response.json()
    if (response.ok && data.accounts) {
      accounts.value = data.accounts.filter(acc => acc.active)
    }
  } catch (error) {
    console.error('Error fetching accounts:', error)
    errorMessage.value = 'Failed to load accounts'
  }
})

const totalDebits = computed(() => {
  return formData.value.entries
    .filter(e => e.type === 'debit')
    .reduce((sum, e) => sum + Number(e.amount), 0)
})

const totalCredits = computed(() => {
  return formData.value.entries
    .filter(e => e.type === 'credit')
    .reduce((sum, e) => sum + Number(e.amount), 0)
})

function addDualEntry() {
  // Add a debit-credit pair
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
  // Remove both debit and credit entries
  formData.value.entries.splice(index, 2)
}

function updatePairAmount(index) {
  // Update the corresponding pair amount
  const isDebit = formData.value.entries[index].type === 'debit'
  const pairIndex = isDebit ? index + 1 : index - 1
  if (formData.value.entries[pairIndex]) {
    formData.value.entries[pairIndex].amount = formData.value.entries[index].amount
  }
}

function close() {
  resetForm()
  emit('close')
}

function resetForm() {
  formData.value = {
    date: new Date().toISOString().split('T')[0],
    transaction_type: 'other',
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
  try {
    // Validate entries
    if (formData.value.entries.length === 0) {
      errorMessage.value = 'At least one entry pair is required'
      return
    }

    // Check if debits equal credits
    if (totalDebits.value !== totalCredits.value) {
      errorMessage.value = 'Total debits must equal total credits'
      return
    }

    // Emit save event with form data
    emit('save', { ...formData.value })
    close()
  } catch (error) {
    errorMessage.value = error.message
  }
}
</script>
