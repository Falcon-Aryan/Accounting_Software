<template>
  <div class="flex flex-col min-h-screen">
    <!-- Header Section -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-2xl font-semibold text-gray-900">{{ title }}</h1>
          <slot name="header-actions"></slot>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-hidden pb-8">
      <div class="h-[calc(100vh-13rem)] max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Error Message -->
        <div v-if="errorMessage" class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {{ errorMessage }}
        </div>
        
        <!-- Loading State -->
        <div v-if="isLoading" class="flex justify-center items-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
        
        <!-- Content -->
        <div v-else class="flex flex-col h-full bg-white shadow rounded-lg">
          <!-- Search and Filter Section -->
          <div class="relative z-10">
            <slot name="filters"></slot>
          </div>

          <!-- Table Container -->
          <div class="flex-1 overflow-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <slot name="table-header"></slot>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="!hasData" class="h-64">
                  <td :colspan="columnCount" class="px-6 py-4 text-center text-gray-500">
                    {{ emptyStateMessage }}
                  </td>
                </tr>
                <slot name="table-body"></slot>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <slot name="modals"></slot>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  errorMessage: {
    type: String,
    default: ''
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  hasData: {
    type: Boolean,
    required: true
  },
  columnCount: {
    type: Number,
    required: true
  },
  emptyStateMessage: {
    type: String,
    default: 'No data found.'
  }
})
</script>
