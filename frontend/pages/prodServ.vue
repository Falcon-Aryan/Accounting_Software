<template>
  <TablePageLayout
    title="Products & Services"
    :error-message="errorMessage"
    :is-loading="isLoading"
    :has-data="filteredItems.length > 0"
    :column-count="6"
    empty-state-message="No products or services found. Create a new item to get started."
  >
    <!-- Search Filter -->
    <template #filters>
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex-1 max-w-sm">
            <label for="search" class="sr-only">Search products & services</label>
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
                placeholder="Search by name, SKU, or description..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <select
              v-model="selectedType"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="All">All Types</option>
              <option value="service">Service</option>
              <option value="inventory_item">Inventory Item</option>
            </select>
            <BaseButton @click="openNewItemModal">
              New Product or Service
            </BaseButton>
          </div>
        </div>
      </div>
    </template>

    <!-- Table Header -->
    <template #table-header>
      <tr>
        <th scope="col" class="px-4 py-3 text-middle text-xs font-medium text-gray-500 uppercase tracking-wider">
          Name
        </th>
        <th scope="col" class="px-4 py-3 text-middle text-xs font-medium text-gray-500 uppercase tracking-wider">
          Type
        </th>
        <th scope="col" class="px-4 py-3 text-middle text-xs font-medium text-gray-500 uppercase tracking-wider">
          SKU
        </th>
        <th scope="col" class="px-4 py-3 text-middle text-xs font-medium text-gray-500 uppercase tracking-wider">
          Price
        </th>
        <th scope="col" class="px-4 py-3 text-middle text-xs font-medium text-gray-500 uppercase tracking-wider">
          Quantity
        </th>
        <th scope="col" class="px-4 py-3 text-middle text-xs font-medium text-gray-500 uppercase tracking-wider">
          Actions
        </th>
      </tr>
    </template>

    <!-- Table Body -->
    <template #table-body>
      <tr v-for="item in filteredItems" :key="item.id" class="even:bg-gray-50">
        <td class="px-4 py-4 whitespace-nowrap">
          <div>
            <div class="text-sm font-medium text-gray-900">
              <NuxtLink 
                :to="`/reports/product/${item.id}`"
                class="text-green-600 hover:text-green-500"
              >
                {{ item.name }}
              </NuxtLink>
            </div>
            <div class="text-sm text-gray-500">{{ item.description || 'No description' }}</div>
          </div>
        </td>
        <td class="px-4 py-4 whitespace-nowrap">
          <span :class="{
            'px-2 py-1 rounded-full text-xs font-medium': true,
            'bg-green-100 text-green-800': item.type === 'service',
            'bg-blue-100 text-blue-800': item.type === 'inventory_item'
          }">
            {{ formatType(item.type) }}
          </span>
        </td>
        <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ item.sku || '-' }}
        </td>
        <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 text-right">
          {{ formatCurrency(item.unit_price) }}
        </td>
        <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 text-right">
          {{ item.type === 'inventory_item' ? item.inventory_info?.quantity || 0 : '-' }}
        </td>
        <td class="px-4 py-4 whitespace-nowrap text-sm font-medium">
          <div class="relative inline-block text-left options-container">
            <button
              @click="(event) => toggleOptions(item.id, event)"
              class="text-indigo-600 hover:text-indigo-900 flex items-center"
            >
              Options
              <svg class="ml-2 -mr-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div 
              v-if="activeOptions === item.id"
              class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none z-10"
              @click.stop
            >
              <div class="py-1">
                <button
                  @click="editItem(item)"
                  class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 w-full text-left"
                >
                  <svg class="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit
                </button>
              </div>
              <div class="py-1">
                <button
                  @click="deleteItem(item.id)"
                  class="group flex items-center px-4 py-2 text-sm text-red-700 hover:bg-gray-100 hover:text-red-900 w-full text-left"
                >
                  <svg class="mr-3 h-5 w-5 text-red-400 group-hover:text-red-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </template>
  </TablePageLayout>

  <!-- Modals -->
  <Teleport to="body">
    <NewProdServModal
      v-if="showNewItemModal"
      :is-open="showNewItemModal"
      @close="closeNewItemModal"
      @create="handleCreateItem"
    />

    <EditProdServModal
      v-if="showEditItemModal"
      :is-open="showEditItemModal"
      :item="selectedItem"
      @close="closeEditItemModal"
      @update="handleUpdateItem"
    />
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRuntimeConfig } from '#app'
import TablePageLayout from '~/components/TablePageLayout.vue'
import BaseButton from '~/components/BaseButton.vue'
import NewProdServModal from '~/components/NewProdServModal.vue'
import EditProdServModal from '~/components/EditProdServModal.vue'

