<template>
  <div v-if="isOpen" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-[800px] shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Edit Item</h3>
        <form @submit.prevent="handleSubmit">
          <!-- Basic Information -->
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
              <input
                v-model="form.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
              <input
                :value="formatType(form.type)"
                type="text"
                disabled
                class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
              <p class="mt-1 text-sm text-gray-500">Type cannot be changed after creation</p>
            </div>
          </div>

          <!-- SKU and Price -->
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">SKU</label>
              <input
                v-model="form.sku"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Unit Price</label>
              <input
                v-model="form.unit_price"
                type="number"
                step="0.01"
                min="0"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
              />
            </div>
          </div>

          <!-- Description -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            ></textarea>
          </div>

          <!-- Sales Information -->
          <div class="mb-4 p-4 bg-gray-50 rounded-md">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-medium text-gray-700">Sales Information</h4>
              <label class="flex items-center">
                <input
                  v-model="form.sell_enabled"
                  type="checkbox"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-600">Enable for Sales</span>
              </label>
            </div>
            <div v-if="form.sell_enabled">
              <label class="block text-sm font-medium text-gray-700 mb-2">Income Account</label>
              <select
                v-model="form.income_account_id"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
              >
                <option value="" disabled>Select an account</option>
                <template v-if="form.type === 'service'">
                  <option v-for="account in serviceIncomeAccounts" :key="account.id" :value="account.id">
                    {{ account.name }} --- {{ account.detailType }} --- {{ account.accountType }}
                  </option>
                </template>
                <template v-else>
                  <option v-for="account in incomeAccounts" :key="account.id" :value="account.id">
                    {{ account.name }} --- {{ account.detailType }} --- {{ account.accountType }}
                  </option>
                </template>
              </select>
            </div>
          </div>

          <!-- Purchase Information -->
          <div class="mb-4 p-4 bg-gray-50 rounded-md">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-medium text-gray-700">Purchase Information</h4>
              <label class="flex items-center">
                <input
                  v-model="form.purchase_enabled"
                  type="checkbox"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-600">Enable for Purchases</span>
              </label>
            </div>
            <div v-if="form.purchase_enabled">
              <label class="block text-sm font-medium text-gray-700 mb-2">Expense Account</label>
              <select
                v-model="form.expense_account_id"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
              >
                <option value="" disabled>Select an account</option>
                <template v-if="form.type === 'service'">
                  <option v-for="account in serviceExpenseAccounts" :key="account.id" :value="account.id">
                    {{ account.name }} --- {{ account.detailType }} --- {{ account.accountType }}
                  </option>
                </template>
                <template v-else>
                  <option v-for="account in cogsAccounts" :key="account.id" :value="account.id">
                    {{ account.name }} --- {{ account.detailType }} --- {{ account.accountType }}
                  </option>
                </template>
              </select>
            </div>
          </div>

          <!-- Inventory Information (if type is inventory_item) -->
          <div v-if="form.type === 'inventory_item'" class="mb-4 p-4 bg-gray-50 rounded-md">
            <h4 class="text-sm font-medium text-gray-700 mb-3">Inventory Information</h4>
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                <input
                  v-model="form.inventory_info.quantity"
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">As of Date</label>
                <input
                  v-model="form.inventory_info.as_of_date"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Inventory Asset Account</label>
              <select
                v-model="form.inventory_info.inventory_asset_account_id"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
              >
                <option value="" disabled>Select an account</option>
                <option v-for="account in inventoryAssetAccounts" :key="account.id" :value="account.id">
                  {{ account.name }} --- {{ account.detailType }} --- {{ account.accountType }}
                </option>
              </select>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="close"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'
import { useRuntimeConfig } from '#app'

const config = useRuntimeConfig()

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  item: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'update'])

// Account refs
const incomeAccounts = ref([])
const serviceIncomeAccounts = ref([])
const serviceExpenseAccounts = ref([])
const cogsAccounts = ref([])
const inventoryAssetAccounts = ref([])

// Account type constants
const SERVICE_ACCOUNT_TYPES = [
  'Income',
  'Other Income',
  'Other Current Liability',
  'Expense',
  'Other Expense',
  'Cost of Goods Sold'
]

const form = ref({
  id: '',
  name: '',
  type: '',
  sku: '',
  unit_price: '',
  description: '',
  sell_enabled: true,
  purchase_enabled: false,
  income_account_id: '',
  expense_account_id: '',
  inventory_info: {
    quantity: 0,
    as_of_date: new Date().toISOString().split('T')[0],
    inventory_asset_account_id: ''
  }
})

// Load accounts on component mount
onMounted(async () => {
  try {
    // Get all accounts
    const accountsResponse = await axios.get(`${config.public.apiBase}/api/coa/list_accounts`)
    const accounts = accountsResponse.data.accounts || []
    
    // Filter income accounts for inventory items - only Sales Revenue and Sales of Product Income
    incomeAccounts.value = accounts.filter(acc => 
      acc.active && 
      acc.accountType === 'Income' && 
      (acc.name.toLowerCase().includes('sales revenue') || 
       acc.name.toLowerCase().includes('sales of product income'))
    )

    // Filter accounts for service items
    serviceIncomeAccounts.value = accounts.filter(acc => 
      SERVICE_ACCOUNT_TYPES.includes(acc.accountType) && 
      acc.active
    )

    // Filter accounts for service expense
    serviceExpenseAccounts.value = accounts.filter(acc => 
      SERVICE_ACCOUNT_TYPES.includes(acc.accountType) && 
      acc.active
    )

    // Filter Cost of Goods Sold accounts only
    cogsAccounts.value = accounts.filter(acc => 
      acc.accountType === 'Cost of Goods Sold' && 
      acc.active
    )

    // Filter Inventory Asset accounts
    inventoryAssetAccounts.value = accounts.filter(acc => 
      acc.detailType === 'Inventory' && 
      acc.active
    )
  } catch (error) {
    console.error('Error loading accounts:', error)
  }
})

// Watch for changes in the item prop and update form
watch(() => props.item, (newItem) => {
  if (newItem) {
    form.value = { ...newItem }
    if (!form.value.inventory_info) {
      form.value.inventory_info = {
        quantity: 0,
        as_of_date: new Date().toISOString().split('T')[0],
        inventory_asset_account_id: ''
      }
    }
    // Set account IDs based on type
    if (form.value.type === 'inventory_item') {
      if (!form.value.income_account_id || form.value.income_account_id === 'Sales of Product Income') {
        form.value.income_account_id = '4000-0001' // Sales Revenue ID
      }
      if (!form.value.expense_account_id || form.value.expense_account_id === 'Cost of Goods Sold') {
        form.value.expense_account_id = '5000-0001' // COGS ID
      }
    } else {
      if (!form.value.income_account_id) {
        form.value.income_account_id = '4000-0001' // Sales Revenue ID
      }
      if (!form.value.expense_account_id) {
        form.value.expense_account_id = '6004-0001' // Purchases ID
      }
    }
  }
}, { immediate: true })

const formatType = (type) => {
  if (!type) return ''
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const close = () => {
  emit('close')
}

const handleSubmit = () => {
  const formData = { ...form.value }
  
  // Remove inventory info if not an inventory item
  if (formData.type !== 'inventory_item') {
    delete formData.inventory_info
  }
  
  // Remove account IDs if not enabled
  if (!formData.sell_enabled) {
    delete formData.income_account_id
  }
  if (!formData.purchase_enabled) {
    delete formData.expense_account_id
  }
  
  emit('update', formData)
}
</script>
