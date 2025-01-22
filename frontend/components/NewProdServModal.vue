<template>
  <BaseNewFormModal
    :is-open="isOpen"
    title="Create New Product/Service"
    width="md"
    @close="close"
  >
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
          <select
            v-model="form.type"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
          >
            <option value="" disabled>Select a type</option>
            <option value="service">Service</option>
            <option value="inventory_item">Inventory Item</option>
          </select>
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
              <option v-for="account in inventoryIncomeAccounts" :key="account.id" :value="account.id">
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
              <option v-for="account in inventoryExpenseAccounts" :key="account.id" :value="account.id">
                {{ account.name }} --- {{ account.detailType }} --- {{ account.accountType }}
              </option>
            </template>
          </select>
        </div>
      </div>

      <!-- Inventory Information -->
      <div v-if="form.type === 'inventory_item'" class="mb-4 p-4 bg-gray-50 rounded-md">
        <h4 class="text-sm font-medium text-gray-700 mb-3">Inventory Information</h4>
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Cost Price</label>
            <input
              v-model.number="form.cost_price"
              type="number"
              min="0"
              :max="form.unit_price"
              step="0.01"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            />
            <p v-if="showCostPriceError" class="mt-1 text-sm text-red-600">
              Cost price must be lower than unit price
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
            <input
              v-model="form.inventory_info.quantity"
              type="number"
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">As of Date</label>
            <input
              v-model="form.inventory_info.as_of_date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            />
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
          Create Item
        </button>
      </div>
    </form>
  </BaseNewFormModal>
</template>

<style scoped>
.account-option {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  padding-right: 8px;
}

.account-type {
  color: #6B5B4E;
  text-align: right;
}
</style>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { useRuntimeConfig } from '#app'
import { getAuth } from 'firebase/auth'
import BaseNewFormModal from '~/components/BaseNewFormModal.vue'

const config = useRuntimeConfig()
const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close', 'create'])

// Account type constants
const INCOME_ACCOUNT_TYPES = [
  'Income',
  'Other Income'
]

const EXPENSE_ACCOUNT_TYPES = [
  'Expense',
  'Other Expense',
  'Cost of Goods Sold'
]

const INVENTORY_ACCOUNT_TYPES = [
  'Other Current Asset',
]

// Account refs
const serviceIncomeAccounts = ref([])
const serviceExpenseAccounts = ref([])
const inventoryIncomeAccounts = ref([])
const inventoryExpenseAccounts = ref([])
const inventoryAssetAccounts = ref([])

// Load accounts on component mount
onMounted(async () => {
  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()

    const accountsResponse = await axios.get(`${config.public.apiBase}/api/coa/list_accounts`, {
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    })
    const accounts = accountsResponse.data.accounts || []

    // Filter accounts for service items
    serviceIncomeAccounts.value = accounts.filter(acc => 
      INCOME_ACCOUNT_TYPES.includes(acc.accountType) && 
      acc.active
    )

    // Filter accounts for service expense
    serviceExpenseAccounts.value = accounts.filter(acc => 
      EXPENSE_ACCOUNT_TYPES.includes(acc.accountType) && 
      acc.active
    )

    // Filter accounts for inventory items
    inventoryIncomeAccounts.value = accounts.filter(acc => 
      INCOME_ACCOUNT_TYPES.includes(acc.accountType) && 
      acc.active
    )

    // Filter Cost of Goods Sold accounts
    inventoryExpenseAccounts.value = accounts.filter(acc => 
    EXPENSE_ACCOUNT_TYPES.includes(acc.accountType) && 
    acc.active
    )

    // Filter Inventory Asset accounts
    inventoryAssetAccounts.value = accounts.filter(acc => 
      INVENTORY_ACCOUNT_TYPES.includes(acc.accountType) && 
      acc.active
    )

    // Set initial type if not set
    if (!form.value.type) {
      form.value.type = 'service'
      handleTypeChange()
    }
  } catch (error) {
    console.error('Error loading accounts:', error)
  }
})

const form = ref({
  name: '',
  type: '',
  sku: '',
  unit_price: 0,
  cost_price: null,
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

const handleTypeChange = () => {
  if (form.value.type === 'inventory_item') {
    form.value.sell_enabled = true
    form.value.purchase_enabled = true
    form.value.income_account_id = '4000-0001' // Sales Revenue ID
    form.value.expense_account_id = '5000-0001' // COGS ID
  } else {
    form.value.sell_enabled = true
    form.value.purchase_enabled = false
    form.value.income_account_id = '4000-0001' // Sales Revenue ID
    form.value.expense_account_id = ''
  }
}

// Watch for type changes
watch(() => form.value.type, (newType) => {
  if (newType) {
    handleTypeChange()
  }
})

// Watch for purchase_enabled changes
watch(() => form.value.purchase_enabled, (enabled) => {
  if (!enabled) {
    form.value.expense_account_id = ''
  }
})

const close = () => {
  emit('close')
  resetForm()
}

const resetForm = () => {
  form.value = {
    name: '',
    type: '',
    sku: '',
    unit_price: 0,
    cost_price: null,
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
  }
}

const showCostPriceError = computed(() => {
  return form.value.type === 'inventory_item' && 
         form.value.cost_price !== null && 
         form.value.cost_price >= form.value.unit_price
})

const handleSubmit = () => {
  const formData = { ...form.value }
  
  if (formData.sku) {
    formData.sku = `SKU-${formData.sku}`
  }

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
  
  emit('create', formData)
  resetForm()
}
</script>