const config = useRuntimeConfig()
const items = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const searchQuery = ref('')
const selectedType = ref('All')
const activeOptions = ref(null)
const showNewItemModal = ref(false)
const showEditItemModal = ref(false)
const selectedItem = ref(null)

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (activeOptions.value && !event.target.closest('.options-container')) {
    activeOptions.value = null
  }
}

onMounted(() => {
  fetchItems()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Fetch items from the API
const fetchItems = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(`${config.public.apiBase}/api/ProdServ/list`)
    if (!response.ok) throw new Error('Failed to fetch items')
    const data = await response.json()
    items.value = data.products
  } catch (error) {
    console.error('Error:', error)
    errorMessage.value = 'Failed to load items. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// Filter items based on search query and type
const filteredItems = computed(() => {
  if (!items.value) return []
  
  return items.value.filter(item => {
    const matchesSearch = searchQuery.value
      ? item.name?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        item.sku?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchQuery.value.toLowerCase())
      : true

    const matchesType = selectedType.value === 'All' || item.type === selectedType.value

    return matchesSearch && matchesType
  })
})

// Format type for display
const formatType = (type) => {
  switch (type) {
    case 'service': return 'Service'
    case 'inventory_item': return 'Inventory Item'
    default: return type
  }
}

// Format currency
const formatCurrency = (value) => {
  if (!value) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

// Toggle options menu
const toggleOptions = (itemId, event) => {
  event.stopPropagation()
  activeOptions.value = activeOptions.value === itemId ? null : itemId
}

// Delete item
const deleteItem = async (itemId) => {
  if (!confirm('Are you sure you want to delete this item?')) return
  
  try {
    const response = await fetch(`${config.public.apiBase}/api/ProdServ/delete/${itemId}`, {
      method: 'DELETE'
    })
    
    if (!response.ok) throw new Error('Failed to delete item')
    
    items.value = items.value.filter(item => item.id !== itemId)
    activeOptions.value = null
  } catch (error) {
    console.error('Error:', error)
    errorMessage.value = 'Failed to delete item. Please try again.'
  }
}

// Edit item handler
const editItem = (item) => {
  selectedItem.value = item
  showEditItemModal.value = true
  activeOptions.value = null
}

// Close edit modal
const closeEditItemModal = () => {
  showEditItemModal.value = false
  selectedItem.value = null
}

// Handle update item
const handleUpdateItem = async (updatedData) => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/ProdServ/update/${updatedData.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updatedData)
    })
    
    if (!response.ok) throw new Error('Failed to update item')
    
    const updatedItem = await response.json()
    const index = items.value.findIndex(item => item.id === updatedItem.id)
    if (index !== -1) {
      items.value[index] = updatedItem
    }
    
    closeEditItemModal()
  } catch (error) {
    console.error('Error:', error)
    errorMessage.value = 'Failed to update item. Please try again.'
  }
}

// Modal handlers
const openNewItemModal = () => {
  showNewItemModal.value = true
}

const closeNewItemModal = () => {
  showNewItemModal.value = false
}

const handleCreateItem = async (itemData) => {
  try {
    const response = await fetch(`${config.public.apiBase}/api/ProdServ/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(itemData)
    })
    
    if (!response.ok) throw new Error('Failed to create item')
    
    const newItem = await response.json()
    items.value.push(newItem)
    closeNewItemModal()
  } catch (error) {
    console.error('Error:', error)
    errorMessage.value = 'Failed to create item. Please try again.'
  }
}

// Watch for changes in search query or type to refresh items
watch([searchQuery, selectedType], () => {
  fetchItems()
})
</script>